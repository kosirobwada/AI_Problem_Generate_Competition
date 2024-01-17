import openai
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import wikipedia
import csv

# 環境変数を読み込む
load_dotenv()

# OpenAI APIキーを設定
openai.api_key = os.getenv('OPENAI_API_KEY')
def ask_gpt_chat(question, model="gpt-3.5-turbo", temperature=0.7):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ],
            temperature=temperature
        )
        return response.choices[0].message['content']
    except Exception as e:
        return str(e)

def main():
    while True:
        question = input("質問を入力してください (終了するには 'exit' と入力): ")
        if question.lower() == 'exit':
            break
        answer = ask_gpt_chat(question)
        print("回答:", answer)

if __name__ == "__main__":
    main()