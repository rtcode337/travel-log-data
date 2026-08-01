# travel-log-data

[travel-log](https://github.com/rtcode337/travel-log)用の初期データを置くリポジトリ。travel-log本体とは独立して更新・管理する。

> **このリポジトリ全体に適用される単一のライセンスはありません。** フォルダ(スポットキー)
> ごとに由来元のライセンス・利用制限が異なるため、リポジトリ直下に`LICENSE`は置いていません。
> 再配布・二次利用の際は、下の「収録データ」の表と各フォルダのREADMEを確認してください。

## 収録データ

スポット種別ごとの詳細(出典・生成手順・収録の基準・ライセンス)は各フォルダのREADMEが正。

| スポット種別 | 内容 | 件数 | 主な出典 | ライセンス・制限 |
|---|---|---|---|---|
| [tourist](tourist/README.md)<br>(観光地) | 日本全国の観光地。travel-log側の唯一の既定種別 | 10,708 | 説明文: Wikipedia(ja)の記事<br>座標: Wikipedia(ja)の記事・Wikidata | 説明文: CC BY-SA 4.0<br>座標: CC BY-SA 4.0・CC0 |
| [goshuin](goshuin/README.md)<br>(御朱印) | 御朱印を受けに行く先としての全国の寺社仏閣 | 51,950 | 説明文: Wikipedia(ja)の記事<br>座標・名称: OpenStreetMap | 説明文: CC BY-SA 4.0<br>座標・名称: ODbL |
| [post_office](post_office/README.md)<br>(郵便局) | 全国の郵便局 | 24,526 | 名称・座標: 国土数値情報(郵便局データ P30) | **非商用利用限定** |
| [restaurant](restaurant/README.md)<br>(有名飲食店) | Wikipedia(ja)に記事がある店に絞った飲食店(網羅ではない) | 171 | 説明文: Wikipedia(ja)の記事<br>座標: OpenStreetMap | 説明文: CC BY-SA 4.0<br>座標: ODbL |
| [buratamori](buratamori/README.md)<br>(ブラタモリ) | NHK「ブラタモリ」の訪問地(ルート3本) | 406 | 説明文: LLMの記憶(**未検証**。訪問地の一覧のみWikipedia(ja))<br>座標: OpenStreetMap | 説明文: 出典なし<br>座標: ODbL |
| [suiyou_dodesho_domestic](suiyou_dodesho_domestic/README.md)<br>(水曜どうでしょう・国内編) | HTB「水曜どうでしょう」国内39企画の立ち寄り地(ルート34本) | 279 | 説明文: LLMの記憶(**未検証**。企画・行程のみWikipedia(ja))<br>座標: OpenStreetMap | 説明文: 出典なし<br>座標: ODbL |
| [suiyou_dodesho_overseas](suiyou_dodesho_overseas/README.md)<br>(水曜どうでしょう・海外編) | 同・海外15企画の立ち寄り地(29ヵ国・ルート15本) | 136 | 説明文: LLMの記憶(**未検証**。企画・旅程のみWikipedia(ja))<br>座標: OpenStreetMap | 説明文: 出典なし<br>座標: ODbL |
| [anime_seichi](anime_seichi/README.md)<br>(アニメ聖地) | アニメ・漫画の聖地。アニメツーリズム協会の現行の選定地が母数(名称のみ取得し、データはWikipedia/OSMから取り直し) | 101 | 説明文: Wikipedia(ja)の記事(全行の根拠を`evidence.csv`に保持)<br>座標: OpenStreetMap | 説明文: CC BY-SA 4.0<br>座標: ODbL |

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
だけ。列の定義と取り込みの挙動(差分更新の同一判定など)は
[travel-log/README.mdの「外部データ(travel-log-data)」](https://github.com/rtcode337/travel-log#外部データtravel-log-data)を参照
(実装上の正はtravel-log側の`components/AdminView.tsx`の`CSV_COLUMNS` / `ROUTE_CSV_COLUMNS`)。

取り込みはtravel-log側の管理画面(`/[type]/admin`)の「GitHubリポジトリからスポット種別取り込み」から、
このリポジトリのmainを直接読んで種別ごとに一括適用する(ファイルを手元にダウンロードして
アップロードする経路も残っている)。

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

番組ロケ地の3種別(buratamori・水曜どうでしょう)は説明文がLLMの記憶で出典を持たないが、
**座標はOSM由来のためODbLが適用される**。1件ずつ座標を裏取りした場合も、Overpass APIでの
一括抽出と区別せず表示義務が付くものとして扱う。
