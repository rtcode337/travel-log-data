#!/usr/bin/env python3
"""ランクの点検 —— 知名度の由来が観光でないスポットを機械で洗い出す。

なぜ要るか
----------
`rank`はWikipedia(ja)の月次ページビューのパーセンタイル区分だが、**ページビューは
観光以外の関心でも伸びる**。大学は受験、企業は就活、駅は乗り換え、島は地理の調べ物 ——
どれも「観光地としての知名度」ではないのに、パーセンタイルは高く出る。

これまでは気づくたびに名前のパターン(大学・本社・株式会社・駅・空港…)を発明して
目視で洗っていた。パターンを継ぎ足す運用は、次の類型に気づくまで漏れ続ける。
**このスクリプトは、偏りの類型をWikipediaのカテゴリで定義して固定する。**

判定
----
次の3類型を候補に挙げ、2つの免除で戻す。

- **法人・組織** —— 記事の主題が学校法人・企業・鉄道事業者・放送局などの組織
- **交通インフラ** —— 駅・空港(乗り換え・時刻表の調べ物でPVが伸びる)
- **広域の地誌** —— 島・諸島(記事が島全体の地理・歴史・行政を扱い、訪問先より広い)

免除(候補から戻す):

- `観光`を含むカテゴリを持つ(例: 兼六園の「石川県の観光地」)
- 訪ねる先そのものを表すカテゴリを持つ(水族館・博物館・公園・史跡など)。
  **運営会社のカテゴリが付いた施設**を巻き込まないために要る
  (仙台うみの杜水族館は「仙台市青葉区の企業」を、震災遺構の大川小学校は
  「学校記事」を持っている)

試して駄目だった信号
--------------------
**周辺の観光施設÷生活施設の比(OSM)は使えない。** 観光地には宿と土産物屋が濃く
集まるはず、という見込みで測ったが、A・Bの21.6%(371件)が引っかかり、中身は
住吉大社0.07・太陽の塔0.06・丸亀城0.19といった本物の観光地だった。**城西大学0.02と
住吉大社0.07を分ける閾値は引けない。** 比が測っていたのは「観光地かどうか」ではなく
**「宿泊型リゾートかどうか」**で、日帰りで訪ねる都市部の寺社・城はすべて低く出る
(箱根神社11.50・白川郷7.20で当たったように見えたのは、宿が集まる土地を選んでいたため)。

**PVの単純な密度も使えない。** 都市度を測るだけで、東京国際フォーラム1,447が
白川郷49を上回る。

**このスクリプトはランクを書き換えない。候補を挙げるだけ。**
過去の目視結果71件で測って適合率97%・再現率86%だったので、
**100件下げれば3件は下げるべきでないものが混ざる**。自動適用すると、
どれがずれたか分からないまま残る。仕分けは人がやり、結果は
`<スポットキー>/excluded_candidates/series_demotions.md`に記録する。

    python3 .github/scripts/rank_audit.py [スポットキー]

カテゴリの取得元は、LAN内のchiezo(あれば)かWikipedia API。
**CIでは回さない**(外部APIに依存させないため)。
"""

from __future__ import annotations

import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CHIEZO = "http://192.168.1.3:7010/v1/jawiki/doc"
WIKIPEDIA = "https://ja.wikipedia.org/w/api.php"
UA = "travel-log-data rank audit (+https://github.com/rtcode337/travel-log-data)"

# 記事の主題が「組織」であることを示すカテゴリ
ORG = re.compile(r"(学校記事|大学|短期大学|専門学校|の企業|メーカー|鉄道事業者|バス事業者|"
                 r"テレビ局|放送局|新聞社|証券取引所|銀行|保険|商社|正会員企業|"
                 r"株式会社|グループ企業|の法人|プロデュース会社|に関係する企業)")
INFRA = re.compile(r"(の鉄道駅|の空港)")
WIDE = re.compile(r"(日本の島|諸島|列島|群島|火山島)")

# 訪ねる先そのものを表すカテゴリ。**組織のカテゴリより優先する**
PLACE = re.compile(r"(水族館|博物館|美術館|動物園|植物園|遊園地|テーマパーク|温泉|公園|城$|城郭|"
                   r"神社|寺院|遺構|史跡|名勝|展望台|タワー|庭園|観光)")

TYPES = (("法人・組織", ORG), ("交通インフラ", INFRA), ("広域の地誌（島）", WIDE))
TARGET_RANKS = "AB"  # C以下は観光実態との乖離が小さいため対象外(既存の運用に合わせる)


class Tags:
    """記事のカテゴリを引く。chiezoが見えればそちら、駄目ならWikipedia API。"""

    def __init__(self) -> None:
        self.source = "chiezo" if self._alive() else "wikipedia"
        self.cache: dict[str, list[str]] = {}

    def _alive(self) -> bool:
        try:
            urllib.request.urlopen(f"{CHIEZO}?title=%E6%97%A5%E6%9C%AC", timeout=3).read()
            return True
        except Exception:
            return False

    def _get(self, url: str) -> dict:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.load(r)

    def __call__(self, title: str) -> list[str]:
        if title in self.cache:
            return self.cache[title]
        try:
            if self.source == "chiezo":
                q = urllib.parse.urlencode({"title": title, "fields": "title,tags"})
                tags = self._get(f"{CHIEZO}?{q}").get("tags") or []
            else:
                # 相手はコミュニティ運営なので、こちらで間隔を空ける
                time.sleep(0.2)
                q = urllib.parse.urlencode({
                    "action": "query", "format": "json", "prop": "categories",
                    "cllimit": "max", "titles": title})
                pages = self._get(f"{WIKIPEDIA}?{q}")["query"]["pages"]
                tags = [c["title"].removeprefix("Category:")
                        for p in pages.values() for c in p.get("categories", [])]
        except (urllib.error.URLError, KeyError, json.JSONDecodeError):
            tags = []
        self.cache[title] = tags
        return tags


def classify(tags: list[str]) -> str | None:
    """候補にする類型を返す。免除されるか、どの類型にも当たらなければ None。"""
    if not tags:
        return None
    joined = " ".join(tags)
    if PLACE.search(joined):
        return None
    for label, pattern in TYPES:
        if pattern.search(joined):
            return label
    return None


def main() -> int:
    key = sys.argv[1] if len(sys.argv) > 1 else "tourist"
    spots = Path(key) / "spots.csv"
    if not spots.exists():
        print(f"{spots} が無い", file=sys.stderr)
        return 1

    # 既に目視で決着したものは挙げ直さない(据え置きの判断も記録に含まれるため)
    record = Path(key) / "excluded_candidates" / "series_demotions.md"
    decided = record.read_text(encoding="utf-8") if record.exists() else ""

    rows = [r for r in csv.DictReader(spots.open(encoding="utf-8"))
            if r["rank"] in TARGET_RANKS]
    tags = Tags()
    print(f"{key}: ランク {TARGET_RANKS} が {len(rows)} 件。"
          f"カテゴリを {tags.source} から引きます…", file=sys.stderr)

    found: dict[str, list[dict]] = {}
    for row in rows:
        if row["name"] in decided:
            continue
        label = classify(tags(row["name"]))
        if label:
            found.setdefault(label, []).append(row)

    total = sum(len(v) for v in found.values())
    print(f"\n未点検の候補 {total} 件（{key} のランク {TARGET_RANKS} の "
          f"{total / len(rows) * 100:.1f}%）")
    print()
    for label, items in sorted(found.items(), key=lambda x: -len(x[1])):
        print(f"## {label}（{len(items)}件）\n")
        for r in sorted(items, key=lambda r: (r["rank"], r["region"])):
            print(f"| {r['name']} | {r['rank']} | {r['region']} | {r['description'][:70]} |")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
