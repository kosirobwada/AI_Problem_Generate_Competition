# quiz-generation-baseline

クイズ生成ベースライン実装です。

- OpenAI ChatCompletion API を利用して、与えられたテーマに対するクイズを作成する単純な実装です。
  - エラー対策などは十分ではありません。
- クイズは問題文と正解からなります。
- 入力は、テーマを列挙した、以下の形式の JSONLファイルです。
```json
{"theme": "フェルマーの最終定理"} 
{"theme": "カーボンニュートラル"}
...
```
- 出力は、以下の形式のJSONLファイルです。
```json
{"theme":"フェルマーの最終定理","question":" ...", "answer": ".."}
{"theme":"カーボンニュートラル","question":" ...", "answer": ".."}
...
```

- 参考までに、テーマに対応するWikipedia記事を取得してプロンプトに含める動作と、一度生成したクイズを評価して修正する動作を用意しています。あくまでご参考で、デフォルトではオフとしています。
- 実行例は以下のとおりです。
```bash
python ./quizgen-wikipedia-openai-baseline-nofunccall.py  --retry_max 3 --verbose  input_data.jsonl
```