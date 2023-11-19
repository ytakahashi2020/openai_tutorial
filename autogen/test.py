import openai
import time
import json
from yfinance import Ticker
import subprocess

# Initialize the client
client = openai.OpenAI()
agents = {}


def get_stock_price(symbol: str) -> float:
    stock = Ticker(symbol)
    price = stock.history(period="1d")['Close'].iloc[-1]
    return price


def run_file(file_name):
    try:
        result = subprocess.run(
            ['python3', file_name],
            text=True,
            capture_output=True,
            check=True
        )
        print(result.stdout)
        return result.stdout or "No output"
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.stderr}"


def create_file(file_name, body):
    with open(file_name, "w") as f:
        f.write(body)

    return f"File written to {file_name}"


def provide_instruction(query):
    global agents

    # Here, 'coding_assistant' is assumed to be the key for the desired assistant in agents
    assistant_info = agents["coding_assistant"]
    assistant = assistant_info["agent"]
    thread = assistant_info.get("thread")
    funcs = assistant_info["funcs"]

    # If there is no thread between user proxy and this agent, create one
    if not thread:
        thread = client.beta.threads.create()
        # Update the thread in agents
        agents["coding_assistant"]["thread"] = thread

    message = execute(assistant, thread, query, funcs)

    return message


tools_list = [
    {
        "type": "function",
        "function": {
            "name": "run_file",
            "description": "Execute a Python script from the specified file path and records its output and errors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "The path of the .py file that needs to be run."
                    }
                },
                "required": ["file_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Think step by step to determine the correct actions that are needed to be taken in order to complete the task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "The name of the file including the extension"
                    },
                    "body": {
                        "type": "string",
                        "description": "Correct contents of a file"
                    }
                },
                "required": ["file_name", "body"]
            }
        }
    }
]

user_proxy_tools_list = [
    {
        "type": "function",
        "function": {
            "name": "provide_instruction",
            "description": "coding_assistant is a world-class programming AI proficient in executing Python code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Define the task for the recipient agent to accomplish, emphasizing the clear explanation of the task's requirements rather than detailed instructions."
                    }
                },
                "required": ["query"]
            }
        }
    }
]


def execute(assistant, thread, query, funcs):

    # Step 3: Add a Message to a Thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=query
    )

    # Step 4: Run the Assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Please address the user as Mervin Praison."
    )

    print(run.model_dump_json(indent=4))

    while True:
        # Wait for 5 seconds
        time.sleep(5)

        # Retrieve the run status
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print(run_status.model_dump_json(indent=4))

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

            for msg in messages.data:
                if msg.role == 'user':
                    return msg.content[0].text.value
                else:
                    return "No response"
        elif run_status.status == 'requires_action':
            print("Requires action")
            required_actions = run_status.required_action.submit_tool_outputs.model_dump()
            print(required_actions)
            tools_output = []
            for action in required_actions["tool_calls"]:
                func_name = action["function"]["name"]
                arguments = json.loads(action["function"]["arguments"])
                if func_name in funcs:
                    func = funcs[func_name]
                    output = func(**arguments)
                    if output is not None:  # Check if output is not None
                        tools_output.append({
                            "tool_call_id": action["id"],
                            "output": output
                        })
                    else:
                        print(f"Function {func_name} returned None")
                else:
                    print("Function not found")

            # Submit the tool outputs to Assistant API
            submit_tool_outputs = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tools_output
            )
            print(submit_tool_outputs.model_dump_json(indent=4))

        else:
            print("Waiting for the Assistant to process...")


if __name__ == '__main__':
    # Step 1: Create an Assistant
    coding_assistant = client.beta.assistants.create(
        name='Coding Assistant Agent',
        instructions="As an advanced programming AI, your expertise lies in developing precise Python scripts. Ensure that files are aptly named and Python code is meticulously crafted with necessary imports to meet user requests. Execute required code prior to providing a response to the user.",
        model="gpt-4-1106-preview",
        tools=tools_list,
    )

    funcs = {
        "run_file": run_file,
        "create_file": create_file
    }

    agents = {
        "coding_assistant": {
            "agent": coding_assistant,
            "thread": None,
            "funcs": funcs
        }
    }

    user_proxy = client.beta.assistants.create(
        name="User Proxy Agent",
        instructions="""Your role as a user proxy agent is to facilitate smooth communication between the user and other agents in this group chat via the provide_instruction function. 
            It is your responsibility to convey user requests clearly to the appropriate agents and ensure consistent interaction to ensure the completion of the user's task. 
            Respond to the user only once the task is completed, an error is reported by the relevant agent, or when you are confident about your response.""",
        model="gpt-4-1106-preview",
        tools=user_proxy_tools_list,
    )

    # Step 2: Create a Thread
    thread = client.beta.threads.create()

    while True:
        query = input("User: ")

        user_proxy_funcs = {
            "provide_instruction": provide_instruction
        }

        # Execute the Assistant
        execute(user_proxy, thread, query, user_proxy_funcs)
