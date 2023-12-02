import asyncio
from openai import OpenAI
import pprint
import difflib
from IPython.display import display, HTML
client = OpenAI()

GPT_MODEL = "gpt-3.5-turbo-1106"

topic = "a journey to Mars"
system_message = "You are a helpful assistant that generates short stories."
user_request = f"Generate a short story about {topic}."


async def get_chat_response(system_message: str, user_request: str, seed: int = None):
    try:
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_request},
        ]

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages,
            seed=seed,
            max_tokens=200,
            temperature=0.7,
        )

        response_content = response["choices"][0]["message"]["content"]
        system_fingerprint = response["system_fingerprint"]
        prompt_tokens = response["usage"]["prompt_tokens"]
        completion_tokens = (
            response["usage"]["total_tokens"] -
            response["usage"]["prompt_tokens"]
        )

        table = f"""
        <table>
        <tr><th>Response</th><td>{response_content}</td></tr>
        <tr><th>System Fingerprint</th><td>{system_fingerprint}</td></tr>
        <tr><th>Number of prompt tokens</th><td>{prompt_tokens}</td></tr>
        <tr><th>Number of completion tokens</th><td>{completion_tokens}</td></tr>
        </table>
        """
        display(HTML(table))

        return response_content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# This function compares two responses and displays the differences in a table.
# Deletions are highlighted in red and additions are highlighted in green.
# If no differences are found, it prints "No differences found."


def compare_responses(previous_response: str, response: str):
    d = difflib.Differ()
    diff = d.compare(previous_response.splitlines(), response.splitlines())

    diff_table = "<table>"
    diff_exists = False

    for line in diff:
        if line.startswith("- "):
            diff_table += f"<tr style='color: red;'><td>{line}</td></tr>"
            diff_exists = True
        elif line.startswith("+ "):
            diff_table += f"<tr style='color: green;'><td>{line}</td></tr>"
            diff_exists = True
        else:
            diff_table += f"<tr><td>{line}</td></tr>"

    diff_table += "</table>"

    if diff_exists:
        display(HTML(diff_table))
    else:
        print("No differences found.")


async def main():
    previous_response = await get_chat_response(
        system_message=system_message, user_request=user_request
    )
    response = await get_chat_response(
        system_message=system_message, user_request=user_request
    )

# The function compare_responses is then called with the two responses as arguments.
# This function will compare the two responses and display the differences in a table.
# If no differences are found, it will print "No differences found."
    # compare_responses(previous_response, response)

# 非同期イベントループを使用してmain関数を実行
asyncio.run(main())
