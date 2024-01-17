import openai
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import wikipedia
import csv
import time

# 環境変数を読み込む
load_dotenv()

start_time = time.time()

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

def generate_quiz(theme, model="gpt-4", temperature=0):
    try:
        retrieved_content = retrieve_information(theme)
        if retrieved_content:
            prompt = (
                f"以下の情報に基づいて、テーマ:{theme}に関する早押しクイズの問題文とその答えを作成してください。\n"
                "答えは必ず単語で答えられる問題を生成してください。\n"
                "ただし、答えは「答え：」で始めてください。...\n\n"
                "問題作成のポイント：\n"
                "- 問題文から答えが一意に絞り込めるか。\n"
                "- 問題文と想定解が正しく対応しているか。\n"
                "- 問題文と想定解が正しい内容と言えるか。\n"
                "問題文は80字以内にしてください。\n"
                "もう一度言いますが、答えは「答え：」で始めてください。...\n\n"
                "情報：{retrieved_content}\n\n"
                "問題："
            )
            # print(retrieved_content)
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            text = response.choices[0].message['content']
        if "答え：" in text:
            question, answer = text.split("答え：", 1)
            return question.strip(), answer.strip()
        else:
            return "適切なクイズが生成できませんでした", ""
    except Exception as e:
        return f"エラーが発生しました: {str(e)}", ""

def review_quiz(quiz_question, quiz_answer, model="gpt-4", temperature=0):
    try:
        print(quiz_question)
        print(quiz_answer)
        if quiz_question == "適切なクイズが生成できませんでした" or quiz_answer == "" or quiz_question =="":
            prompt = (
                f"テーマ:{theme}に関する早押しクイズの問題文とその答えを作成してください。\n"
                "答えは必ず単語で答えられる問題を生成してください。\n"
                "ただし、答えは「答え：」で始めてください。...\n\n"
                "問題作成のポイント：\n"
                "- 問題文から答えが一意に絞り込めるか。\n"
                "- 問題文と想定解が正しく対応しているか。\n"
                "- 問題文と想定解が正しい内容と言えるか。\n"
                "もう一度言いますが、答えは必ず「答え：」で始めてください。...\n\n"
                "問題："     
            )
        else: 
            prompt = (
                f"以下のクイズの問題と答えをレビューしてください。\n\n"
                f"問題：{quiz_question}\n"
                f"答え：{quiz_answer}\n\n"
                "このクイズの質はどうですか？ 問題や答えに改善が必要な点はありますか？\n"
                "レビューのポイント：\n"
                "- 問題の語句に修飾語を付けるとしたらどこに何を付けるか。\n"
                "- 問題文から答えが一意に絞り込めるか。\n"
                "- 問題文と想定解が正しく対応しているか。\n"
                "- 問題文に雑学的なトピックや興味深い情報などが適切に盛り込まれているか。具体的にどんなトピックを入れるかを考えてください。\n"
                "上記のポイントに基づいて、クイズの質を評価し、改善が必要な点を指摘してください。"
                "簡潔な文よりも、冗長な文の方が好ましいです。"
                "ただし、問題文は複数になってはいけません。"
                "また、解答も単語にならなければなりません。" 
                "補足情報は名詞を修飾する形で、必ず問題文に入れてください。"           
            )

        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )

        review_result = response.choices[0].message['content']
        print(review_result)
        return quiz_question, quiz_answer, review_result.strip()
    except Exception as e:
        return "エラーが発生しました: " + str(e), "", ""

def final_quiz(theme, quiz_question, quiz_answer, review_result, model="gpt-4", temperature=0):
    try:
        if quiz_question == "適切なクイズが生成できませんでした" or quiz_answer == "" or quiz_question =="":
            prompt = (
                f"テーマ:{theme}に関する早押しクイズの問題文とその答えを作成してください。\n"
                "答えは必ず単語で答えられる問題を生成してください。\n"
                "ただし、答えは「答え：」で始めてください。...\n\n"
                "問題作成のポイント：\n"
                "- 問題文から答えが一意に絞り込めるか。\n"
                "- 問題文と想定解が正しく対応しているか。\n"
                "- 問題文と想定解が正しい内容と言えるか。\n"
                "もう一度言いますが、答えは必ず「答え：」で始めてください。...\n\n"
                "問題："            
            )
        else:
            prompt = (
                f"以下のレビューを参考にして最終的な問題と答えを作成してください。\n\n"
                "ただし、答えは「答え：」で始めてください。...\n\n"
                "また、問題文は複数の文にならないようにしてください。"
                "日本語として違和感のない文章にしてください。"
                f"テーマ：{theme}\n"
                f"問題：{quiz_question}\n"
                f"答え：{quiz_answer}\n\n"
                f"レビュー：{review_result}"            
            )

        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        text = response.choices[0].message['content']
        if "答え：" in text:
            question, answer = text.split("答え：", 1)
            return question.strip(), answer.strip()
        else:
            return "適切なクイズが生成できませんでした", ""
    except Exception as e:
        return f"エラーが発生しました: {str(e)}", ""
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
        quiz_text, answer_text, review_result = review_quiz(quiz_text,answer_text)
        quiz_text, answer_text = final_quiz(theme, quiz_text, answer_text, review_result)
        if "問題：" in quiz_text:
            quiz_text = quiz_text[3:]
        answer_text = answer_text.split('\n',1)[0]
        print(quiz_text)
        print(answer_text)
        quiz_results.append({"theme": theme, "quiz": quiz_text, "answer": answer_text})
        
# タイムスタンプを取得してファイル名を生成
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
output_filename = f"output_{timestamp}.jsonl"

# 結果をJSONLファイルに保存
with open(output_filename, 'w', encoding='utf-8') as file:
    for item in quiz_results:
        json.dump(item, file, ensure_ascii=False)
        file.write('\n')

# CSVファイルへの変換
csv_output_filename = f"output_{timestamp}.csv"

# 結果をCSVファイルに保存
with open(csv_output_filename, 'w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    # CSVのヘッダーを書き込み
    csv_writer.writerow(['theme', 'quiz', 'answer'])

    # 各クイズの結果をCSVに書き込み
    for item in quiz_results:
        csv_writer.writerow([item['theme'], item['quiz'], item['answer']])

# スクリプトの実行終了時刻を記録
end_time = time.time()

# 実行時間を計算（秒単位）
execution_time = end_time - start_time

print(f"実行時間: {execution_time} 秒")