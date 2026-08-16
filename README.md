# travel-log-data

[travel-log](https://github.com/rtcode337/travel-log)用の初期データを置くリポジトリ。travel-log本体とは独立して更新・管理する。

> **リポジトリ直下に`LICENSE`は置いていない。** 由来元の条件がスポット種別ごとに違い、
> 全体を1つのライセンスで括れないため。再配布・二次利用の条件は
> [ライセンスと出典表示](#ライセンスと出典表示)にまとめてある。

## 収録データ

スポット種別ごとの詳細(出典・生成手順・収録の基準・ライセンス)は各フォルダのREADMEが正。

| スポット種別 | 内容 | 件数 | 主な出典 | ライセンス・制限 |
|---|---|---|---|---|
| [tourist](tourist/README.md)<br>(観光地) | 日本全国の観光地。travel-log側の唯一の既定種別 | 10,705 | 説明文: Wikipedia(ja)の記事<br>座標: Wikipedia(ja)の記事・Wikidata | 説明文: CC BY-SA 4.0<br>座標: CC BY-SA 4.0・CC0 |
| [goshuin](goshuin/README.md)<br>(御朱印) | 御朱印を受けに行く先としての全国の寺社仏閣 | 51,950 | 説明文: Wikipedia(ja)の記事<br>座標・名称: OpenStreetMap | 説明文: CC BY-SA 4.0<br>座標・名称: ODbL |
| [post_office](post_office/README.md)<br>(郵便局) | 全国の郵便局 | 24,526 | 名称・座標: 国土数値情報(郵便局データ P30) | **非商用利用限定** |
| [restaurant](restaurant/README.md)<br>(有名飲食店) | Wikipedia(ja)に記事がある店に絞った飲食店(網羅ではない) | 171 | 説明文: Wikipedia(ja)の記事<br>座標: OpenStreetMap | 説明文: CC BY-SA 4.0<br>座標: ODbL |
| [buratamori](buratamori/README.md)<br>(ブラタモリ) | NHK「ブラタモリ」の訪問地(ルート3本) | 420 | 説明文: LLMの記憶(**未検証**。訪問地の一覧のみWikipedia(ja))<br>座標: OpenStreetMap | 説明文: 出典なし<br>座標: ODbL |
| [suiyou_dodesho_domestic](suiyou_dodesho_domestic/README.md)<br>(水曜どうでしょう・国内編) | HTB「水曜どうでしょう」国内39企画の立ち寄り地(ルート34本) | 331 | 説明文: LLMの記憶(**未検証**。企画・行程のみWikipedia(ja))<br>座標: OpenStreetMap | 説明文: 出典なし<br>座標: ODbL |
| [suiyou_dodesho_overseas](suiyou_dodesho_overseas/README.md)<br>(水曜どうでしょう・海外編) | 同・海外15企画の立ち寄り地(29ヵ国・ルート15本) | 142 | 説明文: LLMの記憶(**未検証**。企画・旅程のみWikipedia(ja))<br>座標: OpenStreetMap | 説明文: 出典なし<br>座標: ODbL |
| [anime_seichi](anime_seichi/README.md)<br>(アニメ聖地) | アニメの聖地。アニメツーリズム協会の現行の選定地と、Wikipedia(ja)の舞台カテゴリ由来の2系統 | 498 | 説明文: Wikipedia(ja)の記事(全行の根拠を`evidence.csv`に保持)<br>座標: OpenStreetMap | 説明文: CC BY-SA 4.0<br>座標: ODbL |
| [gotouchi_gourmet](gotouchi_gourmet/README.md)<br>(ご当地グルメ) | ご当地グルメ・郷土料理を、その料理の**発祥地**に置いたもの | 553 | 説明文: Wikipedia(ja)の記事(全行の根拠を`evidence.csv`に保持)<br>座標: OpenStreetMap | 説明文: CC BY-SA 4.0<br>座標: ODbL |

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

**このリポジトリ全体に適用される単一のライセンスは無い。** 条件は使うスポット種別の
フォルダごとに決まる。travel-log本体(MIT)とは別物なので、本体のライセンスは根拠にならない。

### 使う前に確認すること

| 使う種別 | 掛かる制約 |
|---|---|
| `post_office` | **商用利用できない。** 出典が国土数値情報(非商用利用限定)のため、表示だけでは足りない |
| `tourist` | 出典表示が要る。説明文を再配布するなら、その配布物も CC BY-SA 4.0(または互換)にする |
| 上記以外(`goshuin`・`restaurant`・`anime_seichi`・`gotouchi_gourmet`・`buratamori`・`suiyou_dodesho_*`) | 出典表示が要る。説明文を再配布するなら CC BY-SA 4.0(または互換)、**座標を含むデータベースを再配布するなら ODbL(または互換)**にする |

複数の種別を混ぜて再配布する場合は、**混ぜたものすべての条件が同時に掛かる**。
`post_office`を混ぜた時点で、その配布物全体が商用利用できなくなる。

`buratamori`・`suiyou_dodesho_domestic`・`suiyou_dodesho_overseas`の説明文は
**出典を持たない未検証データ**(LLMの記憶による推定)で、内容の正しさは保証しない。
座標はOpenStreetMap由来のためODbLが掛かる。

### 表示する文言

再配布時はそのまま使える。使った種別に応じて必要な行だけ残す。

```
出典: フリー百科事典『ウィキペディア(Wikipedia)』(CC BY-SA 4.0)
座標データ: © OpenStreetMap contributors (ODbL)
郵便局データ: 国土数値情報(郵便局データ P30)/ 国土交通省 ※非商用利用限定
```

Wikipedia由来の説明文は、どの記事から取ったかを行単位で辿れるようにしてある種別が
ある(`anime_seichi/evidence.csv`など)。個別の記事名まで示す場合はそちらを使う。

### 新しいデータを足すとき

由来元の条件を確認し、**そのスポット種別のREADMEの「ライセンス」節**と上の
「収録データ」の表の両方に書く。判断に迷う場合(取り方によってODbLの表示義務が
変わるか、など)の基準はCLAUDE.mdの「外部データソース…を扱う際の注意」を参照。
