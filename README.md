# travel-log-data

[travel-log](https://github.com/rtcode337/travel-log)本体には同梱しない、容量の大きいスポットの
初期データ(シード用CSV)を置くリポジトリ。travel-log本体とは独立して更新・管理する。

## フォルダ構成

`<スポットキー>/`(`spot_types.key`、例: `post_office`)フォルダの下に、そのスポット種別の
データを置く。

```
post_office/
  post_offices.csv
  settings.json
goshuin/
  goshuin_ranked.csv
  goshuin_unranked_z.csv
  settings.json
buratamori/
  spots.csv
  settings.json
suiyou_dodesho/
  spots.csv
  settings.json
```

スポットデータはCSV、スポット種別そのものの初期設定は`settings.json`で持つ。

### スポットデータ(CSV)

CSV形式はtravel-log本体の`/[type]/admin`のCSVインポート機能
(`components/AdminView.tsx`の`CSV_COLUMNS`)に合わせること。

```csv
name,name_kana,prefecture,municipality,lat,lng,rank,category,description,official_url
```

- 必須列: `name`, `prefecture`, `lat`, `lng`
- `rank`/`category`はスポット種別ごとに意味が異なってよい自由入力(空でも可)
- 取り込みはtravel-log側の管理画面(`/[type]/admin`)からこのCSVファイルを
  手動アップロードして行う(自動取り込みの仕組みは今のところ無い)

### スポット種別の設定(settings.json)

`spot_types`(key・表示名)と`spot_type_settings`(公開範囲・口コミ・Wikipediaリンクなどの
ON/OFF設定)をまとめて1つのスポット種別として作成するための定義ファイル。

```json
{
  "key": "post_office",
  "label": "郵便局",
  "settings": {
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

- `key`/`label`は必須。`settings`は省略可(省略したキーは既定値のまま — 既定値は
  travel-log側の`lib/types.ts`の`SPOT_TYPE_SETTING_DEFAULTS`参照。現時点では
  `public_visible`が既定`false`、`reviews_enabled`/`wikipedia_enabled`が既定`true`)。
  種別追加時は基本的に非公開(`public_visible`既定false)で始める運用のため、
  `public_visible`は明示せず省略するのが基本(明示するのは既定と異なる値にしたい
  設定のみでよい。上の例も既定と同じ`public_visible`は書いていない)
- `ranks`も省略可。このスポット種別で使えるランクの一覧と、それぞれの表示スタイル
  (バッジ・地図ピン共通)を配列で指定する。配列の順序がそのままランクの並び順
  (絞り込みチップ・一覧のソート順)になる
  - `rank`: ランク値そのもの(`spots.rank`に入る自由入力の文字列)
  - `color`: 背景色(`#rrggbb`)
  - `borderColor`: 縁取り線の色。非公開スポットはこの色のまま破線になる(それ以外は
    公開スポットと同じ実線)
  - `size`: 地図ピンの大きさ(px)。バッジの大小はこれと無関係(表示側の`size`propで別管理)
  - `label`: バッジ・ピンに表示するラベル。文字列、または`{ "image": "data:image/png;base64,..." }`
    形式の画像(base64)のどちらか
  - `textColor`: 省略可。ラベルが文字列の場合の文字色。省略時は`color`の明度から
    自動で白/濃色を選ぶ(画像ラベルの場合は無視される)
  - `ranks`自体を省略した場合(または管理画面の手入力フォームで種別を追加した場合)は、
    観光地の現行A〜E配色がそのまま既定のランク設定になる
    (travel-log側`lib/rankStyle.ts`の`DEFAULT_RANK_STYLES`参照)
- 取り込みはtravel-log側の管理画面(`/[type]/admin`の「別のスポット種別の管理」)から
  このJSONファイルを手動アップロードして行う。スポットデータ(CSV)とは別工程で、
  先にこのJSONで種別を作成してから、CSVをその種別のページでインポートする想定
- `public_visible`が`false`(既定)で作成された種別は、CSVインポート・内容確認が終わってから
  管理画面の「スポット種別の設定」で`true`に切り替えて一般公開する

## 各データの出典

- `post_office/post_offices.csv`: 国土交通省 国土数値情報(郵便局データ P30、平成25年度版)。
  行政区域コードを都道府県名・市区町村名に変換、郵便局分類コードを`category`列に変換した加工版。
  非商用利用限定のデータセットである点に注意(travel-log側のCLAUDE.md「外部データソースを
  扱う際の注意」も参照)。
- `goshuin/goshuin_ranked.csv`: OSM Overpass(`amenity=place_of_worship`、`religion=shinto`/`buddhist`)で
  wikipedia/wikidataタグ付きの寺社を全国一括取得し、Wikipedia記事が存在するものに絞り込んだ上で、
  直近60日ページビュー数の相対順位でランク(A〜E)を機械区分したもの。座標・名称・説明文はOSM/
  Wikipedia由来。都道府県は座標と国土数値情報の都道府県境ポリゴンとの空間検索による機械判定の近似値
- `goshuin/goshuin_unranked_z.csv`: 上記で対象にしたWikipedia記事付きタグ以外の、名前ありでOSMに
  採録されている寺社をそのまま採録し、機械的に全件ランク`Z`(未整理)としたもの。名前が無い/座標が
  取れない要素、`goshuin_ranked.csv`と100m以内で近接するものは除外済み
- `buratamori/spots.csv`: NHK「ブラタモリ」レギュラー版全5シリーズ(第1シリーズ2009年〜
  第5シリーズ放送中)について、放送回ごとの訪問地(都道府県・市区町村)はjawikiの番組公式記事
  「放送日程」節を参照した上で、具体的な立ち寄りスポット名・そのスポットの回内での役割の
  説明文は一般知識から作成した試験データ。座標のみosm_japanで裏取り済み。アンコール放送・
  完全版・過去回の再構成スペシャルなど新しいロケ地情報が無い回は対象外。`rank`列は
  `第<N>シリーズ`(1〜5)でシリーズを表す。
  **具体的なスポット名・説明文・各回との対応関係は未検証(要確認)。** シリーズごとに別々の
  調査(別セッション)で作成したものを1ファイルに統合したため、同じスポットが複数シリーズ・
  複数放送回にまたがって重複登録されている場合がある(番組が同じ場所を再訪した回も含むため。
  例: 東京大学赤門は第1・第2・第5シリーズで計3回登場)。travel-log側の取り込みは
  `name`+`prefecture`+`lat`+`lng`の完全一致で重複除外されるため実害は無いが、
  2回目以降の登場回の`category`(放送回情報)は取り込まれない点に留意
- `suiyou_dodesho/spots.csv`: HTB(北海道テレビ)「水曜どうでしょう」のレギュラー放送時
  (1996年〜2002年)の国内企画について、jawiki記事「水曜どうでしょうの企画 (日本国内)」の
  本文から、企画中に立ち寄った・通過した地点を一般知識で抽出した試験データ。観光名所に
  限らず、サイコロの目で決まっただけの経由地・宿泊地・道の駅・サービスエリア・フェリー
  乗り場なども対象に含む(HTB社屋・スタジオ収録場所、地名が特定できない曖昧な記述、
  廃業済みでosm_japanに実在データが無い場所のみ対象外)。座標のみosm_japanで裏取り済み
  (駅・IC・SA等はosm_japanに本体データが無いことが多く、その場合は駅前の実在POIなど
  代用座標を使っている行がある)。`rank`列は`水曜どうでしょう`固定、`category`列に企画名
  (例: `サイコロ4〜日本列島完全制覇〜`)。
  **具体的なスポットの採否・説明文・各企画との対応関係は未検証(要確認)。** 2つのパートに
  分けた別々の調査を1ファイルに統合したため、稀に同一スポットが重複登録されている場合がある
  (例: 厳美渓が「桜前線捕獲大作戦」「東北2泊3日生き地獄ツアー」の両方に登場)

## 将来構想(未実装)

`settings.json`の`ranks`は色・縁取り線の色・地図ピンの大きさ・ラベル(文字列/画像)のみに
対応している。ランクの並び順以外のさらに複雑な表示条件(ズームレベルに応じた見た目の変化など)
が必要になった場合の形式は、現時点では未設計・未実装。
