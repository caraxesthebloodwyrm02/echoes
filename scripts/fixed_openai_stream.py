import os
from openai import OpenAI
from typing import AsyncGenerator, Dict, Any
import json

# Initialize the OpenAI client with API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

client = OpenAI(api_key=api_key)

async def stream_openai_response(messages: list, model: str = "gpt-4") -> AsyncGenerator[Dict[str, Any], None]:
    """
    Stream responses from OpenAI's chat completion API.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: The model to use for completion
        
    Yields:
        Dictionary containing the response data
    """
    try:
        # Make the API call with streaming enabled
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            temperature=0.7,
        )
        
        # Process the stream
        full_response = ""
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content is not None:
                    content = delta.content
                    full_response += content
                    yield {
                        "type": "content",
                        "content": content,
                        "full_response": full_response
                    }
                
    except Exception as e:
        yield {
            "type": "error",
            "error": str(e)
        }

# Example usage
async def main():
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about artificial intelligence."}
    ]
    
    print("Starting stream...")
    async for chunk in stream_openai_response(messages):
        if chunk["type"] == "content":
            print(chunk["content"], end="", flush=True)
        elif chunk["type"] == "error":
            print(f"\nError: {chunk['error']}")
            break

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
