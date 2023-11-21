from openai import OpenAI
client = OpenAI()

response = client.images.edit(
    model="dall-e-2",
    image=open("./sunlit_lounge.png", "rb"),
    mask=open("./mask.png", "rb"),
    prompt="In the mask.png's mask point , add a flamingo and a palm tree .",
    n=1,
    size="1024x1024"
)
image_url = response.data[0].url

print(response)
