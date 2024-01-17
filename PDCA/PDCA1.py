import openai
import json

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

# テーマの例
theme = "フェルマーの最終定理"

# クイズの生成
quiz = generate_quiz(theme)
print(quiz)
