#!/usr/bin/env python3
"""
Test script to verify smart terminal and assistant interaction.
"""
import asyncio
import sys
from pathlib import Path
from typing import Any, List, Optional, Tuple

# Add project root to path
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class TestSmartTerminal:
    """Test suite for Smart Terminal functionality."""
    
    def __init__(self) -> None:
        """Initialize test environment."""
        self.predictor: Optional[Any] = None
        self.feedback: Optional[Any] = None
        self.terminal: Optional[Any] = None
    
    async def setup(self) -> bool:
        """Set up the test environment."""
        try:
            from smart_terminal.core.feedback import FeedbackHandler
            from smart_terminal.core.predictor import CommandPredictor
            from smart_terminal.interface.terminal import TerminalInterface
            
            self.predictor = CommandPredictor()
            self.feedback = FeedbackHandler()
            self.terminal = TerminalInterface(self.predictor, self.feedback)
            return True
        except ImportError as e:
            print(f"❌ Import error: {e}")
            return False
        except Exception as e:  # pylint: disable=broad-except
            print(f"❌ Setup failed: {e}")
            return False
    
    async def test_command_prediction(self) -> bool:
        """Test command prediction functionality."""
        if not self.predictor:
            return False
            
        test_commands = [
            "git status",
            "python -m pip install",
            "ls -la"
        ]
        
        try:
            for cmd in test_commands:
                self.predictor.update_command(cmd)
                
            # Test prediction
            suggestions = self.predictor.get_suggestions("git")
            if not isinstance(suggestions, list):
                print("❌ Suggestions should be a list")
                return False
                
            print(f"\nSuggestions for 'git': {suggestions[:3]}...")
            return True
            
        except Exception as e:  # pylint: disable=broad-except
            print(f"❌ Command prediction test failed: {e}")
            return False

async def test_smart_terminal() -> bool:
    """Test smart terminal functionality."""
    print("\n=== Testing Smart Terminal ===")
    tester = TestSmartTerminal()
    
    # Setup test environment
    if not await tester.setup():
        print("❌ Failed to setup test environment")
        return False
        
    # Run tests
    if await tester.test_command_prediction():
        print("✅ Command prediction test passed")
        return True
    
    return False

async def test_assistant() -> bool:
    """Test assistant functionality."""
    print("\n=== Testing Assistant ===")
    try:
        # Import only what's needed
        from assistant import \
            Assistant  # pylint: disable=import-outside-toplevel
        print("✅ Assistant imports successful")
        
        # Initialize assistant
        assistant = Assistant()
        response = await assistant.process("Hello, can you help me?")
        
        if not response or not isinstance(response, str):
            print("❌ Invalid response from assistant")
            return False
            
        print(f"✅ Assistant response: {response[:100]}...")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import assistant: {e}")
        return False
    except Exception as e:  # pylint: disable=broad-except
        print(f"❌ Assistant test failed: {e}")
        return False

async def test_integration() -> bool:
    """Test integration between smart terminal and assistant."""
    print("\n=== Testing Integration ===")
    print("ℹ️  No integration tests implemented yet")
    return True

async def run_tests() -> int:
    """Run all tests and return exit code."""
    tests: List[Tuple[str, Any]] = [
        ("Smart Terminal", test_smart_terminal()),
        ("Assistant", test_assistant()),
        ("Integration", test_integration())
    ]
    
    results: List[Tuple[str, bool]] = []
    for name, test_coro in tests:
        print(f"\n--- Running {name} Tests ---")
        success = await test_coro
        results.append((name, success))
        status = "PASSED" if success else "FAILED"
        print(f"\n--- {name} Tests {status} ---")
    
    # Print summary
    print("\n=== Test Summary ===")
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name}: {status}")
    
    # Return non-zero exit code if any test failed
    return 0 if all(success for _, success in results) else 1

def main() -> int:
    """Main entry point."""
    try:
        return asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:  # pylint: disable=broad-except
        print(f"\nUnexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
                if result:
                    print(result.output)
            except Exception as e:
                print(f"Command '{cmd}' failed: {e}")
        
        print("\n✅ Assistant basic tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Assistant test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Test integration between smart terminal and assistant."""
    print("\n=== Testing Integration ===")
    try:
        from assistant import FusedAssistant
        from smart_terminal.core.predictor import CommandPredictor

        # Initialize both components
        assistant = FusedAssistant()
        predictor = CommandPredictor()
        
        # Test if assistant can use smart terminal's predictor
        if hasattr(assistant, 'smart_predictor'):
            print("✅ Assistant has smart_predictor")
            
            # Test command prediction through assistant
            test_cmd = "git "
            suggestions = assistant.smart_predictor.get_suggestions(test_cmd)
            print(f"\nAssistant's smart terminal suggestions for '{test_cmd}':")
            for i, suggestion in enumerate(suggestions[:3], 1):
                print(f"  {i}. {suggestion}")
        else:
            print("⚠️  Assistant doesn't have smart_predictor (SMART_TERMINAL_AVAILABLE might be False)")
        
        print("\n✅ Integration tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=== Starting Smart Terminal & Assistant Integration Tests ===\n")
    
    # Run individual tests
    smart_terminal_ok = test_smart_terminal()
    assistant_ok = test_assistant()
    integration_ok = test_integration()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Smart Terminal: {'✅' if smart_terminal_ok else '❌'}")
    print(f"Assistant: {'✅' if assistant_ok else '❌'}")
    print(f"Integration: {'✅' if integration_ok else '❌'}")
    
    if all([smart_terminal_ok, assistant_ok, integration_ok]):
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
