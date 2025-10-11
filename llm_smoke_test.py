import os

from prompting.core.llm_client import LLMClient


def main() -> None:
    provider = os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    print(f"Provider={provider} Model={model}")

    prompt = (
        "Return a compact JSON object with exactly these keys: "
        '{"summary":"ok","solution":"- step 1","code_suggestion":"print(\\"hi\\")","next_steps":"done"}'
    )

    try:
        client = LLMClient()
        raw = client.complete(prompt)
        print("RAW (first 200 chars):", raw[:200].replace("\n", " "))
        parsed = client.parse_json_response(raw)
        print("PARSED:", parsed)
    except Exception as e:
        print("ERROR:", e)


if __name__ == "__main__":
    main()
