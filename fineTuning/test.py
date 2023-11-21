from openai import OpenAI


client = OpenAI()

response = client.chat.completions.create(
    model="ft:gpt-3.5-turbo-0613:personal::8N9Pvs8n",  # ここでファインチューニングされたモデルを使用
    messages=[
        {"role": "system", "content": "このチャットボットは関西弁で回答します。"},
        {"role": "user", "content": "ドイツの首都はどこですか？"}
    ]
)
print(response.choices[0].message.content)
