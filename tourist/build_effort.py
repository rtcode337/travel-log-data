#!/usr/bin/env python3
"""観光地スポットに「じっくり」(= 立ち寄るのに手間がかかる)を付ける。

## 判定の基準

**「入場して中を見る場所」= じっくり / 「外から見る・通りかかる場所」= サッと。**
お金と時間はだいたい連動する(入場するなら料金がかかり、30分以上要る)ので、この
1つの軸に畳んでいる。付けないものが「サッと」なので、CSVに増えるのは じっくり だけ。

## なぜ推定なのか

実データ(OSMの fee タグ / Wikipedia本文の料金記述)で費用が読めるのは全体の21.5%、
所要時間に至っては2.5%しかない(200件のサンプル調査で実測)。特に温泉は0%で、
「有料なのが自明すぎて誰も書かない」。だから読み取るのではなく**種別から決め打ちし、
実データがあるものだけ補強する**。

## 根拠

判定の根拠は effort_basis.csv に別ファイルで残す(spots.csv には列を足せない —
travel-log の取り込みが未知の列を例外で弾くため)。

外部APIは叩かない。すべてローカルの chiezo(jawiki / osm_japan)を引く。
"""
from __future__ import annotations

import csv
import io
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

CHIEZO = "http://localhost:9000"
HERE = Path(__file__).resolve().parent
SPOTS = HERE / "spots.csv"
BASIS = HERE / "effort_basis.csv"

HEAVY = "じっくり"
BBOX = 0.004  # 約400m四方。名寄せの候補を絞る範囲

# --- 名前のパターン(カテゴリより強い。名前に出ていれば種別はほぼ確定する) ---

# 入場して中を見る場所
NAME_HEAVY = re.compile(
    r"美術館|博物館|資料館|記念館|史料館|文学館|科学館|水族館|動物園|植物園|昆虫館|"
    r"遊園地|テーマパーク|ランド$|ワールド$|牧場|農園|果樹園|ワイナリー|酒蔵|"
    r"温泉|湯$|スパ|スキー場|ゴルフ|キャンプ場|鍾乳洞|洞窟|洞$|"
    r"天守|城$|城郭|御殿|屋敷|旧宅|生家|古民家|集落$|"
    r"劇場|ホール$|水族|プラネタリウム|ミュージアム|美術品|工房|窯$|"
    # 有料の展望施設。記事に料金が書かれないことも多いので名前で拾う(東京タワー等)
    r"タワー|スカイツリー|展望塔|"
    # 山・渓谷・湿原は歩く・登る対象で、旅程の観点では最も時間がかかる部類。
    # 「〇〇山公園」のように公園なら NAME_LIGHT が先に効いて サッと に戻る
    r"山$|岳$|峰$|連峰|高原$|渓谷$|峡$|湿原$|樹海|カルデラ"
)
# 外から見る・通りかかる場所(NAME_HEAVY より優先する)
NAME_LIGHT = re.compile(
    r"展望台|展望所|展望|灯台|大橋|橋$|橋梁|道の駅|^道の駅|駅$|駅前|"
    r"岬$|崎$|鼻$|滝$|滝壺|並木|street|通り$|商店街|"
    r"石碑|記念碑|碑$|像$|銅像|鳥居|門$|跡$|址$|趾$|古墳|貝塚|"
    r"ダム|堰|水門|港$|漁港|埠頭|桟橋|広場|噴水|時計台|公園$|公園 |緑地$"
)

# --- カテゴリの既定値 ---
CATEGORY_DEFAULT = {
    "美術館博物館": HEAVY,   # ほぼ例外なく入場して見る
    "温泉": HEAVY,           # 入浴するなら確実に時間がかかる
    "城": HEAVY,             # 天守・櫓に入る前提(城跡は NAME_LIGHT の「跡」で戻る)
    "神社仏閣": None,        # 参拝だけなら短い。拝観料があれば下で じっくり に上げる
    "街並み": None,          # 歩くだけ
    "自然": None,            # 幅が大きいので名前とOSMに委ねる
    "その他": None,          # 最大勢力。名前とOSMで振り分ける
}

# --- OSM の地物種別 ---
OSM_HEAVY = {
    "tourism=museum", "tourism=gallery", "tourism=zoo", "tourism=aquarium",
    "tourism=theme_park", "leisure=water_park", "amenity=public_bath",
    "tourism=hotel", "leisure=golf_course", "tourism=camp_site",
}
OSM_LIGHT = {
    "tourism=viewpoint", "tourism=artwork", "historic=memorial",
    "historic=monument", "man_made=lighthouse", "man_made=bridge",
    "amenity=parking", "leisure=park", "natural=peak", "natural=water",
}

# Wikipedia本文で「入場して見る場所」を裏付ける記述(補強にだけ使う)。
# **「無料」が続く場合は数えない** — 「入館料は無料である」(奥多摩湖のダム資料館)を
# 有料と読んで じっくり に上げてしまうため。語の有無だけを見ると必ずこれを踏む。
WIKI_PAID = re.compile(r"(入館料|入園料|拝観料|入場料|観覧料)")
WIKI_FREE_AFTER = re.compile(r"^.{0,8}(無料|不要|かからない)")


def get(path: str, **params) -> dict | None:
    url = f"{CHIEZO}{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=15) as res:
            return json.load(res)
    except Exception:
        return None


def osm_feature(name: str, lat: float, lng: float) -> str | None:
    """座標の近傍から名前が一致する地物を探し、その feature(key=value)を返す。"""
    got = get(
        "/v1/osm_japan/filter",
        bbox=f"{lat - BBOX},{lng - BBOX},{lat + BBOX},{lng + BBOX}",
        fields="title,feature",
        limit=60,
    )
    if not got or not got.get("results"):
        return None
    fallback = None
    for r in got["results"]:
        title = (r.get("title") or "").split(" (")[0]
        if title == name:
            return r.get("feature")
        if fallback is None and len(title) > 2 and (name in title or title in name):
            fallback = r.get("feature")
    return fallback


def wiki_is_paid(name: str) -> bool:
    """本文に料金の記述があるか。「入館料は無料」のような打ち消しは数えない。"""
    doc = get("/v1/jawiki/doc", title=name, fields="body", max_chars=20000)
    body = (doc or {}).get("body") or ""
    for m in WIKI_PAID.finditer(body):
        if not WIKI_FREE_AFTER.match(body[m.end():]):
            return True
    return False


def decide(row: dict) -> tuple[bool, str, str]:
    """(じっくりか, 根拠のルール, 根拠の中身) を返す。"""
    name = row["name"]
    cats = [c.strip() for c in row["categories"].split("|") if c.strip()]

    # 1. 種別からの推定(名前 → カテゴリ → OSM の順に強い手がかりを見る)
    verdict, rule, evidence = False, "default", "手がかり無し"
    if m := NAME_LIGHT.search(name):
        verdict, rule, evidence = False, "name_light", m.group(0)
    elif m := NAME_HEAVY.search(name):
        verdict, rule, evidence = True, "name_heavy", m.group(0)
    elif any(CATEGORY_DEFAULT.get(c) == HEAVY for c in cats):
        cat = next(c for c in cats if CATEGORY_DEFAULT.get(c) == HEAVY)
        verdict, rule, evidence = True, "category", cat
    else:
        feature = osm_feature(name, float(row["lat"]), float(row["lng"]))
        if feature in OSM_HEAVY:
            verdict, rule, evidence = True, "osm_feature", feature
        elif feature in OSM_LIGHT:
            verdict, rule, evidence = False, "osm_feature", feature

    # 2. Wikipedia に拝観料・入館料の記述があれば じっくり に**引き上げる**。
    #    推定は種別からの決め打ちだが、こちらは実データの裏付けなので最も強い。
    #    「〇〇公園」でも入園料があれば じっくり、「〇〇寺」でも拝観料があれば じっくり、
    #    と例外を救えるのがこの順序の狙い(逆順だと名前のパターンに潰される)。
    if not verdict and wiki_is_paid(name):
        return True, "wikipedia_fee", "料金の記述あり"

    return verdict, rule, evidence


def main() -> None:
    dry = "--apply" not in sys.argv
    with open(SPOTS, newline="", encoding="utf-8") as f:
        raw = f.read()
    rows = list(csv.reader(io.StringIO(raw)))
    header, body = rows[0], rows[1:]
    col = {name: i for i, name in enumerate(header)}

    basis: list[list[str]] = [["key", "effort", "rule", "evidence"]]
    heavy_count = 0
    by_rule: dict[str, int] = {}

    for r in body:
        row = {name: r[i] for name, i in col.items()}
        is_heavy, rule, evidence = decide(row)
        by_rule[rule] = by_rule.get(rule, 0) + 1
        cats = [c.strip() for c in row["categories"].split("|") if c.strip()]
        cats = [c for c in cats if c != HEAVY]  # 再実行しても重複しない
        if is_heavy:
            heavy_count += 1
            cats.append(HEAVY)
        r[col["categories"]] = "|".join(cats)
        basis.append([row["key"], HEAVY if is_heavy else "", rule, evidence])

    total = len(body)
    print(f"じっくり: {heavy_count} / {total} ({heavy_count / total:.1%})")
    print("根拠の内訳:")
    for rule, n in sorted(by_rule.items(), key=lambda kv: -kv[1]):
        print(f"  {n:6d}  {rule}")

    if dry:
        print("\n(--apply を付けると書き込む。いまは試算のみ)")
        return

    out = io.StringIO(newline="")
    csv.writer(out, lineterminator="\r\n").writerows([header, *body])
    with open(SPOTS, "w", newline="", encoding="utf-8") as f:
        f.write(out.getvalue())

    out = io.StringIO(newline="")
    csv.writer(out, lineterminator="\r\n").writerows(basis)
    with open(BASIS, "w", newline="", encoding="utf-8") as f:
        f.write(out.getvalue())
    print(f"\n書き込んだ: {SPOTS.name} / {BASIS.name}")


main()
