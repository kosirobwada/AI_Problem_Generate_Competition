import openai
import json
from dotenv import load_dotenv
import  os

# 環境変数を読み込む
load_dotenv()

# OpenAI APIキーを設定
openai.api_key = os.getenv('OPENAI_API_KEY')


def generate_quiz(theme, model="text-davinci-003", temperature=0.7):
    prompt = f"テーマ:{theme}\n早押しクイズの問題文とその答えを作成してください。"

    try:
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return str(e)

# OpenAI APIキーを設定
openai.api_key = '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'

# JSONファイルを読み込む
data = []
with open('input_data.jsonl', 'r', encoding='utf-8') as file:
    for line in file:
        data.append(json.loads(line))
# テーマに基づいてクイズを生成
for item in data:
    theme = item.get("theme")
    if theme:
        quiz = generate_quiz(theme)
        print(f"テーマ: {theme}")
        print(f"クイズ: {quiz}\n")
