# quiz-generation-baseline

- クイズ作問部門のベースライン実装として、OpenAI APIを用いた実装です。
- テーマを入力として、早押しクイズの問題文と正解の対を出力します。
- OpenAI API の rate limit に対する処理、function callingで期待する応答が得られない場合の処理があまいです。参考としての位置づけとしてご了承ください。


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
{"theme": "藤井聡太"}
```

### 出力

入力に対応する形で、問題文と正解のペアが並びます。

```json
{"theme":"フェルマーの最終定理","question":"フェルマーの最終定理は、17世紀の数学者ピエール・ド・フェルマーが提案した数学の問題です。この問題の中でフェルマーは、ある数学の公式にはどんな制約があるのかを示しています。この公式は、x^n + y^n = z^nの形式を持つ等式です。ただし、nは2より大きい整数です。この公式は、いわゆる「フェルマーの最終定理」という名前で広く知られています。フェルマーの最終定理について、もう少し詳しく説明しますと、フェルマーはこの公式が成立するようなx、y、zの組み合わせは存在しないことを示しています。しかし、この証明には非常に長い時間と高度な数学的な知識が必要です。そのため、証明自体がフェルマーの死後、約350年後の1994年になって初めて証明されました。","answer":"フェルマーの最終定理は、x^n + y^n = z^nの形式を持つ等式がnが2より大きい整数の場合には解を持たないことを示すものです。","reference":null}
{"theme":"カーボンニュートラル","question":"気候変動対策の一環として注目される、地球上の二酸化炭素の排出量を実質的にゼロにすることを目指す概念は何でしょう？","answer":"カーボンニュートラル","reference":null}
{"theme":"藤井聡太","question":"将棋界で注目を集める若手プレーヤーで、2021年に最年少でプロ入りを果たしたのは誰でしょう？","answer":"藤井聡太","reference":null}
```


## 利用方法

- 作問の素材をテーマに関連するwikipedia本文に限定する `--from_wikipedia_content`、一度生成したクイズを評価して見直す `--refine_quiz` を用意しています。意図通りに動作しないこともあり、あくまでもご参考です。

```bash
python ./quizgen-wikipedia-openai-baseline.py input_data.jsonl --output_file output_`date +%Y%m%d-%H%M%S`.jsonl --verbose  --from_wikipedia_content --refine_quiz  --refine--retry_max 1 --debug 
```

## ライセンス

コードに関する部分は、MITライセンスとします。

Copyright (c) 2023 MORIOKA Yasuhiro

以上
