# travel-log-data

[travel-log](https://github.com/rtcode337/travel-log)本体には同梱しない、容量の大きいスポットの
初期データ(シード用CSV)を置くリポジトリ。travel-log本体とは独立して更新・管理する。

## フォルダ構成

`<スポットキー>/`(`spot_types.key`、例: `post_office`)フォルダの下に、そのスポット種別の
データを置く。

```
tourist/
  spots.csv
  settings.json
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
suiyou_dodesho_domestic/
  spots.csv
  settings.json
```

`tourist/`(観光地)だけは例外で、travel-log側の唯一の既定スポット種別としてアプリ初期化時に
自動で入っている必要があるため、ここに置くCSV・settings.jsonは「取り込み用の参照データ」
ではなく「travel-log本体の`db/init/tourist_spots.csv`と同内容を保持するための複製」という
位置づけになる(`settings.json`もtravel-log側では`db/init/01_schema.sql`が直接種別を
作成するため実際には使われず、現状の設定を文書化するためだけに置いてある)。編集する際は
travel-log本体の`db/init/tourist_spots.csv`にも同じ内容を反映すること。それ以外のスポット
キーは、このリポジトリのCSVがそのまま(=travel-log側に複製を持たない)取り込み対象になる。

スポットデータはCSV、スポット種別そのものの初期設定は`settings.json`で持つ。

### スポットデータ(CSV)

CSV形式はtravel-log本体の`/[type]/admin`のCSVインポート機能
(`components/AdminView.tsx`の`CSV_COLUMNS`)に合わせること。

```csv
name,name_kana,region,lat,lng,rank,category,description
```

- 必須列: `name`, `region`, `lat`, `lng`
- `region`はスポット種別の`region_scope`設定に応じた地域(既定`'jp'`=都道府県、
  国コード指定=州・県、`'world'`=国名)
- `rank`/`category`はスポット種別ごとに意味が異なってよい自由入力(空でも可)
- 取り込みはtravel-log側の管理画面(`/[type]/admin`)からこのCSVファイルを
  手動アップロードして行う(自動取り込みの仕組みは今のところ無い)

### スポット種別の設定(settings.json)

`spot_types`(key・表示名)と`spot_type_settings`(公開範囲・口コミ・Wikipediaリンクなどの
ON/OFF設定、ランク・カテゴリの一覧)をまとめて1つのスポット種別として作成するための定義ファイル。

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
- `ranks`も省略可。このスポット種別で使えるランクの一覧と、それぞれの表示スタイル
  (バッジ・地図ピン共通)を配列で指定する。配列の順序がそのままランクの並び順
  (絞り込みチップ・一覧のソート順)になる
  - `rank`: ランク値そのもの(`spots.rank`に入る自由入力の文字列)
  - `color`: 背景色(`#rrggbb`)
  - `borderColor`: 縁取り線の色。非公開スポットはこの色のまま破線になる(それ以外は
    公開スポットと同じ実線)
  - `size`: 地図ピンの大きさ(px)。バッジの大小はこれと無関係(表示側の`size`propで別管理)。
    `rank`が重要度・段階を表さない種別(放送回・企画名など)は全ランク26(観光地Aランクと同じ)に
    統一し、`rank`が重要度・段階を表す種別(観光地のA〜Eなど)だけ上位ほど大きくする
  - `label`: バッジ・ピンに表示するラベル。文字列、または`{ "image": "data:image/png;base64,..." }`
    形式の画像(base64)のどちらか
  - `textColor`: 省略可。ラベルが文字列の場合の文字色。省略時は`color`の明度から
    自動で白/濃色を選ぶ(画像ラベルの場合は無視される)
  - `ranks`自体を省略した場合(または管理画面の手入力フォームで種別を追加した場合)は、
    観光地の現行A〜E配色がそのまま既定のランク設定になる
    (travel-log側`lib/rankStyle.ts`の`DEFAULT_RANK_STYLES`参照)
- `categories`も省略可。このスポット種別で使うカテゴリの一覧(文字列配列。ランクと違い
  見た目の指定は無い)。配列の順序がそのままカテゴリの並び順(地図・スポット一覧の
  カテゴリ絞り込みチップと、スポット追加・編集フォームのサジェストの並び)になる。
  CSVの`category`列の値と一致させる(未定義の値でも動くが、並びは一覧の後ろになる)
  - `categories`自体を省略した場合(または手入力フォームで種別を追加した場合)は、
    観光地の現行カテゴリがそのまま既定になる
    (travel-log側`lib/category.ts`の`DEFAULT_CATEGORIES`参照)。
    空配列`[]`を明示すると「定義済みカテゴリなし」(既存スポットの値だけが
    絞り込み・サジェストに出る)になる
- 取り込みはtravel-log側の管理画面(`/[type]/admin`の「別のスポット種別の管理」)から
  このJSONファイルを手動アップロードして行う。スポットデータ(CSV)とは別工程で、
  先にこのJSONで種別を作成してから、CSVをその種別のページでインポートする想定
- `public_visible`が`false`(既定)で作成された種別は、CSVインポート・内容確認が終わってから
  管理画面の「スポット種別の設定」で`true`に切り替えて一般公開する

## 各データの出典

- `tourist/spots.csv`: travel-log本体の`db/init/`に元々SQLの形(都道府県別ファイル、
  7,039件)で同梱されていた観光地データを、CSVとしてtravel-log本体から複製したもの。
  Wikipedia(ja)月次ページビュー数に基づく相対順位(パーセンタイル)の機械分類で
  ランク(A〜E)を付与している(詳細はtravel-log側のREADME.md「ランクの決め方」参照)。
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
  `description`冒頭と同じ`【#9 品川】`形式(放送回番号+タイトル。合体回は`【#17-18 ...】`、
  スペシャルは`【#SP1 ...】`のような表記)。放送回番号(`9`のような数字)だけだとシリーズが
  変わると1話から数え直すため種別全体では一意にならず、番号だけをrankにすると別シリーズの
  同じ番号の回が同じ見た目・同じ絞り込み対象になってしまう。そのためrankはタイトルまで
  含めた文字列にして種別全体で一意にし、ピンに表示する短い番号は`settings.json`の`ranks`側の
  `label`(合体回は先頭の番号のみ、例: `17-18`→`17`)に分離してある。`category`列は
  `第<N>シリーズ`(1〜5)でシリーズを表す。`settings.json`の`ranks`は全340話(5シリーズ合計)を
  放送順に列挙した機械生成(見た目は全話共通、ピンには`label`の番号のみ表示)。
  **具体的なスポット名・説明文・各回との対応関係は未検証(要確認)。** シリーズごとに別々の
  調査(別セッション)で作成したものを1ファイルに統合したため、同じ場所を複数シリーズ・
  複数放送回にわたって再訪しているケースがある(例: 東京大学赤門は第1・第2・第5シリーズで
  計3回登場)。travel-log側の取り込みが`name`+`region`+`lat`+`lng`の完全一致で重複除外する
  ため、CSV側でも先に訪れた回の行だけを残し、あとの回に訪れたことは残した行の
  `description`末尾に追記する形で統合済み(重複行として残してはいない)
- `suiyou_dodesho_domestic/spots.csv`: HTB(北海道テレビ)「水曜どうでしょう」のレギュラー放送時
  (1996年〜2002年)の**国内企画のみ**を対象にした試験データ(海外企画は対象外。別キーで海外編を
  追加する想定のため、意図的に`suiyou_dodesho_domestic`という国内限定であることが分かる
  キー名にしている。travel-log側の海外対応は実装済みなので、海外編を追加する場合は
  `settings.json`の`region_scope`を`"world"`にした別フォルダを作り、`region`列に国名を入れる)。
  jawiki記事「水曜どうでしょうの企画 (日本国内)」の
  本文から、企画中に立ち寄った・通過した地点を一般知識で抽出した試験データ。観光名所に
  限らず、サイコロの目で決まっただけの経由地・宿泊地・道の駅・サービスエリア・フェリー
  乗り場なども対象に含む(HTB社屋・スタジオ収録場所、地名が特定できない曖昧な記述、
  廃業済みでosm_japanに実在データが無い場所のみ対象外)。座標のみosm_japanで裏取り済み
  (駅・IC・SA等はosm_japanに本体データが無いことが多く、その場合は駅前の実在POIなど
  代用座標を使っている行がある)。`rank`列・`category`列とも企画名
  (例: `サイコロ4〜日本列島完全制覇〜`)が入る。放送回数の情報が取れないため、
  ランク=放送回の代わりにランク=企画としており、`settings.json`の`ranks`が企画ごとに
  2文字以内の略称ラベル(例: `サ4`。地図ピン・バッジに表示される)と系列ごとの色
  (サイコロ・釣りバカ・試験に出る等は同色)を定義している。並び順はjawiki記事の
  企画の掲載順(=CSVの出現順)。
  **具体的なスポットの採否・説明文・各企画との対応関係は未検証(要確認)。** 2つのパートに
  分けた別々の調査を1ファイルに統合したため、同一スポットが複数企画に登場するケースが
  稀にある(例: 厳美渓は「桜前線捕獲大作戦」「東北2泊3日生き地獄ツアー」の両方に登場)。
  buratamoriと同様、先に登場した企画の行だけを残し、あとの企画に登場したことは
  `description`末尾に追記して統合済み

## 将来構想(未実装)

`settings.json`の`ranks`は色・縁取り線の色・地図ピンの大きさ・ラベル(文字列/画像)のみに
対応している。ランクの並び順以外のさらに複雑な表示条件(ズームレベルに応じた見た目の変化など)
が必要になった場合の形式は、現時点では未設計・未実装。
