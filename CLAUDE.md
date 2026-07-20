# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 回答言語

ユーザーとの会話・説明・コミットメッセージ等は常に日本語で行うこと。

## このリポジトリの役割

[travel-log](https://github.com/rtcode337/travel-log)本体には同梱しない、容量の大きいスポットの
初期データ(CSV)とスポット種別の設定(settings.json)を置くリポジトリ。travel-log側のソース
コードを一切参照しなくても、このファイルだけを見て新しいスポット種別のCSV・settings.jsonを
生成できるよう、必要なスキーマ・既定値をすべてここに書き出してある(travel-log側の実装は
`lib/types.ts`・`lib/rankStyle.ts`・`components/AdminView.tsx`だが、参照必須ではない)。

## フォルダ構成

`<スポットキー>/`(機械可読な英数字+アンダースコア。例: `post_office`)フォルダの下に、
そのスポット種別のCSV(スポットデータ、複数ファイルに分けてもよい)と`settings.json`
(スポット種別そのものの設定、省略可)を置く。

```
<スポットキー>/
  <任意のファイル名>.csv   # 1つでも複数に分けてもよい
  settings.json            # 省略可(省略時は全項目が既定値の種別になる)
```

## CSV形式(スポットデータ)

1行目はヘッダー行必須。列順は自由。

```csv
name,name_kana,prefecture,municipality,lat,lng,rank,category,description,official_url
厳島神社,いつくしまじんじゃ,広島県,廿日市市,34.2959,132.3197,A,神社仏閣,海に浮かぶ大鳥居,https://example.com
```

| 列 | 必須 | 説明 |
|---|---|---|
| `name` | ○ | スポット名 |
| `name_kana` | | ふりがな(五十音ソート用) |
| `prefecture` | ○ | 都道府県 |
| `municipality` | | 市区町村(空でも可) |
| `lat` / `lng` | ○ | 緯度・経度(数値) |
| `rank` | | 自由入力のランク文字列。`settings.json`の`ranks`で定義した`rank`値と一致させる(未定義の値でも動くが見た目は簡易フォールバックになる) |
| `category` | | 自由入力カテゴリ(空でも可) |
| `description` | | 説明文 |
| `official_url` | | 公式サイトURL |

取り込みはtravel-log側の管理画面(`/[type]/admin`)からの手動アップロード(自動取り込みの
仕組みは無い)。差分更新のため、既存行との重複判定は`name`+`prefecture`+`lat`+`lng`の
完全一致で行われる(`municipality`は使わない)。同じCSVを何度アップロードしても
重複登録されない。

## settings.json形式(スポット種別の設定)

```json
{
  "key": "post_office",
  "label": "郵便局",
  "settings": {
    "public_visible": false,
    "reviews_enabled": false,
    "wikipedia_enabled": false
  },
  "ranks": [
    {
      "rank": "郵便局",
      "color": "#dc2626",
      "borderColor": "#b91c1c",
      "size": 22,
      "label": "〒",
      "textColor": "#ffffff"
    }
  ]
}
```

- `key`: 必須。機械可読キー(英数字+アンダースコア、既存の`spot_types.key`と重複不可)
- `label`: 必須。表示名(自由な文字列)
- `settings`: 省略可。省略したキー・オブジェクト自体の省略は下表の既定値になる
  (既定値と同じ値をわざわざ書く必要はない — 差分だけ書けばよい)
- `ranks`: 省略可。省略時は後述の既定ランク(A〜E)になる

### settingsの既定値(キーごとに省略可)

| キー | 既定値 | 意味 |
|---|---|---|
| `public_visible` | `false` | `true`で一般公開(全ユーザーに`/[key]/map`等を表示)。`false`はadmin/spot_admin限定(準備中の種別向け) |
| `reviews_enabled` | `true` | `false`でこの種別の口コミ機能(表示・投稿)を無効化 |
| `wikipedia_enabled` | `true` | `false`でスポット詳細のWikipediaリンクを非表示にする(大半のスポットにWikipedia記事が存在しない種別向け) |

上記3キー以外の設定が将来travel-log側に追加される可能性がある。値はすべて`true`/`false`の
booleanのみ(現時点で文字列や数値の設定キーは無い。例外は次項の`rank_styles`だが、これは
`ranks`フィールド経由で扱うため直接書く必要はない)。

### ranksの形式(配列。省略時は既定のA〜E)

各要素:

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `rank` | string | ○ | ランク値そのもの(CSVの`rank`列と一致させる) |
| `color` | string(`#rrggbb`) | ○ | 背景色(バッジ・地図ピン共通) |
| `borderColor` | string(`#rrggbb`) | ○ | 縁取り線の色。非公開スポット(status=`private`)はこの色のまま破線になるだけで、それ以外(色・大きさ・ラベル)は公開スポットと同じ見た目になる |
| `size` | number | ○ | 地図ピンの直径(px)。バッジ自体の大小には影響しない(表示側が別途管理) |
| `label` | string または `{ "image": "data:image/png;base64,..." }` | ○ | バッジ・ピンに表示するラベル。文字列、またはbase64画像のどちらか |
| `textColor` | string(`#rrggbb`) | 省略可 | ラベルが文字列の場合の文字色。省略時は`color`の明度から自動選択(明るい背景→濃色、暗い背景→白。画像ラベルの場合はそもそも使われない) |

配列の順序がそのままランクの並び順(絞り込みチップの並び・一覧のソート順)になる。

### ranksを省略した場合の既定値(観光地=touristの現行配色。手入力で種別を追加した場合も同じ)

```json
[
  { "rank": "A", "color": "#f59e0b", "borderColor": "#b45309", "size": 26, "label": "A", "textColor": "#451a03" },
  { "rank": "B", "color": "#a7f3d0", "borderColor": "#34d399", "size": 22, "label": "B", "textColor": "#065f46" },
  { "rank": "C", "color": "#93c5fd", "borderColor": "#60a5fa", "size": 18, "label": "C", "textColor": "#1e3a8a" },
  { "rank": "D", "color": "#fef3c7", "borderColor": "#fbbf24", "size": 15, "label": "D", "textColor": "#78350f" },
  { "rank": "E", "color": "#e5e7eb", "borderColor": "#9ca3af", "size": 12, "label": "E", "textColor": "#374151" }
]
```

必要なランクがこれと異なる(独自のランク基準・段階数を使う)種別では、`ranks`に
配列をまるごと指定して上書きする(既定の一部だけを引き継ぐことはできない — `ranks`を
書く場合はそのスポット種別で使う全ランクを列挙すること)。

### 取り込み方法

travel-log側の管理画面の「別のスポット種別の管理」からこのJSONファイルを手動アップロードして
種別を作成する。スポットデータ(CSV)とは別工程で、先にこのJSONで種別(と設定・ランク)を
作成してから、CSVをその種別のページでインポートする。`public_visible`が`false`(既定)で
作成した種別は、CSVインポート・内容確認が終わってから管理画面の「スポット種別の設定」で
`true`に切り替えて一般公開する。

## 外部データソース(Wikipedia、OSM Overpass/Nominatim、政府オープンデータ等)を扱う際の注意

- 自分でレート制限をかけ、リクエストには識別可能な`User-Agent`(名前+連絡先)を設定すること
  — Overpass API・Nominatimはこのプロジェクト専有のインフラではなく、無料でコミュニティ運営
  されているフェアユース前提のサービス
- レンダリング済みHTMLのスクレイピングより、公式API(MediaWiki REST/Action API、Overpass QL)
  を優先すること
- 政府や第三者のオープンデータには、travel-logのライセンスと整合しない利用制限(非商用限定など)
  が付いていることが多い。そうしたデータセットの中身(名称・座標・説明文)をそのままCSVに
  転記しないこと。せいぜい「抜けているスポットに気づくためのヒント」として使い、実際のデータ
  (座標・説明文)はライセンス面で問題のない別ソースから取り直すこと
- 一括でスポットを追加した後は、コミット前に既存行との重複(名前一致・近接座標)がないか
  確認すること

## コミット前に

コードやデータファイルに変更を加えたら、その変更でREADME.md・CLAUDE.mdの記述
(フォルダ構成、CSV/settings.jsonのスキーマ、データ件数、データの出典など)が古くならないか
確認し、必要なら同じコミットで更新すること。特にデータ件数・フォルダ構成・スキーマ(既定値を
含む)は変更が入りやすく、記述が古いまま放置されがち。
