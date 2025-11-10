# responses_quickstart.py
# Requirements: pip install openai
import json
from datetime import datetime, timezone

from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from env

MODEL = "gpt-4o"  # Powerful, general-purpose model
GUIDELINE_PROMPT = (
    "You are an assistant. Before answering, if the user's request is ambiguous, "
    "ask one concise clarifying question. If you need external data, output a single "
    "line starting with TOOL_CALL: followed by one JSON object, e.g. "
    'TOOL_CALL: {"tool":"get_time","args":{}}. Otherwise reply concisely.'
)

user_query = "What's the local time in Dhaka and a 2-line summary of the weather?"

# 1) Initial call
resp = client.responses.create(
    model=MODEL, input=f"USER: {user_query}\n\n{GUIDELINE_PROMPT}"
)

# 2) Read model text safely
text = getattr(resp, "output_text", None)
if not text:
    # defensive fallback for other response shapes
    try:
        text = resp.output[0].content[0].text
    except Exception:
        text = str(resp)

print("MODEL SAYS:\n", text)

# 3) Detect tool call pattern and handle locally
if "TOOL_CALL:" in text:
    payload = text.split("TOOL_CALL:", 1)[1].strip()
    tool_req = json.loads(payload)

    # Example local tool handler: get_time
    if tool_req.get("tool") == "get_time":
        result_value = datetime.now(timezone.utc).astimezone().isoformat()
    else:
        result_value = {"error": "unknown tool"}

    # 4) Feed the tool result back to the model and ask it to continue
    followup = client.responses.create(
        model=MODEL,
        input=f"TOOL_RESULT: {json.dumps(result_value)}\nPlease continue and finish the user's answer.",
    )
    final = getattr(followup, "output_text", str(followup))
    print("FINAL ANSWER:\n", final)
