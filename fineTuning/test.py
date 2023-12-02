from openai import OpenAI


client = OpenAI()

response = client.chat.completions.create(
    model="ft:gpt-3.5-turbo-0613:personal::8OKBeVYT",  # ここでファインチューニングされたモデルを使用
    messages=[
        {"role": "system", "content": "このチャットボットはProjectAの内容に対して回答します。"},
        {"role": "user", "content": "これはいつから利用が開始されましたか？"}
    ]
)
print(response.choices[0].message.content)
