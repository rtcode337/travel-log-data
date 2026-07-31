# travel-log-data

[travel-log](https://github.com/rtcode337/travel-log)本体には同梱しない、容量の大きいスポットの
初期データ(シード用CSV)を置くリポジトリ。travel-log本体とは独立して更新・管理する。

> **このリポジトリ全体に適用される単一のライセンスはありません。** フォルダ(スポットキー)
> ごとに由来元のライセンス・利用制限が異なるため、リポジトリ直下に`LICENSE`は置いていません。
> 再配布・二次利用の際は、下の「収録データ」の表と各フォルダのREADMEを確認してください。

## 収録データ

スポット種別ごとの詳細(出典・生成手順・収録の基準・ライセンス)は各フォルダのREADMEが正。

| スポット種別 | 件数 | 主な出典 | ライセンス・制限 |
|---|---|---|---|
| [tourist](tourist/README.md)(観光地) | 10,708 | Wikipedia(ja)・Wikidata | CC BY-SA 4.0 / CC0 |
| [goshuin](goshuin/README.md)(御朱印) | 51,950 | OpenStreetMap・Wikipedia(ja) | ODbL / CC BY-SA 4.0 |
| [post_office](post_office/README.md)(郵便局) | 24,526 | 国土数値情報(郵便局データ P30) | **非商用利用限定** |
| [restaurant](restaurant/README.md)(飲食店) | 171 | Wikipedia(ja)・OpenStreetMap | ODbL / CC BY-SA 4.0 |
| [buratamori](buratamori/README.md)(ブラタモリ) | 406 | jawiki記事 + LLMの記憶(**未検証**) | — |
| [suiyou_dodesho_domestic](suiyou_dodesho_domestic/README.md)(水曜どうでしょう・国内編) | 279 | jawiki記事 + LLMの記憶(**未検証**) | — |
| [suiyou_dodesho_overseas](suiyou_dodesho_overseas/README.md)(水曜どうでしょう・海外編) | 136 | jawiki記事 + LLMの記憶(**未検証**) | ODbL(座標) |

## フォルダ構成

`<スポットキー>/`(`spot_types.key`、例: `post_office`)フォルダの下に、そのスポット種別の
データを置く。

```
catalog.json                 # スポット種別の一覧(key・label)
.github/
  workflows/validate.yml     # push・PRでデータを検証する(下記「データの検証」)
  scripts/validate_data.py   # 検証の実体。手元でも同じものを実行できる
<スポットキー>/
  README.md                  # この種別の出典・生成手順・収録の基準・ライセンス
  spots.csv                  # スポットデータ
  routes.csv                 # 省略可(スポットを巡った順に矢印で繋ぐルート)
  settings.json              # スポット種別そのものの初期設定
  excluded_candidates/       # 省略可(除外した候補の記録)
    exclude.txt              # travel-log側から削除するスポットのkey一覧(追記式)
```

リポジトリ直下の`catalog.json`は`{ "spot_types": [ { "key": "...", "label": "..." }, ... ] }`形式の
スポット種別カタログで、travel-log側の管理画面「GitHubリポジトリからスポット種別取り込み」が種別の一覧表示に
使う(選んだ種別の`settings.json`・`spots.csv`・`excluded_candidates/exclude.txt`・`routes.csv`が
一括適用される)。**スポットキーのフォルダを追加・改名したら`catalog.json`にも反映すること**。

### スポットデータ(CSV)

CSV形式はtravel-log本体の`/[type]/admin`のCSVインポート機能
(`components/AdminView.tsx`の`CSV_COLUMNS`)に合わせること。

```csv
name,name_kana,lat,lng,region,series,categories,description,key
```

- 必須列: `name`, `lat`, `lng`, `region`, `key`(`key`はこのリポジトリの運用上の必須。
  travel-log側のCSV取り込みでは省略可)
- `region`はスポット種別の`region_scope`設定に応じた地域(既定`'jp'`=都道府県、
  国コード指定=州・県、`'world'`=国名)
- `series`/`categories`はスポット種別ごとに意味が異なってよい自由入力(空でも可)
- `key`は省略可の種別内一意な参照キーで、`routes.csv`がスポットを指すのに使う
  (ルートを持たない種別では列ごと省略してよい)。一度割り当てたら変更しない
- 取り込みはtravel-log側の管理画面(`/[type]/admin`)からこのCSVファイルを
  手動アップロードして行う(自動取り込みの仕組みは今のところ無い)

### ルートデータ(routes.csv)

スポットを巡った順に矢印で繋ぐルートの定義(列:
`route,series,seq,spot_key,description,leg_description`)。
取り込むとtravel-log側の地図に、経由地を`seq`昇順に繋いだラインと進行方向の矢印が描かれる。
`series`列に`settings.json`の`series`のシリーズ値を入れると
矢印がそのシリーズの縁取り色で描かれ、地図のシリーズ絞り込みにも連動する
(`route`はルートの表示名で、シリーズとは独立)。`description`列はルート全体の説明文で、
地図でルートの線をタップすると出るルート詳細の先頭に表示される。`leg_description`列は
その行のスポットから次のスポットへの区間の説明(移動手段など。行単位で、最終地点の行は
空欄にする)で、ルート詳細の経由地一覧で2点の間に表示される。`spot_key`は
スポットCSVの`key`列を指すため、**スポットCSV→routes.csvの順で**同じ管理画面から
取り込む。スキーマの詳細はCLAUDE.mdの「routes.csv形式」節を参照

### スポット種別の設定(settings.json)

`spot_types`(key・表示名)と`spot_type_settings`(公開範囲・口コミ・Wikipediaリンクなどの
ON/OFF設定、シリーズ・カテゴリの一覧)をまとめて1つのスポット種別として作成するための定義ファイル。

```json
{
  "key": "post_office",
  "label": "郵便局",
  "settings": {
    "reviews_enabled": false,
    "wikipedia_enabled": false
  },
  "series": [
    {
      "series": "郵便局",
      "color": "#dc2626",
      "borderColor": "#b91c1c",
      "size": 26,
      "label": "〒",
      "textColor": "#ffffff"
    }
  ]
}
```

- `key`/`label`は必須。`settings`は省略可(省略したキーは既定値のまま — 既定値は
  travel-log側の`lib/types.ts`の`SPOT_TYPE_SETTING_DEFAULTS`参照。現時点では
  `public_visible`が既定`false`、`reviews_enabled`/`wikipedia_enabled`が既定`true`、
  `region_scope`が既定`"jp"`、`wikipedia_lang`が既定`"ja"`)。
  種別追加時は基本的に非公開(`public_visible`既定false)で始める運用のため、
  `public_visible`は明示せず省略するのが基本(明示するのは既定と異なる値にしたい
  設定のみでよい。上の例も既定と同じ`public_visible`は書いていない)
- 日本以外を対象にした種別は`settings`に`region_scope`を指定する(`"jp"`=日本/
  ISO 3166-1 alpha-2の国コード小文字=その国/`"world"`=世界全体)。CSVの`region`列に
  入れる値がこれに連動する(日本=都道府県、国指定=州・県、世界=国名)ほか、
  地域タブの名称と並び順・地名検索の対象国・地図の初回表示も変わる。日本語以外の
  Wikipedia記事を引きたい場合は`wikipedia_lang`(例: `"en"`)も併せて指定する。
  詳細と海外データ作成時の注意はCLAUDE.mdの「region_scope(対象地域)と海外データ」節を参照
- `series`も省略可。このスポット種別で使えるシリーズの一覧と、それぞれの表示スタイル
  (バッジ・地図ピン共通)を配列で指定する。配列の順序がそのままシリーズの並び順
  (絞り込みチップ・一覧のソート順)になる
  - `series`: シリーズ値そのもの(`spots.series`に入る自由入力の文字列)
  - `color`: 背景色(`#rrggbb`)
  - `borderColor`: 縁取り線の色。非公開スポットはこの色のまま破線になる(それ以外は
    公開スポットと同じ実線)
  - `size`: 地図ピンの大きさ(px)。バッジの大小はこれと無関係(表示側の`size`propで別管理)。
    `series`が重要度・段階を表さない種別(放送回・企画名など)は全シリーズ26(観光地Aシリーズと同じ)に
    統一し、`series`が重要度・段階を表す種別(観光地のA〜Eなど)だけ上位ほど大きくする
  - `label`: バッジ・ピンに表示するラベル。文字列、または`{ "image": "data:image/png;base64,..." }`
    形式の画像(base64)のどちらか
  - `textColor`: 省略可。ラベルが文字列の場合の文字色。省略時は`color`の明度から
    自動で白/濃色を選ぶ(画像ラベルの場合は無視される)
  - `series`自体を省略した場合(または管理画面の手入力フォームで種別を追加した場合)は、
    観光地の現行A〜E配色がそのまま既定のシリーズ設定になる
    (travel-log側`lib/seriesStyle.ts`の`DEFAULT_SERIES_STYLES`参照)
- `categories`も省略可。このスポット種別で使うカテゴリの一覧(文字列配列。シリーズと違い
  見た目の指定は無い)。配列の順序がそのままカテゴリの並び順(地図・スポット一覧の
  カテゴリ絞り込みチップと、スポット追加・編集フォームのサジェストの並び)になる。
  CSVの`categories`列の値と一致させる(未定義の値でも動くが、並びは一覧の後ろになる)
  - `categories`自体を省略した場合(または手入力フォームで種別を追加した場合)は、
    観光地の現行カテゴリがそのまま既定になる
    (travel-log側`lib/categories.ts`の`DEFAULT_CATEGORIES`参照)。
- `category_styles`も省略可。カテゴリごとの**地図ピンの形**(`{ category, shape }`の配列。
  `shape`は`circle`(既定)か`rounded-square`)。シリーズが色・大きさ・ラベルを使っている
  ため、カテゴリに割り当てられるのは形だけ。1スポットが複数カテゴリを持つ場合は、
  この配列の順で最初に一致したものが使われる
    空配列`[]`を明示すると「定義済みカテゴリなし」(既存スポットの値だけが
    絞り込み・サジェストに出る)になる
- 取り込みはtravel-log側の管理画面(`/[type]/admin`の「別のスポット種別の管理」)から
  このJSONファイルを手動アップロードして行う。スポットデータ(CSV)とは別工程で、
  先にこのJSONで種別を作成してから、CSVをその種別のページでインポートする想定
- `public_visible`が`false`(既定)で作成された種別は、CSVインポート・内容確認が終わってから
  管理画面の「スポット種別の設定」で`true`に切り替えて一般公開する

## データの検証

```bash
python3 .github/scripts/validate_data.py
```

CSVを編集したらコミット前に実行する(標準ライブラリのみ・依存なし。push・PRでも
GitHub Actionsが同じものを回す)。travel-log側はこのリポジトリのmainを直接読むため、
壊れたCSVはそのまま取り込みの失敗になる。見ているのは列名・改行コード(CRLF)・
必須項目・座標の範囲・`key`の一意性・`routes.csv`の参照先・`settings.json`の妥当性など、
目視では気づけない種類の誤り(詳細はCLAUDE.mdの「データの検証(CI)」節)。

## ライセンスと出典表示

このリポジトリのCSVはtravel-log本体(MITライセンス)とは別物で、**由来元の利用許諾条件が
スポット種別ごとにそのまま適用される**。上の「収録データ」の表を出発点に、実際に再配布・
二次利用するデータのフォルダのREADMEを読むこと。代表的な条件は次の3つ:

- **CC BY-SA 4.0**(Wikipedia(ja)由来の説明文・座標。一部旧記事はGFDLとのデュアルライセンス):
  出典(「出典: フリー百科事典『ウィキペディア(Wikipedia)』」+該当記事名・URL)の表示と、
  改変物を同一(または互換)ライセンスで提供することが求められる
- **ODbL**(OpenStreetMap由来の座標・名称): まとまった量を再配布する場合は
  「© OpenStreetMap contributors」の表示と、データベース自体をODbL(または互換ライセンス)で
  提供することが求められる
- **非商用利用限定**(国土数値情報): CC BY-SA・ODbLとは別種の制限で、商用利用そのものが
  許諾されていない

座標をosm_japan(OSMのローカルミラー)やNominatimで1件ずつ裏取りしただけの種別
(buratamori・suiyou_dodesho_domestic)は、Overpass APIでの一括抽出(データベースからの
実質的な取り出し)ではなく既知の地点を個別に参照した程度のため、ODbLの表示義務は
適用されないと考えている(まとまった量の再配布にあたるかどうかの境界事例ではあるので、
大量に追加抽出する場合は改めて要検討)。

かつて`tourist/spots.csv`と同内容をtravel-log本体の`db/init/tourist_spots.csv`に複製し
出典表示なくコミットしていたが、このリポジトリでの管理に一本化した。

## 将来構想(未実装)

`settings.json`の`series`は色・縁取り線の色・地図ピンの大きさ・ラベル(文字列/画像)のみに
対応している。シリーズの並び順以外のさらに複雑な表示条件(ズームレベルに応じた見た目の変化など)
が必要になった場合の形式は、現時点では未設計・未実装。
