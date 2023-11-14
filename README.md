# quiz-generation-baseline

- クイズ作問部門のベースライン実装としての、OpenAI APIを用いた実装です。
- テーマを入力として、早押しクイズの問題文と正解の対を出力します。
- OpenAI API の rate limit に対する処理、function callingで期待する応答が得られない場合の処理が十分ではありません。参考としての位置づけとしてご了承ください。
  - function callingを用いない `quizgen-wikipedia-openai-baseline-nofunccall.py` を合わせて用意しています。
- 2023/08/31 以降、コードの変更は行いません。

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
...
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
python ./quizgen-wikipedia-openai-baseline.py input_data.jsonl --output_file output_data.jsonl --verbose --debug 
python ./conv_jsonl_to_csv.py output_data.jsonl output_data.csv
```


- 意図通りに動作しないこともあり、あくまでご参考ですが、以下のオプションを用意しています。
  - `--from_wikipedia_content` : 作問の素材をテーマに関連するwikipedia本文に限定する
  - `--refine_quiz`  : 一度生成したクイズを評価して見直す


```bash
python ./quizgen-wikipedia-openai-baseline.py input_data.jsonl --output_file output_data.jsonl --verbose  --from_wikipedia_content --refine_quiz  --refine--retry_max 1 --debug 
python ./conv_jsonl_to_csv.py output_data.jsonl output_data.csv
```

## ライセンス

コードに関する部分は、MITライセンスとします。

Copyright (c) 2023 MORIOKA Yasuhiro

以上
