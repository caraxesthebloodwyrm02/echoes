import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load .env from the repo root
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_user_data",
            "description": "Get user data by ID.",
            "parameters": {
                "type": "object",
                "properties": {"user_id": {"type": "integer"}},
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_report",
            "description": "Generate a summary report from user data.",
            "parameters": {
                "type": "object",
                "properties": {"user_info": {"type": "object"}},
                "required": ["user_info"],
            },
        },
    },
]

# Function implementations
def fetch_user_data(user_id: int) -> dict:
    # In a real app, call your DB or API
    return {"id": user_id, "name": "Alice", "activity": ["coding", "reading"]}


def generate_report(user_info: dict) -> str:
    act = ", ".join(user_info["activity"])
    return f"User {user_info['name']} is active in {act}."


FUNCTIONS = {
    "fetch_user_data": fetch_user_data,
    "generate_report": generate_report,
}


def run_cascade():
    messages = [{"role": "user", "content": "Generate a report for user 42"}]

    # 1️⃣ First call
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
    )
    tool_call = resp.choices[0].message.tool_calls[0]
    func = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    print(f"[Cascade 1] Calling {func} with {args}")
    result = FUNCTIONS[func](**args)

    # 2️⃣ Feed back to the model
    messages.append(resp.choices[0].message)  # assistant message with tool call
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result),
        }
    )

    # 3️⃣ Second call
    resp2 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
    )
    if getattr(resp2.choices[0].message, "tool_calls", []):
        tc = resp2.choices[0].message.tool_calls[0]
        print(f"[Cascade 2] Calling {tc.function.name}")
        # Pass the user info from the first function call
        args = json.loads(tc.function.arguments)
        if tc.function.name == "generate_report":
            args["user_info"] = result
        r2 = FUNCTIONS[tc.function.name](**args)
        print("Final result:", r2)
    else:
        print("Final message:", resp2.choices[0].message.content)


if __name__ == "__main__":
    run_cascade()
