# goshuin(御朱印)

- 全国の寺社仏閣 **51,950件**(御朱印を受けに行く先として使う)
- 出典: OpenStreetMap(Overpass API)の`amenity=place_of_worship`。ランク付けはWikipedia(ja)のページビュー
- ライセンス: **ODbL**(座標・名称)+ **CC BY-SA 4.0**(説明文)。再配布時は出典表示が必要(→[ライセンス](#ライセンス))

| ファイル | 内容 |
|---|---|
| `spots.csv` | スポットデータ(51,950件) |
| `settings.json` | スポット種別の設定(シリーズA〜E・Z) |

## 出典と生成

OpenStreetMap(Overpass API)の寺社仏閣(`amenity=place_of_worship`かつ
`religion=shinto`/`buddhist`)を唯一のスポット候補ソースとして機械生成した。かつてランク付き
(`goshuin_ranked.csv`)と未整理(`goshuin_unranked_z.csv`)の2ファイルに分かれていたものを、
1ファイルに統合して全件を作り直した(Wikipedia記事との突き合わせが甘く、人物記事や
宗教団体の記事にぶら下がった誤ランクが混ざっていたため)。

シリーズ(A〜E)は[tourist](../tourist/README.md)と同じく**Wikipedia(ja)の月次ページビュー数**
(bot除外)のパーセンタイル区分で、Wikipedia記事に紐付かない寺社は`Z`(未整理)。
御朱印は無名の寺社でも受けられるため、`Z`も落とさず同じファイルに収録している。

| シリーズ | 件数 | 内容 |
|---|---|---|
| A〜E | 6,995件 | Wikipedia記事と紐付き、ページビューでランク付けできたもの |
| Z | 44,955件 | Wikipedia記事が無く、OSMに名前付きで採録されているだけのもの |

生成手順(スクリプトはリポジトリに含めていない一時作業):

1. Overpassで47都道府県の`admin_level=4`エリアごとにnode/way/relationを取得(境内が面で
   描かれている寺社を取りこぼさないため。way/relationは重心座標を採用)。`region`列は
   この絞り込みで確定するので、座標からの空間検索による近似判定は不要になった
2. 同名かつ200m以内の要素(建物way+POI nodeなど)を1件に統合
3. OSMの`wikipedia`タグ、無ければ`wikidata`タグ経由でja記事名を解決
4. その記事が**本当にその寺社の記事か**をchiezo(jawikiのローカルミラー)で検証し、
   外れたものはランク付けせず`Z`に落とす:
   - 記事が実在する(リダイレクトは解決する)
   - 冒頭文が寺社の記事である(人物・宗教団体・自治体・駅などを除外。例:
     「崇徳天皇御廟」→崇徳天皇本人の記事、「立正佼成会」→宗教団体の記事)
   - 冒頭文に都道府県名が出る場合、OSM上の所在県と一致する(分社が総本社の記事を
     指しているケースを除外)
   - 「稲荷神社」のような社名全体を説明する総称記事にぶら下がっていない
   - 同じ記事を複数のスポットが指す場合、記事名と一致する1件だけを採用(曖昧なら全て`Z`)
5. ページビューはchiezoがWikimediaの月次ダンプ(`pageview_complete`、bot除外)から
   取り込んだ値を使い、A=上位5%/B=次15%/C=次30%/D=次30%/E=残り20%で区分。
   世界遺産の構成資産などページビューが伸びにくい寺社は目視で格上げする例外を許容する
   (touristと同じハイブリッド方式)
6. `description`はWikipedia記事の冒頭文(200字を目安に文単位で切り出し)、`name_kana`は
   冒頭文の読み仮名から機械抽出(記事名と名称が一致する場合のみ)。名称のうち英語併記
   (`猿田彦神社 (Sarutahiko Shrine)`など)は日本語表記だけに整形
7. ランク付きスポットと100m以内で近接する`Z`(同一寺社の別名タグ等、2,520件)は除外

## ライセンス

- **座標・名称**: OpenStreetMap(Overpass APIでの一括取得)由来で
  [ODbL](https://opendatacommons.org/licenses/odbl/)。まとまった量を再配布する場合は
  「© OpenStreetMap contributors」の表示と、データベース自体をODbL(または互換ライセンス)で
  提供することが求められる
- **説明文**(`description`列): Wikipedia記事の冒頭文由来で
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.ja)
  (出典表示と、改変物の同一・互換ライセンスでの提供が必要)
