import openai
import time

# Initialize the client
client = openai.OpenAI()

file = client.files.create(
    file=open("./nobunaga.txt", "rb"),
    purpose='assistants'
)

# Step 1: Create an Assistant
assistant = client.beta.assistants.create(
    name="Customer Service Assistant",
    instructions="You are a customer support chatbot. Use your knowledge base to best respond to customer queries.",
    model="gpt-4-1106-preview",
    tools=[{"type": "retrieval"}],
    file_ids=[file.id]
)

# Step 2: Create a Thread
thread = client.beta.threads.create()

# Step 3: Add a Message to a Thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Tell me about Nobunaga Oda in 30 words."
)

# Step 4: Run the Assistant
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
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
            print(f"{role.capitalize()}: {content}")
        break
    else:
        print("Waiting for the Assistant to process...")
        time.sleep(5)
