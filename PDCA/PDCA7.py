import openai
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import wikipedia

# 環境変数を読み込む
load_dotenv()

# Wikipediaの言語設定を日本語に変更
wikipedia.set_lang("ja")

# OpenAI APIキーを設定
openai.api_key = os.getenv('OPENAI_API_KEY')

def retrieve_information(theme):
    try:
        # Wikipediaからテーマに関連する情報を取得
        page = wikipedia.page(theme)
        return page.content[:1500]  # 最初の1500文字を取得
    except:
        return None

def generate_quiz(theme, model="text-davinci-003", temperature=0.7):
    try:
        retrieved_content = retrieve_information(theme)
        if retrieved_content:
            #print("Retrieved Content: ", retrieved_content)
            prompt = f"以下の情報に基づいて、テーマ:{theme}に関する早押しクイズの問題文とその答えを作成してください。問題は単語で答えることの可能な問題にしてください。ただし、問題文は、「問題：」で始め、語尾は絶対に「〇〇でしょう？」という形にしてください。また、答えは「答え：」で始めてください。\n\n{retrieved_content}\n\n問題："
        else:
            prompt = f"テーマ:{theme}\nに関する早押しクイズの問題文とその答えを作成してください。ただし、問題文は、「問題：」で始め、語尾は絶対に「〇〇でしょう？」という形にしてください。また、答えは「答え：」で始めてください。"
        
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=150
        )
        text = response.choices[0].text.strip()
        if "答え：" in text:
            question, answer = text.split("答え：", 1)
            return question.strip(), answer.strip()
        else:
            return "問題が見つかりませんでした", "回答が見つかりませんでした"
    except Exception as e:
        return str(e), "エラーが発生しました"

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
        if answer_text.startswith("答え："):
            answer_text = answer_text[3:]  # 先頭の '答え：' を取り除く
        quiz_results.append({"theme": theme, "quiz": quiz_text, "answer": answer_text})

# タイムスタンプを取得してファイル名を生成
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
output_filename = f"output_{timestamp}.json"

# 結果をJSONファイルに保存
with open(output_filename, 'w', encoding='utf-8') as file:
    json.dump(quiz_results, file, ensure_ascii=False, indent=4)
