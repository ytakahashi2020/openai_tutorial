from openai import OpenAI
client = OpenAI()

response = client.moderations.create(
    input="You are idiot!!!!")

output = response.results[0]

print(output)
