#!/usr/bin/env python3
"""travel-log-data のデータ整合性を検査する。

travel-log 本体は raw.githubusercontent.com からこのリポジトリの main を直接読むため、
壊れた CSV が main に入った時点で取り込みが壊れる。目視では気づけず取り込み時に
初めて分かる種類の壊れ方(列名の綴り違い・改行コード・key の重複・ルートの参照切れ)を
push / PR で止めるのがこのスクリプトの役目。

    python3 .github/scripts/validate_data.py

標準ライブラリのみで動く(依存を増やすとデータリポジトリに requirements が必要になる)。
検査の基準は travel-log 側の components/AdminView.tsx(CSV_COLUMNS / ROUTE_CSV_COLUMNS /
必須列)と lib/types.ts(PREFECTURES)に合わせてある。
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# travel-log 側 components/AdminView.tsx の CSV_COLUMNS / ROUTE_CSV_COLUMNS。
# 未対応の列があると本体の取り込みが例外で弾く(列名の綴り違いを黙って無視しないため)
SPOT_COLUMNS = {
    "key", "name", "name_kana", "lat", "lng",
    "region", "series", "categories", "description",
}
SPOT_REQUIRED = ("name", "lat", "lng", "region")
ROUTE_COLUMNS = {"route", "series", "seq", "spot_key", "description", "leg_description"}
ROUTE_REQUIRED = ("route", "seq", "spot_key")

# travel-log 側 lib/types.ts の PREFECTURES(JIS X 0401順)
PREFECTURES = {
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
    "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
    "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
    "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県",
}

# region_scope='jp' のスポットが収まるべき範囲(与那国島〜択捉島を含む緩めの箱)。
# 緯度経度の取り違え・符号の反転・度分秒の混入といった桁違いの誤りを拾うためのもので、
# 県境をまたぐ程度のずれは検出しない
JP_BBOX = (20.0, 122.0, 46.5, 154.0)

COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
# travel-log 側の lib/categoryStyle.ts の PIN_SHAPES と同じ集合にする
# (増やしたら両方直す。あちらは pinIcon.ts の描画にも分岐が要る)
SHAPES = {"circle", "rounded-square", "diamond", "pentagon", "hexagon", "castle"}
# 自前の形(category_styles の path)。travel-log 側 lib/categoryStyle.ts の
# PATH_D_RE と同じ考え方で、Mで始まりパスに使える字だけでできていることを見る
PATH_D_RE = re.compile(r"^[Mm][\s0-9.,+\-eE]*[MmLlHhVvCcSsQqTtAaZz][A-Za-z0-9.,+\-eE\s]*$")
REGION_SCOPES_RE = re.compile(r"^(jp|world|[a-z]{2})$")

errors: list[str] = []


def error(where: Path | str, message: str) -> None:
    errors.append(f"{where}: {message}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_crlf(path: Path) -> None:
    """CSV は CRLF 固定(travel-log 側のエクスポート lib/csv.ts の出力に合わせる)。

    かつて `\\r\\r\\n` になっていた事故があり、行末に見えない CR が残ると最終列の値に
    紛れ込む。.gitattributes で `*.csv -text` にしてあるので git は直してくれない。
    """
    raw = path.read_bytes()
    if not raw:
        error(path, "空のファイル")
        return
    without_crlf = raw.replace(b"\r\n", b"")
    if b"\r" in without_crlf:
        error(path, "CRLF 以外の位置に CR がある(\\r\\r\\n などの壊れた改行)")
    if b"\n" in without_crlf:
        error(path, "LF だけの行がある(CSV は CRLF で統一する)")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    rows = list(csv.reader(io.StringIO(read_text(path))))
    if not rows:
        error(path, "空のファイル")
        return [], []
    header = rows[0]
    records = []
    for line_no, row in enumerate(rows[1:], start=2):
        if len(row) != len(header):
            error(path, f"{line_no}行目: 列数がヘッダーと違う({len(row)} != {len(header)})")
            continue
        records.append(dict(zip(header, row)))
    return header, records


def check_header(path: Path, header: list[str], allowed: set[str], required: tuple[str, ...]) -> bool:
    unknown = [c for c in header if c not in allowed]
    if unknown:
        error(path, f"未対応の列がある: {', '.join(unknown)}(使えるのは {', '.join(sorted(allowed))})")
    missing = [c for c in required if c not in header]
    if missing:
        error(path, f"必須の列が無い: {', '.join(missing)}")
    dup = [c for c in header if header.count(c) > 1]
    if dup:
        error(path, f"列名が重複している: {', '.join(sorted(set(dup)))}")
    return not missing


def check_spots(path: Path, scope: str) -> set[str]:
    """spots.csv を検査し、key の集合を返す(routes.csv の参照確認に使う)。"""
    check_crlf(path)
    header, records = read_csv(path)
    if not check_header(path, header, SPOT_COLUMNS, SPOT_REQUIRED):
        return set()
    if "key" not in header:
        # travel-log 側の取り込みでは省略可だが、このリポジトリでは routes.csv の参照と
        # 再取り込み時の同一判定に使うため必須
        error(path, "key 列が無い(このリポジトリでは必須)")

    keys: set[str] = set()
    for line_no, row in enumerate(records, start=2):
        for column in SPOT_REQUIRED:
            if not row.get(column, "").strip():
                error(path, f"{line_no}行目: {column} が空")
        key = row.get("key", "").strip()
        if not key:
            error(path, f"{line_no}行目: key が空")
        elif key in keys:
            error(path, f"{line_no}行目: key が重複している: {key}")
        else:
            keys.add(key)

        try:
            lat, lng = float(row["lat"]), float(row["lng"])
        except (KeyError, ValueError):
            error(path, f"{line_no}行目: lat/lng が数値でない({row.get('lat')}, {row.get('lng')})")
            continue
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            error(path, f"{line_no}行目: lat/lng が範囲外({lat}, {lng})")
        elif scope == "jp":
            min_lat, min_lng, max_lat, max_lng = JP_BBOX
            if not (min_lat <= lat <= max_lat and min_lng <= lng <= max_lng):
                error(path, f"{line_no}行目: 日本の範囲外の座標({lat}, {lng})")
            region = row.get("region", "").strip()
            if region and region not in PREFECTURES:
                error(path, f"{line_no}行目: region が都道府県名でない: {region}")
    return keys


def check_routes(path: Path, spot_keys: set[str]) -> None:
    check_crlf(path)
    header, records = read_csv(path)
    if not check_header(path, header, ROUTE_COLUMNS, ROUTE_REQUIRED):
        return

    seen: set[tuple[str, int]] = set()
    for line_no, row in enumerate(records, start=2):
        route = row.get("route", "").strip()
        if not route:
            error(path, f"{line_no}行目: route が空")
        spot_key = row.get("spot_key", "").strip()
        if not spot_key:
            error(path, f"{line_no}行目: spot_key が空")
        elif spot_keys and spot_key not in spot_keys:
            error(path, f"{line_no}行目: spot_key が spots.csv に無い: {spot_key}")
        try:
            seq = int(row["seq"])
        except (KeyError, ValueError):
            error(path, f"{line_no}行目: seq が整数でない: {row.get('seq')}")
            continue
        if (route, seq) in seen:
            error(path, f"{line_no}行目: 同じルート内で seq が重複している: {route} / {seq}")
        seen.add((route, seq))


def check_settings(path: Path, folder: str, catalog_label: str | None) -> str:
    """settings.json を検査し、region_scope を返す。"""
    try:
        settings = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        error(path, f"JSON として読めない: {exc}")
        return "jp"

    if settings.get("key") != folder:
        error(path, f"key がフォルダ名と違う: {settings.get('key')!r} != {folder!r}")
    label = settings.get("label")
    if not label:
        error(path, "label が無い")
    elif catalog_label is not None and label != catalog_label:
        error(path, f"label が catalog.json と違う: {label!r} != {catalog_label!r}")

    scope = (settings.get("settings") or {}).get("region_scope", "jp")
    if not isinstance(scope, str) or not REGION_SCOPES_RE.match(scope):
        error(path, f"region_scope が不正: {scope!r}(jp / world / 国コード2文字)")
        scope = "jp"

    series_values: set[str] = set()
    for entry in settings.get("series") or []:
        name = entry.get("series")
        if not name:
            error(path, f"series に series が無い項目がある: {entry}")
            continue
        if name in series_values:
            error(path, f"series が重複している: {name}")
        series_values.add(name)
        for key in ("color", "borderColor", "textColor"):
            value = entry.get(key)
            if value is not None and not COLOR_RE.match(str(value)):
                error(path, f"series {name!r} の {key} が #rrggbb 形式でない: {value!r}")

    for entry in settings.get("category_styles") or []:
        # path(自前の形。100×145の箱に描いたSVGのパス)があればそちらが優先で、
        # shape は省略できる。パスは canvas で描くだけなので危険は無いが、
        # 打ち間違いを黙って空のピンにしないよう字面だけ検査する
        custom = entry.get("path")
        if custom is not None:
            if not isinstance(custom, str) or not PATH_D_RE.match(custom):
                error(path, f"category_styles の path が SVG のパスとして不正: {custom!r}")
        else:
            shape = entry.get("shape")
            if shape not in SHAPES:
                error(path, f"category_styles の shape が不正: {shape!r}(使えるのは {', '.join(sorted(SHAPES))})")
        category = entry.get("category")
        categories = settings.get("categories")
        if categories is not None and category not in categories:
            error(path, f"category_styles の category が categories に無い: {category!r}")

    return scope


def check_exclude(path: Path, spot_keys: set[str]) -> None:
    """exclude.txt は travel-log 側から消すキーの一覧なので、spots.csv に残っていてはいけない。"""
    for line_no, line in enumerate(read_text(path).splitlines(), start=1):
        key = line.strip()
        if not key or key.startswith("#"):
            continue
        if key in spot_keys:
            error(path, f"{line_no}行目: spots.csv に残っているキーが除外一覧にある: {key}")


def main() -> int:
    catalog_path = ROOT / "catalog.json"
    try:
        catalog = json.loads(read_text(catalog_path))
    except (OSError, json.JSONDecodeError) as exc:
        error(catalog_path, f"読めない: {exc}")
        print("\n".join(errors), file=sys.stderr)
        return 1

    labels: dict[str, str] = {}
    for entry in catalog.get("spot_types") or []:
        key, label = entry.get("key"), entry.get("label")
        if not key or not label:
            error(catalog_path, f"key / label が揃っていない項目がある: {entry}")
            continue
        if key in labels:
            error(catalog_path, f"key が重複している: {key}")
        labels[key] = label

    folders = sorted(
        p.name for p in ROOT.iterdir()
        if p.is_dir() and not p.name.startswith(".") and (p / "spots.csv").exists()
    )
    for name in folders:
        if name not in labels:
            error(catalog_path, f"spots.csv があるのに catalog.json に無いスポット種別: {name}")
    for key in labels:
        if key not in folders:
            error(catalog_path, f"catalog.json にあるのに spots.csv が無いスポット種別: {key}")

    for name in folders:
        folder = ROOT / name
        settings_path = folder / "settings.json"
        scope = "jp"
        if settings_path.exists():
            scope = check_settings(settings_path, name, labels.get(name))
        else:
            error(folder, "settings.json が無い")

        # 種別ごとの出典・生成手順・ライセンスはこのREADMEが正(ルートREADMEは汎用のみ)
        if not (folder / "README.md").exists():
            error(folder, "README.md が無い(出典・生成手順・ライセンスを書く)")

        spot_keys = check_spots(folder / "spots.csv", scope)

        routes_path = folder / "routes.csv"
        if routes_path.exists():
            check_routes(routes_path, spot_keys)

        exclude_path = folder / "excluded_candidates" / "exclude.txt"
        if exclude_path.exists():
            check_exclude(exclude_path, spot_keys)

        # 補助 CSV(観光地の effort_basis.csv など)。列は種別ごとに自由だが、
        # 改行コードと key 列の参照だけは spots.csv と揃っている必要がある
        for extra in sorted(folder.glob("*.csv")):
            if extra.name in ("spots.csv", "routes.csv"):
                continue
            check_crlf(extra)
            header, records = read_csv(extra)
            if "key" in header and spot_keys:
                unknown = {r["key"] for r in records if r.get("key") and r["key"] not in spot_keys}
                if unknown:
                    sample = ", ".join(sorted(unknown)[:5])
                    error(extra, f"spots.csv に無い key がある({len(unknown)}件): {sample}")

    if errors:
        print(f"NG: {len(errors)}件", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(f"OK: スポット種別 {len(folders)}件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
