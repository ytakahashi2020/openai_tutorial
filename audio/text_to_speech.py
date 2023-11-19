from openai import OpenAI

client = OpenAI()

response = client.audio.speech.create(
    model="tts-1-hd",
    voice="nova",
    input="こんにちは、私はノバです。今日はいい天気ですね。",
)

response.stream_to_file("output2.mp3")
