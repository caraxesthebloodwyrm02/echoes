"""Quick verification script"""
from realtime_preview import create_preview_system

print("Creating system...")
system = create_preview_system(mode="timeline", enable_security=False)

print("Starting system...")
if system.start():
    print("OK: System started")
else:
    print("FAIL: System start failed")
    exit(1)

print("Processing input...")
result = system.process_input(action="insert", position=0, text="Hello world")

if result.get("success"):
    print("OK: Input processed")
    print(f"  Direction: {result['trajectory']['current_direction']}")
    print(f"  Confidence: {result['trajectory']['confidence']:.2f}")
else:
    print("FAIL: Input processing failed")
    exit(1)

print("Getting state...")
state = system.get_full_state()
print(f"OK: Total events: {state['system']['total_events']}")

print("Stopping system...")
system.stop()
print("OK: System stopped")

print("\n=== ALL VERIFICATIONS PASSED ===")
