#!/usr/bin/env python3
"""Quick test script for assistant system_stats command."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

try:
    from assistant import FusedAssistant

    assistant = FusedAssistant()
    print("Assistant initialized successfully")

    # Test the method directly first
    try:
        result = assistant._get_system_stats()
        print("_get_system_stats() works directly")
        print("Result type:", type(result))
        print(
            "Result keys:",
            list(result.keys()) if isinstance(result, dict) else "Not a dict",
        )
    except Exception as e:
        print("_get_system_stats() failed directly:", str(e))
        import traceback

        traceback.print_exc()

    # Debug the realtime_monitor initialization
    if hasattr(assistant, "realtime_monitor"):
        print("realtime_monitor exists:", assistant.realtime_monitor)
        print("realtime_monitor type:", type(assistant.realtime_monitor))
        try:
            # Test the monitor directly
            monitor_result = assistant.realtime_monitor.get_system_stats()
            print("Monitor works directly, keys:", list(monitor_result.keys()))
        except Exception as e:
            print("Monitor failed directly:", str(e))
            import traceback

            traceback.print_exc()
    else:
        print("realtime_monitor attribute does not exist")

    # Debug the tool mapping
    if (
        "realtime_operations" in assistant.tools
        and "system_stats" in assistant.tools["realtime_operations"]
    ):
        tool_func = assistant.tools["realtime_operations"]["system_stats"]
        print("system_stats tool function:", tool_func)
        print(
            "Function name:",
            tool_func.__name__ if hasattr(tool_func, "__name__") else "No name",
        )
        print(
            "Function qualname:",
            tool_func.__qualname__
            if hasattr(tool_func, "__qualname__")
            else "No qualname",
        )
    else:
        print("system_stats tool not found in realtime_operations")

    # Now test through command execution
    result = assistant.execute_command("system_stats")
    print("Command execution - Success:", result.success)
    if result.success:
        print("Output:", result.output[:500])
    else:
        print("Error:", result.error)
        print("Attention filtered:", getattr(result, "attention_filtered", False))
        print("Attention score:", getattr(result, "attention_score", 0))

except Exception as e:
    import traceback

    print("Error:", str(e))
    traceback.print_exc()
