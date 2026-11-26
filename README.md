# 概要

[あそぶかい](https://sites.google.com/view/itoasobukai/linktree)で作成した、ブラウザ上でそのまま使えるツールをまとめたページです。  
インストール不要で、PC・スマートフォンのブラウザから利用できます。  
HTMLファイルをダウンロードし、直接開くとオフラインでも使用できます。  
制作は主にClaudeを使用して作成しています。


## ツール一覧

### 1. スコアシート
- **ツールを開く:** [scoresheet_2026.html](./scoresheet_2026.html)
- **概要:** ラウンドごとの得点集計、構成データのJSON保存・読込、結果の画像（PNG）出力ができるスコアシートです。
- **ソースファイル:**
  - [HTMLファイル（scoresheet_2026.html）](https://github.com/asobukaitools/tools/blob/main/scoresheet/scoresheet_2026.html)  
    トリックリスト組み込み版。このバージョンは日本語のみで、Level13までです。
  -  [HTMLファイル（scoresheet.html）](https://github.com/asobukaitools/tools/blob/main/scoresheet/scoresheet.html)  
    トリックリストを組み込む前の本体データです。日本語↔英語の表示切り替えに対応しています。
  - [技リスト組込みスクリプト（Python）](./scoresheet/build.py)  
    毎年変わるトリックリストをscoresheetに組込むためのスクリプト。使い方はスクリプトの冒頭に書いてあります。
  - [技リスト(csv)](./scoresheet/skills.csv)  
    英語切り替えを追加する際には、4列目にトリックの英語表記が入ります。

### 2. 競技タイマー
- **ツールを開く:** [カウントダウンタイマー.html](./CountdownTimer/カウントダウンタイマー.html)
- **概要:** カウントダウンタイマーです。開始前（タイマーイン）も設定可能です。
- **ソースファイル:**
  - [HTMLファイル（カウントダウンタイマー.html）](https://github.com/asobukaitools/tools/blob/main/CountdownTimer/カウントダウンタイマー.html)


## ライセンス
- 改変・配布・商用利用ご自由に可能です。


## 免責事項
- こちらの利用で生じた一切の損害・問題は、当方では責任を負いません。
