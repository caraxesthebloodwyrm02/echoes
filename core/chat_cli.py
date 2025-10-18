#!/usr/bin/env python3
"""
OpenAI 4‑family chat CLI – **streamed** replies (like ai_chat.py)

* Uses the new OpenAI SDK (>=1.0.0)
* Loads OPENAI_API_KEY (and optional OPENAI_PROJECT_ID) from `.env`
* Default model = gpt‑4o, temperature = 1.0
* Switch model on‑the‑fly with “--<model>” or with /model <name>
* Allowed models: gpt‑4o, gpt‑4o‑mini, gpt‑4o‑1‑mini, gpt‑3.5‑turbo
* Commands: /help, /list, /reset, /clear, /quit
* Replies are streamed live – you see the text as GPT produces it.
"""

import os
import sys
import signal
from typing import List, Dict

# --------------------------------------------------------------------------- #
# 1. Load .env – opens up both user and project keys
# --------------------------------------------------------------------------- #
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)            # respects .env even if already in env
except Exception as exc:                 # pragma: no cover
    print(f"[ERROR] Could not load .env: {exc}")
    sys.exit(1)

# --------------------------------------------------------------------------- #
# 2. OpenAI SDK (new interface)
# --------------------------------------------------------------------------- #
try:
    from openai import OpenAI, OpenAIError
except Exception as exc:                 # pragma: no cover
    print(f"[ERROR] openai library missing: {exc}")
    print("Install with: pip install openai")
    sys.exit(1)

# --------------------------------------------------------------------------- #
# 3. API key & optional project ID
# --------------------------------------------------------------------------- #
API_KEY = os.getenv("OPENAI_API_KEY")
PROJECT_ID = os.getenv("OPENAI_PROJECT_ID")   # None if you’re not using a project key

if not API_KEY:
    print("[ERROR] No OPENAI_API_KEY found in environment.")
    print("Create a .env file with: OPENAI_API_KEY=sk‑…")
    sys.exit(1)

# Create a client – pass project when present
client = OpenAI(api_key=API_KEY, project=PROJECT_ID if PROJECT_ID else None)

# --------------------------------------------------------------------------- #
# 4. State
# --------------------------------------------------------------------------- #
current_model: str = "gpt-4o"
temperature: float = 1.0

conversation: List[Dict[str, str]] = []

ALLOWED_MODELS = {
    "gpt-4o":          "⚡️ Gpt‑4o (default)",
    "gpt-4o-mini":     "🚀 Gpt‑4o‑mini (smaller, cheaper)",
    "gpt-4o-1-mini":   "📦 Gpt‑4o‑1‑mini (tiny, still good)",
    "gpt-3.5-turbo":   "🤖 Gpt‑3.5‑turbo (classic, inexpensive)",
}

# --------------------------------------------------------------------------- #
# 5. Helpers
# --------------------------------------------------------------------------- #
def clear_screen() -> None:  # pragma: no cover (terminal dependent)
    os.system("cls" if os.name == "nt" else "clear")

def banner() -> None:
    clear_screen()
    print("=== OpenAI 4‑family Chat CLI ===")
    print(f"Model      : {current_model}")
    print(f"Temperature: {temperature:.2f}")
    print("Type '/help' for commands. Press Ctrl‑D to exit.\n")

def list_models() -> None:
    """Print all models we can try out."""
    try:
        res = client.models.list()
        print("\nAllowed models:")
        for m in res.data:
            desc = ALLOWED_MODELS.get(m.id, "(unknown)")
            print(f"  - {m.id:15} {desc}")
        print()
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] Cannot list models: {exc}")

def switch_model(name: str) -> None:
    """Attempt to set a new model."""
    global current_model
    name = name.lower()
    if name not in ALLOWED_MODELS:
        print(f"[ERROR] '{name}' not in allowed list. Use /list to see options.")
        return
    try:
        client.models.retrieve(name)          # quick check – throws if the model is unreachable
        current_model = name
        print(f"[INFO] Switched to {name} ({ALLOWED_MODELS[name]})")
    except Exception as exc:  # pragma: no cover
        print(f"[ERROR] Cannot switch to '{name}': {exc}")

def set_temperature(tok: str) -> None:
    """Set the temperature (0‑2)."""
    global temperature
    try:
        v = float(tok)
        if 0.0 <= v <= 2.0:
            temperature = v
            print(f"[INFO] Temperature set to {temperature:.2f}")
        else:
            print("[ERROR] Temperature must be between 0.0 and 2.0")
    except ValueError:
        print("[ERROR] Provide a numeric temperature (e.g., /temp 1.2)")

def reset_conversation() -> None:
    """Clear chat history."""
    global conversation
    conversation.clear()
    print("[INFO] Conversation history cleared.")

def help_msg() -> None:
    print(
        """
Commands (start with a slash /):
  /help          Show this help
  /list          Show allowed models
  /model <name>  Switch to <name>
  /temp <value>  Set temperature (0.0‑2.0)
  /reset         Clear conversation history
  /clear         Clear screen
  /quit          Exit program
"""
    )

def parse_prompt(prompt: str) -> tuple[str, str]:
    """
    Return (prompt_text, model_override).
    If user appended ' --modelname', the override is returned; otherwise ''.
    """
    if " --" in prompt:
        text, mdl = prompt.rsplit(" --", 1)
        return text.strip(), mdl.strip()
    return prompt.strip(), ""

# --------------------------------------------------------------------------- #
# 6. Signal handling
# --------------------------------------------------------------------------- #
def handle_sigint(signum: int, frame) -> None:  # pragma: no cover
    print("\n[INFO] Interrupt received. Exiting.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

# --------------------------------------------------------------------------- #
# 7. Chat loop
# --------------------------------------------------------------------------- #
def chat_loop() -> None:
    banner()
    while True:
        try:
            raw = input("You: ").strip()
        except EOFError:  # Ctrl‑D
            print("\n[INFO] EOF received. Exiting.")
            break

        if not raw:
            continue

        # -------- Slash commands --------
        if raw.startswith("/"):
            cmd, *rest = raw.split(maxsplit=1)
            arg = rest[0] if rest else ""
            cmd = cmd.lower()

            if cmd in ("/help", "/h"):
                help_msg()
            elif cmd in ("/list", "/models"):
                list_models()
            elif cmd in ("/model", "/m"):
                if arg:
                    switch_model(arg)
                else:
                    print("[ERROR] Usage: /model <name>")
            elif cmd in ("/temp", "/t"):
                if arg:
                    set_temperature(arg)
                else:
                    print("[ERROR] Usage: /temp <value>")
            elif cmd in ("/reset", "/r"):
                reset_conversation()
            elif cmd in ("/clear", "/c"):
                banner()
            elif cmd in ("/quit", "/exit", "/q"):
                print("[INFO] Goodbye!")
                break
            else:
                print(f"[ERROR] Unknown command '{cmd}'. Type /help.")
            continue

        # -------- Normal chat --------
        prompt, model_override = parse_prompt(raw)
        if model_override:
            switch_model(model_override)

        if not prompt:
            continue

        conversation.append({"role": "user", "content": prompt})

        # ---- API call ----
        try:
            resp = client.chat.completions.create(
                model=current_model,
                messages=conversation,
                temperature=temperature,
                stream=True,   # stream reply live
            )

            full_text = ""
            for chunk in resp:                 # each chunk is a ChatCompletionChunk
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
                    full_text += content

            print("\n")  # newline after the stream ends
            conversation.append({"role": "assistant", "content": full_text.strip()})
        except OpenAIError as exc:  # pragma: no cover
            print(f"\n[ERROR] OpenAI API error: {exc}")
        except Exception as exc:  # pragma: no cover
            print(f"\n[ERROR] Unexpected error: {exc}")

if __name__ == "__main__":
    chat_loop()
