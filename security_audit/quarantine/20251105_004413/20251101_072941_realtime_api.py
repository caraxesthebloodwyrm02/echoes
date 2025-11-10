import os

import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_realtime():
    print("[INFO] Starting streaming chat...")

    # Using the chat completions API with streaming
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL") or "gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me a short story about AI assistants."},
        ],
        stream=True,
    )

    print("Assistant: ", end="", flush=True)
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n[INFO] Stream complete.")


if __name__ == "__main__":
    run_realtime()
