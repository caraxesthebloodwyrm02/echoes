#!/usr/bin/env python3
"""Quick test to verify tool schema fix"""

from assistant_v2_core import EchoesAssistantV2

print("Testing tool schema fix...")

# Initialize assistant
assistant = EchoesAssistantV2(enable_rag=False)

# Test calculator tool
response = assistant.chat("Calculate 25 * 4")
print(f"Calculator response: {response}")

# Test if it contains the result
if "100" in response:
    print("[OK] Tool calling works!")
else:
    print("[FAIL] Tool calling failed")
    print(f"Response was: {response}")
