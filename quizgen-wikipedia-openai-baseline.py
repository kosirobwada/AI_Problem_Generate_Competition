# # AI王 クイズ生成 ベースライン
# 
# ## 概要
# - 与えられたテーマをもとにして早押しクイズを生成する
# - 入力：テーマ
# - 出力：クイズ(質問、正解, 出典)

import argparse
import json
import os
import random
import time

import numpy as np
import openai
import pandas as pd

import wikipedia

wikipedia.set_lang("ja")


def get_wikipedia_content(theme :str = None, content_len :int = 6000):
  # Wikipediaの見出し語であるか
  titles = wikipedia.search(theme)
  if theme not in titles:
    return None

  # Wikipediaページを取得
  wp = wikipedia.page(theme)
  if wp.title != theme:
    return None

  content = wp.content[:content_len]

  return content


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
#    torch.manual_seed(seed)
#    torch.cuda.manual_seed(seed)
#    torch.backends.cudnn.deterministic = True
#    torch.backends.cudnn.benchmark = False

openai.api_key = os.getenv("OPENAI_API_KEY")


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

def generate_quiz(theme, retry_max=0, interval=1, model="gpt-3.5-turbo"):

    def generate(theme):
        try:
            completion = openai.ChatCompletion.create(
    #            model=OPENAI_MODEL,
                model=model,
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
    #                        },
    #                        "required": ["question","answer","distractors"],
                            },
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
                #  "content": {"question": { "前振り": ..., "後限定": ....}, "answer": ...}
                # }
                try:
                    if message['content'] is not None:
                        res = json.loads(message['content'])
                        res['question'] = "".join(res['question'].values())
                        return res
                except:
                    pass
        except: #  ServiceUnavailableError:
            pass

        return None

    # サービス応答次第でリトライ
    res = None
    for _ in range(retry_max + 1):
        res = generate(theme)
        if res is not None:
            break
        time.sleep(interval)

    return res


def refine_quiz(quiz, retry_max=0, interval=1, model="gpt-3.5-turbo"):

    def refine(quiz):
        try:
            completion = openai.ChatCompletion.create(
                model=model,
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
                #  "content": {"question": { "前振り": ..., "後限定": ....}, "answer": ...}
                # }
                try:
                    if message['content'] is not None:
                        res = json.loads(message['content'])
                        res['question'] = "".join(res['question'].values())
                        return res
                except:
                    pass
        except: #  ServiceUnavailableError:
            pass

        return None

    # サービス応答次第でリトライ
    res = None
    for _ in range(retry_max + 1):
        res = refine(quiz)
        if res is not None:
            break
        time.sleep(interval)

    return res

QG_MATERIAL_SYSTEM_PROMPT="""あなたはプロのクイズ作家です。クイズのよさを評価できます。
以下に示す文章から、クイズの素材にふさわしい部分を抜き出してください。1か所200文字程度で抜き出してください。合計3か所を抜き出して、まとめて出力してください。


"""

QG_MATERIAL_USER_PROMPT = """文章: {content}
"""

def pickup_quiz_material(theme, retry_max=0, interval=1, model="gpt-3.5-turbo"):

    def generate(content):

        try:
            completion = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": QG_MATERIAL_SYSTEM_PROMPT},
                    {"role": "user", "content": QG_MATERIAL_USER_PROMPT.format(content=content)}
                ],
                max_tokens=1500
            )

            message = completion["choices"][0]["message"]
            try:
                return {'content': message['content']}
            except KeyError:
                pass
        except: #  ServiceUnavailableError:
            pass

        return None

    # サービス応答次第でリトライ
    res = None
    for _ in range(retry_max + 1):
        res = generate(theme)
        if res is not None:
            break
        time.sleep(interval)

    return res

def main(args):

    set_seed(args.seed)

    input_data = pd.read_json(args.input_file, lines=True)
    if args.sample > 0:
        input_data = input_data.sample(n=args.sample)

    data = [
        {
            "theme": theme,     # テーマ
            "question": None,   # 問題文
            "answer": None,     # 正解
            "reference": None   # 出典
        } for theme in list(input_data["theme"])
    ]

    for d in data:
        time.sleep(args.interval)

        if args.verbose:
            print("theme:    ", d['theme'])

        # クイズ素材部分の抽出
        if args.use_wikipedia_content:
            content = get_wikipedia_content(d['theme'], content_len=6000)

            res = pickup_quiz_material(content,
                                       retry_max=args.retry_max, 
                                       interval=args.interval,
                                       model=args.material_model)
            if res is None:
                if args.verbose:
                    print('failed to pickup material')
                continue

            material = res['content']
            d['reference'] = material
        else:
            material = d['theme']

        # クイズ生成
        res = generate_quiz(material,
                            retry_max=args.retry_max, 
                            interval=args.interval,
                            model=args.generation_model)
        if res is None:
            if args.verbose:
                print('failed to generate quiz')
            continue
        
        d['question'] = res['question']
        d['answer'] = res['answer']
        if args.verbose:
            print("question:  ", d['question'])
            print("answer:    ", d['answer'])

        if args.refine_quiz:
            # 評価＋修正
            res = refine_quiz(d,
                            retry_max=args.retry_max,
                            interval=args.interval,
                            model=args.refine_model)
            if res is None:
                if args.verbose:
                    print('failed to refine quiz')
                continue

            d['question'] = res['question']
            d['answer'] = res['answer']
            if args.verbose:
                print("refined_question:  ", d['question'])
                print("refined_answer:    ", d['answer'])

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
                        default="output_data.jsonl",
                        help="OpenAIモデルの出力結果を格納するファイル。")
    parser.add_argument("--sample",
                        default=-1,
                        type=int,
                        help="モデルに与えるテーマ数。指定がない場合は全テーマに対して推論を行う。")
    parser.add_argument("--interval",
                        default=3,
                        type=int,
                        help="APIの最小呼び出し間隔。")
    parser.add_argument('--retry_max',
                        default=0,
                        type=int,
                        help="API呼び出しの再試行上限")
    parser.add_argument('--seed',
                        default=42,
                        type=int,
                        help="乱数シード")
    parser.add_argument('--verbose',
                       action='store_true',
                       help="途中経過の出力")
    parser.add_argument('--use_wikipedia_content',
                       action='store_true',
                       help="Wikipedia記事のみ利用")
    parser.add_argument('--refine_quiz',
                       action='store_true',
                       help="生成したクイズを修正する")
    parser.add_argument("--generation_model",
                        default="gpt-3.5-turbo",
                        type=str,
                        help="クイズ生成のモデル"
                        )
    parser.add_argument("--refine_model",
                        default="gpt-3.5-turbo",
                        type=str,
                        help="クイズ修正のモデル"
                        )    
    parser.add_argument("--material_model",
                        default="gpt-3.5-turbo-16k",
                        type=str,
                        help="Wikipedia記事から素材抽出のモデル"
                        )    
    args = parser.parse_args()

    main(args)