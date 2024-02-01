# AIを用いた問題作成
## 各種リンク
- [SIGNATE-AI王：問題作成部門](https://signate.jp/competitions/1234)で3位入賞しました。

- [YouTubeでの配信はこちら](https://www.youtube.com/watch?v=5pT5t6e_bLo&t=5448s) 1:29:37~解法の説明をしています。

- [解法のPDF](https://github.com/kosirobwada/AI_Problem_Generate_Competition/blob/main/SIGNATE%20AI%E7%8E%8B.pdf)

- [表彰状](https://github.com/kosirobwada/AI_Problem_Generate_Competition/blob/main/AIoh4_certificate_m3.pdf)
## 環境

```bash
#python == 3.10.12
pip install numpy openai pandas wikipedia

```

## 入出力

### 入力

JSONL形式でテーマを並べます。

```json
{"theme": "フェルマーの最終定理"} 
{"theme": "カーボンニュートラル"}
```

### 出力

入力に対応する形で、問題文と正解のペアが並びます。

jsonl
```json
{"theme":"フェルマーの最終定理","question":" ...", "answer": ".."}
{"theme":"カーボンニュートラル","question":" ...", "answer": ".."}
```

csv
```csv
theme,question,answer,reference
フェルマーの最終定理,....
カーボンニュートラル,...
```


## 利用方法

```bash
python ./FInal_round/ans.py
```


## ライセンス

コードに関する部分は、MITライセンスとします。

Copyright (c) 2023 MORIOKA Yasuhiro

以上
