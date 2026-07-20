# travel-log-data

[travel-log](https://github.com/rtcode337/travel-log)本体には同梱しない、容量の大きいスポットの
初期データ(シード用CSV)を置くリポジトリ。travel-log本体とは独立して更新・管理する。

## フォルダ構成

`<スポットキー>/`(`spot_types.key`、例: `post_office`)フォルダの下に、そのスポットの種類の
データを置く。

```
post_office/
  post_offices.csv
```

現状はCSVのみ。CSV形式はtravel-log本体の`/[type]/admin`のCSVインポート機能
(`components/AdminView.tsx`の`CSV_COLUMNS`)に合わせること。

```csv
name,name_kana,prefecture,municipality,lat,lng,rank,category,description,official_url
```

- 必須列: `name`, `prefecture`, `lat`, `lng`
- `rank`/`category`はスポットの種類ごとに意味が異なってよい自由入力(空でも可)
- 取り込みはtravel-log側の管理画面(`/[type]/admin`)からこのCSVファイルを
  手動アップロードして行う(自動取り込みの仕組みは今のところ無い)

## 各データの出典

- `post_office/post_offices.csv`: 国土交通省 国土数値情報(郵便局データ P30、平成25年度版)。
  行政区域コードを都道府県名・市区町村名に変換、郵便局分類コードを`category`列に変換した加工版。
  非商用利用限定のデータセットである点に注意(travel-log側のCLAUDE.md「外部データソースを
  扱う際の注意」も参照)。

## 将来構想(未実装)

スポットデータ本体だけでなく、スポットの種類そのものの初期設定(`spot_types`テーブル相当の
公開範囲・表示名・スポットキー・ランクの種類とスタイル)も、将来的には
`<スポットキー>/settings.json`のような設定ファイルとしてこのリポジトリ側に持たせ、
travel-log側の`db/init/01_schema.sql`にハードコードされている`spot_types`の初期INSERTを
置き換えられるようにしたい。現時点では未設計・未実装。
