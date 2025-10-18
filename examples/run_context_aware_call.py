import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.realtime_preview import create_glimpse
from core.context_aware_api import ContextAwareAPICall

def main():
    """Demonstrates a context-aware API call."""
    print("--- Initializing Glimpse System ---")
    glimpse_system = create_glimpse(enable_security=False, enable_guardrails=False)
    glimpse_system.start()

    print("\n--- Simulating User Activity ---")
    glimpse_system.process_input("insert", position=0, text="def hello():\n    print('Hello, world!')")
    glimpse_system.process_input("replace", start=23, end=28, text="Glimpse")
    print("Trajectory now contains some activity.")

    print("\n--- Initializing Context-Aware API Call Handler ---")
    context_api = ContextAwareAPICall(glimpse_system)

    print("\n--- Running Query Requiring Codebase Awareness ---")
    user_query = "What is the purpose of the GuardrailMiddleware class? Summarize it for me."
    context_api.run(user_query)

if __name__ == "__main__":
    main()
