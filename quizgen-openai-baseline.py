# %% [markdown]
# # AI王 クイズ生成 ベースライン
# 
# ## 概要
# - 与えられたテーマをもとにして早押しクイズを生成する
# - 入力：テーマ
# - 出力：クイズ(質問、正解)

# %%
import random
import numpy as np
import os
import json
import pandas as pd

import time

import argparse

import openai

# %%
def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
#    torch.manual_seed(seed)
#    torch.cuda.manual_seed(seed)
#    torch.backends.cudnn.deterministic = True
#    torch.backends.cudnn.benchmark = False

# %%

openai.api_key = os.getenv("OPENAI_API_KEY")
#OPENAI_MODEL="gpt-4"
OPENAI_MODEL="gpt-3.5-turbo"

QG_GENERATE_MODEL="gpt-3.5-turbo"
QG_REFINE_MODEL="gpt-3.5-turbo"


# %%
QG_SYSTEM_PROMPT = """あなたはプロのクイズ作家です。早押しクイズを作成して下さい。
以下のルールを守ってください。

・テーマに基づいて、問題文と答えからなる早押しクイズを作ってください。
・早押しクイズですので、問題文の前半の「前振り」、問題文の後半の「後限定」、そして「問題の答え」に分けて作ってください
・「前振り」は、答えを説明する修飾師です。できる限り、聞いてためになる情報を盛り込んでください。
・「後限定」は、文末は「でしょう？」で終わるようにしてください。ただし、「誰でしょう？」「何でしょう？」だけでなく、皆が知っているような、答えを確実に導き出せる確実な情報を入れて下さい。
・例を示します。
前振り：小説『白鯨』に登場する捕鯨船の航海士に因んで名付けられた、
後限定：シアトルに本拠地を置く世界的なコーヒーチェーンは何でしょう？
・「前振り」と「後限定」は最後につないで出力してください。自然な文章になるようにして下さい。
・問題の答えとテーマが同じになることは避けてください。
"""
# ・「問題の答え」は、正解の他に、外れ選択肢を３つ作ってください。正解がどれかも示して下さい。

QG_USER_PROMPT = """テーマ:{theme}
"""

QG_REFINE_SYSTEM_PROMPT = """あなたはプロのクイズ作家です。早押しクイズをよりよいものに修正できます。
以下のルールを守ってください。

・以下に示す、テーマ、問題文、正解の組は、一般的なクイズとして適切であるならばそのまま出力してください。適切でないならば、適切なものになるよう。問題文または正解を修正してください。
"""
# ・「問題の答え」は、正解の他に、外れ選択肢を３つ作ってください。正解がどれかも示して下さい。

QG_REFINE_USER_PROMPT = """テーマ:{theme}
問題文:{question}
正解:{answer}
"""



def generate_quiz(theme):


    try:
        completion = openai.ChatCompletion.create(
#            model=OPENAI_MODEL,
            model=QG_GENERATE_MODEL,
            messages=[
                {"role": "system", "content": QG_SYSTEM_PROMPT},
                {"role": "user", "content": QG_USER_PROMPT.format(theme=theme)}
            ],
            functions=[
                {
                    "name": "generate_quiz",
                    "description": "クイズを生成してjson形式で返す",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string", "description": "クイズ問題"
                            },
                            "answer": {
                                "type": "string", "description": "正解"
                            },
#                            "distractors": {
#                                "type": "array", "description": "不正解のリスト",
#                                "items": {
#                                    "type": "string", "description": "不正解"
#                                }
#                            }
                        },
#                        "required": ["question","answer","distractors"],
                        "required": ["question","answer"],
                    },
                }
            ],
            function_call="auto",
        )

        message = completion["choices"][0]["message"]
        try:
            return json.loads(message['function_call']['arguments'])
        except KeyError:
            # 前振り、後限定が個別に返されてしまう場合の対処
            # {
            #  "role": "assistant",
            #  "content": "{\n\"question\": {\n\"\u524d\u632f\u308a\": \"\u30a2\u30cb\u30e1\u300c\u540d\u63a2\u5075\u30b3\u30ca\u30f3\u300d\u3067\u4e3b\u4eba\u516c\u30fb\u5de5\u85e4\u65b0\u4e00\u304c\u6bd2\u3092\u76db\u3089\u308c\u3066\u5c0f\u3055\u304f\u306a\u3063\u305f\u6642\u306b\u540d\u4e57\u3063\u305f\u540d\u524d\u306f\u3001\",\n\"\u5f8c\u9650\u5b9a\":\"\u3042\u308b\u6709\u540d\u306a\u4f5c\u5bb6\u306e\u540d\u524d\u304b\u3089\u53d6\u3089\u308c\u3066\u3044\u307e\u3059\u3002\u305d\u306e\u4f5c\u5bb6\u306e\u540d\u524d\u306f\u4f55\u3067\u3057\u3087\u3046\uff1f\"\n},\n\"answer\": \"\u30a2\u30fc\u30b5\u30fc\u30fb\u30b3\u30ca\u30f3\u30fb\u30c9\u30a4\u30eb\",\n\"distractors\": [\"\u30a2\u30ac\u30b5\u30fb\u30af\u30ea\u30b9\u30c6\u30a3\", \"\u30ed\u30a2\u30eb\u30c9\u30fb\u30c0\u30fc\u30eb\", \"\u30a8\u30c9\u30ac\u30fc\u30fb\u30a2\u30e9\u30f3\u30fb\u30dd\u30fc\"]\n}"
            # }
            try:
                if message['content'] is not None:
                    res = json.loads(message['content'])  # {}"question": { "前振り": ..., "後限定": ....}, "ansaer: ...}
                    res['question'] = "".join(res['question'].values())
                    return res
            except:
                pass
    except: #  ServiceUnavailableError:
        pass

    return None

def refine_quiz(quiz):

    try:
        completion = openai.ChatCompletion.create(
#            model=OPENAI_MODEL,
            model=QG_REFINE_MODEL,
            messages=[
                {"role": "system", "content": QG_REFINE_SYSTEM_PROMPT},
                {"role": "user", "content": QG_REFINE_USER_PROMPT.format(theme=quiz['theme'],
                                                                         question=quiz['question'],
                                                                         answer=quiz['answer'])}
            ],
            functions=[
                {
                    "name": "refine_quiz",
                    "description": "クイズを評価・修正してjson形式で返す",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "theme": {
                                "type": "string", "description": "テーマ"
                            },
                            "question": {
                                "type": "string", "description": "クイズ問題"
                            },
                            "answer": {
                                "type": "string", "description": "正解"
                            },
                        },
                        "required": ["theme", "question","answer"],
                    },
                }
            ],
            function_call="auto",
        )

        message = completion["choices"][0]["message"]
        try:
            return json.loads(message['function_call']['arguments'])
        except KeyError:
            # 前振り、後限定が個別に返されてしまう場合の対処
            # {
            #  "role": "assistant",
            #  "content": "{\n\"question\": {\n\"\u524d\u632f\u308a\": \"\u30a2\u30cb\u30e1\u300c\u540d\u63a2\u5075\u30b3\u30ca\u30f3\u300d\u3067\u4e3b\u4eba\u516c\u30fb\u5de5\u85e4\u65b0\u4e00\u304c\u6bd2\u3092\u76db\u3089\u308c\u3066\u5c0f\u3055\u304f\u306a\u3063\u305f\u6642\u306b\u540d\u4e57\u3063\u305f\u540d\u524d\u306f\u3001\",\n\"\u5f8c\u9650\u5b9a\":\"\u3042\u308b\u6709\u540d\u306a\u4f5c\u5bb6\u306e\u540d\u524d\u304b\u3089\u53d6\u3089\u308c\u3066\u3044\u307e\u3059\u3002\u305d\u306e\u4f5c\u5bb6\u306e\u540d\u524d\u306f\u4f55\u3067\u3057\u3087\u3046\uff1f\"\n},\n\"answer\": \"\u30a2\u30fc\u30b5\u30fc\u30fb\u30b3\u30ca\u30f3\u30fb\u30c9\u30a4\u30eb\",\n\"distractors\": [\"\u30a2\u30ac\u30b5\u30fb\u30af\u30ea\u30b9\u30c6\u30a3\", \"\u30ed\u30a2\u30eb\u30c9\u30fb\u30c0\u30fc\u30eb\", \"\u30a8\u30c9\u30ac\u30fc\u30fb\u30a2\u30e9\u30f3\u30fb\u30dd\u30fc\"]\n}"
            # }
            try:
                if message['content'] is not None:
                    res = json.loads(message['content'])  # {}"question": { "前振り": ..., "後限定": ....}, "ansaer: ...}
                    res['question'] = "".join(res['question'].values())
                    return res
            except:
                pass
    except: #  ServiceUnavailableError:
        pass

    return None


def main(args):

    set_seed()

    input_data = pd.read_json(args.input_file, lines=True)
    if args.sample > 0:
        input_data = input_data.sample(n=args.sample)

    data = [
        {
            "theme": theme,     # テーマ
            "question": None,           # 問題文
            "answer": None,             # 正解
        } for theme in list(input_data["theme"])
    ]

    for d in data:
        if args.verbose:
            print("theme:    ", d['theme'])

        # クイズ生成
        for _ in range(args.maxretry):
            res = generate_quiz(d['theme'])
            if res is not None:
                break
            time.sleep(args.interval)
            if args.verbose:
                print("retry ...")

        if res is not None:
            d['question'] = res['question']
            d['answer'] = res['answer']
            print("question: ", d['question'])
            print("answer:   ", d['answer'])

            # 評価＋修正
            for _ in range(args.maxretry):
                res = refine_quiz(d)
                if res is not None:
                    break
                time.sleep(args.interval)
                if args.verbose:
                    print("retry ...")

            if res is not None:
                d['question'] = res['question']
                d['answer'] = res['answer']
                if args.verbose:
                    print("refined_question: ", d['question'])
                    print("refined_answer:   ", d['answer'])
            
        else:
            if args.verbose:
                print('cannot generate quiz')
        time.sleep(args.interval)

    pd.DataFrame(data).to_json(args.output_file, orient='records', force_ascii=False, lines=True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""
    OpenAI APIを用いたクイズ生成のサンプルコード。
    """)
    parser.add_argument("input_file",
                        type=str,
                        help="json lines形式で1行1テーマで書かれている評価データセット。"
                        )
    parser.add_argument("--output_file",
                        type=str,
                        default="output_generaetd.jsonl",
                        help="OpenAIモデルの出力結果を格納するファイル。")
    parser.add_argument("--sample",
                        default=-1,
                        type=int,
                        help="モデルに解かせる問題数。指定がない場合は全データに対して推論を行う。")
    parser.add_argument("--interval",
                        default=3,
                        type=int,
                        help="APIの最小呼び出し間隔。")
    parser.add_argument('--maxretry',
                        default=10,
                        type=int,
                        help="API呼び出しの再試行上限")
    parser.add_argument('--verbose',
                       action='store_true',
                       help="途中経過の出力")
    args = parser.parse_args()

    main(args)