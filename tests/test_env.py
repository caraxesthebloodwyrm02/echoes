import os
from agent_dotenv import load_dotenv

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
if key:
    print(f"✅ API key loaded: {key[:15]}...{key[-4:]}")
    print(f"   Length: {len(key)} characters")
else:
    print("❌ No API key found in environment")
