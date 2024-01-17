import openai
import json
from dotenv import load_dotenv
import os
from datetime import datetime

# 環境変数を読み込む
load_dotenv()

# OpenAI APIキーを設定
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_quiz(theme, model="text-davinci-003", temperature=0.7):
    prompt = f"テーマ:{theme}\nに関する早押しクイズの問題文とその答えを作成してください。ただし、問題文は、「問題：」で始めること。答えは「答え：」で始めること。"

    try:
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=150
        )
        text = response.choices[0].text.strip()
        # クイズの問題文と回答を分割するロジック
        if "答え：" in text:
            question, answer = text.split("答え：", 1)
            return question.strip(), answer.strip()
        else:
            return text, "回答が見つかりませんでした"
    except Exception as e:
        return str(e), str(e)

# JSONファイルを読み込む
data = []
with open('input_data.jsonl', 'r', encoding='utf-8') as file:
    for line in file:
        data.append(json.loads(line))

# テーマに基づいてクイズを生成し、結果を格納
quiz_results = []
for item in data:
    theme = item.get("theme")
    if theme:
        quiz_text, answer_text = generate_quiz(theme)
        quiz_results.append({"theme": theme, "quiz": quiz_text, "answer": answer_text})

# タイムスタンプを取得してファイル名を生成
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
output_filename = f"output_{timestamp}.json"

# 結果をJSONファイルに保存
with open(output_filename, 'w', encoding='utf-8') as file:
    json.dump(quiz_results, file, ensure_ascii=False, indent=4)
