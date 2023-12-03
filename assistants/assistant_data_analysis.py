import openai
import time

# Initialize the client
client = openai.OpenAI()

file = client.files.create(
    file=open("./songs.csv", "rb"),
    purpose='assistants'
)

# Step 1: Create an Assistant
assistant = client.beta.assistants.create(
    name="Data Analyst Assistant",
    instructions="You are a personal Data Analyst Assistant",
    model="gpt-4-1106-preview",
    tools=[{"type": "code_interpreter"}],
    file_ids=[file.id]
)

# Step 2: Create a Thread
thread = client.beta.threads.create()

# Step 3: Add a Message to a Thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Please tell me top3 popular artists by using the csv file and please provide me the csv file."
)

# Step 4: Run the Assistant
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    # instructions="What are the most popular tracks and their artists? and please provide me the top5 csv file."
)

print("Status:", run.status)

while True:
    # Wait for 5 seconds
    time.sleep(5)

    # Retrieve the run status
    run_status = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    print("Status:", run_status.status)

    # If run is completed, get messages
    if run_status.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )

        # Loop through messages and print content based on role
        for msg in messages.data:
            role = msg.role
            content = msg.content[0].text.value
            # print(f"{role.capitalize()}: {content}")
            if msg.content[0].text.annotations:
                file_id = msg.content[0].text.annotations[0].file_path.file_id
                print("file_id: ", file_id)
                file_data = client.files.retrieve_content(file_id=file_id)
                print("file_data: ", file_data)
                file_data_bytes = file_data.encode()

                # ローカルのファイルに書き込み
                with open("./my-file.csv", "wb") as file:
                    file.write(file_data_bytes)
        break
    else:
        print("Waiting for the Assistant to process...")
        time.sleep(5)
