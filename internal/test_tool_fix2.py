#!/usr/bin/env python3
"""Quick test to verify tool schema fix"""

from assistant_v2_core import EchoesAssistantV2

print("Testing tool schema fix...")

# Initialize assistant
assistant = EchoesAssistantV2(enable_rag=False, enable_streaming=False)

# Test calculator tool
response = assistant.chat("Calculate 25 * 4")
print(f"Response length: {len(response)}")
print(f"Response repr: {repr(response)}")
print(f"Response contains 100: {'100' in response}")
