# travel-log-data

[travel-log](https://github.com/rtcode337/travel-log)用の初期データを置くリポジトリ。travel-log本体とは独立して更新・管理する。

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
| [restaurant](restaurant/README.md)(有名飲食店) | 171 | Wikipedia(ja)・OpenStreetMap | ODbL / CC BY-SA 4.0 |
| [buratamori](buratamori/README.md)(ブラタモリ) | 406 | jawiki記事 + LLMの記憶(**未検証**) | — |
| [suiyou_dodesho_domestic](suiyou_dodesho_domestic/README.md)(水曜どうでしょう・国内編) | 279 | jawiki記事 + LLMの記憶(**未検証**) | — |
| [suiyou_dodesho_overseas](suiyou_dodesho_overseas/README.md)(水曜どうでしょう・海外編) | 136 | jawiki記事 + LLMの記憶(**未検証**) | ODbL(座標) |

## フォルダ構成

`<スポットキー>/`(`spot_types.key`、例: `tourist`)フォルダの下に、そのスポット種別の
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

### データの形式

各ファイルの形式は**travel-log本体の取り込み機能の仕様**で、このリポジトリはそれに合わせる
だけ。列定義の正はtravel-log側の`components/AdminView.tsx`(`CSV_COLUMNS` /
`ROUTE_CSV_COLUMNS`)で、取り込みは管理画面(`/[type]/admin`)からの手動アップロード。

```csv
name,name_kana,lat,lng,region,series,categories,description,key
```

このリポジトリ側の運用ルールは2つだけ: **改行コードはCRLF**(`.gitattributes`で変換を
無効にしてある)と、**全スポットに`key`を付ける**(travel-log側では省略可だが、`routes.csv`の
参照と再取り込み時の同一判定に使う)。どちらも`python3 .github/scripts/validate_data.py`が
検査する。

## データの検証

```bash
python3 .github/scripts/validate_data.py
```

CSVを編集したらコミット前に実行する(標準ライブラリのみ・依存なし。push・PRでも
GitHub Actionsが同じものを回す)。travel-log側はこのリポジトリのmainを直接読むため、
壊れたCSVはそのまま取り込みの失敗になる。見ているのは列名・改行コード(CRLF)・
必須項目・座標の範囲・`key`の一意性・`routes.csv`の参照先・`settings.json`の妥当性など、
目視では気づけない種類の誤り(検査項目の詳細はスクリプト冒頭のコメントを参照)。

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
