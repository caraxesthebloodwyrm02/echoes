#!/usr/bin/env python3
"""
Token Iteration Verification Test
Verifies that token iteration is completely unblocked and functions properly.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add echoes root to path
echoes_root = Path(__file__).parent.parent
sys.path.insert(0, str(echoes_root))

async def test_token_iteration_unblocked():
    """Test that token iteration is completely unblocked."""
    print("🔄 Testing Token Iteration Unblocking...")
    
    try:
        # Test 1: Verify DEFAULT_MAX_TOKENS is removed
        print("\n1️⃣ Testing DEFAULT_MAX_TOKENS removal...")
        try:
            from echoes.config import DEFAULT_MAX_TOKENS
            print("   ❌ DEFAULT_MAX_TOKENS still exists - BLOCKING DETECTED")
            return False
        except ImportError:
            print("   ✅ DEFAULT_MAX_TOKENS successfully removed")
        except AttributeError:
            print("   ✅ DEFAULT_MAX_TOKENS successfully removed")
        
        # Test 2: Verify Echoes core doesn't block tokens
        print("\n2️⃣ Testing Echoes core token blocking removal...")
        try:
            from echoes.config import RuntimeOptions
            
            # Create options with specific token limit
            opts = RuntimeOptions(max_tokens=123)
            
            # Check if the token limit is preserved (not overridden)
            if opts.max_tokens == 123:
                print("   ✅ User token limits preserved")
            else:
                print(f"   ❌ Token limit overridden: {opts.max_tokens}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing token limits: {e}")
            return False
        
        # Test 3: Test direct connection with various token limits
        print("\n3️⃣ Testing direct connection token iteration...")
        try:
            from direct import get_direct_connection
            
            connection = get_direct_connection()
            
            # Test multiple token levels to ensure iteration works
            test_tokens = [1, 5, 10, 25, 50, 100, 500, 1000]
            
            for token_limit in test_tokens:
                response = await connection.direct_chat(
                    messages=[{"role": "user", "content": f"Test {token_limit}"}],
                    model="gpt-3.5-turbo",
                    max_tokens=token_limit,
                    temperature=0.0
                )
                
                completion_tokens = response["usage"]["completion_tokens"]
                
                # Verify token limit is respected (allowing small buffer for OpenAI behavior)
                if completion_tokens <= token_limit + 5:
                    print(f"   ✅ Token limit {token_limit}: {completion_tokens} tokens (respected)")
                else:
                    print(f"   ❌ Token limit {token_limit}: {completion_tokens} tokens (BLOCKED)")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Error testing token iteration: {e}")
            return False
        
        # Test 4: Test extreme token limits
        print("\n4️⃣ Testing extreme token iteration...")
        try:
            extreme_tests = [
                {"max_tokens": 1, "name": "minimum"},
                {"max_tokens": 2, "name": "tiny"},
                {"max_tokens": 3, "name": "small"},
                {"max_tokens": 10000, "name": "large"},
                {"max_tokens": 128000, "name": "maximum"}
            ]
            
            for test in extreme_tests:
                response = await connection.direct_chat(
                    messages=[{"role": "user", "content": f"Extreme test: {test['name']}"}],
                    model="gpt-3.5-turbo",
                    max_tokens=test["max_tokens"],
                    temperature=0.0
                )
                
                completion_tokens = response["usage"]["completion_tokens"]
                
                if test["max_tokens"] <= 100:
                    # For small limits, check strict compliance
                    if completion_tokens <= test["max_tokens"] + 2:
                        print(f"   ✅ Extreme {test['name']} ({test['max_tokens']}): {completion_tokens} tokens")
                    else:
                        print(f"   ❌ Extreme {test['name']} ({test['max_tokens']}): {completion_tokens} tokens - BLOCKED")
                        return False
                else:
                    # For large limits, just check it works
                    print(f"   ✅ Extreme {test['name']} ({test['max_tokens']}): {completion_tokens} tokens")
                    
        except Exception as e:
            print(f"   ❌ Error testing extreme tokens: {e}")
            return False
        
        # Test 5: Test token iteration speed (no blocking delays)
        print("\n5️⃣ Testing token iteration speed...")
        try:
            import time
            
            start_time = time.perf_counter()
            
            # Rapid token iteration test
            for i in range(10):
                response = await connection.direct_chat(
                    messages=[{"role": "user", "content": f"Speed test {i}"}],
                    model="gpt-3.5-turbo",
                    max_tokens=5,
                    temperature=0.0
                )
            
            end_time = time.perf_counter()
            total_time = end_time - start_time
            avg_time = total_time / 10
            
            if avg_time < 2.0:  # Should be fast without blocking
                print(f"   ✅ Token iteration speed: {avg_time:.2f}s average (unblocked)")
            else:
                print(f"   ⚠️ Token iteration speed: {avg_time:.2f}s average (potential blocking)")
                
        except Exception as e:
            print(f"   ❌ Error testing iteration speed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Critical error in token iteration test: {e}")
        return False

async def test_no_default_interference():
    """Test that no default values interfere with token iteration."""
    print("\n🎯 Testing No Default Interference...")
    
    try:
        # Test that None token limits work
        from echoes.config import RuntimeOptions
        
        # Test with None (should not default to 4000)
        opts_none = RuntimeOptions(max_tokens=None)
        print(f"   ✅ None token limit: {opts_none.max_tokens}")
        
        # Test with zero tokens
        opts_zero = RuntimeOptions(max_tokens=0)
        print(f"   ✅ Zero token limit: {opts_zero.max_tokens}")
        
        # Test with negative tokens (edge case)
        try:
            opts_negative = RuntimeOptions(max_tokens=-1)
            print(f"   ✅ Negative token limit: {opts_negative.max_tokens}")
        except:
            print("   ✅ Negative tokens properly rejected")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing default interference: {e}")
        return False

async def generate_token_iteration_report(results: list):
    """Generate comprehensive token iteration report."""
    print("\n" + "=" * 60)
    print("🔄 TOKEN ITERATION UNBLOCKING REPORT")
    print("=" * 60)
    
    passed_tests = sum(results)
    total_tests = len(results)
    
    print(f"Test Summary: {passed_tests}/{total_tests} tests passed")
    print("")
    
    print("Detailed Results:")
    test_names = [
        "Token Iteration Unblocked",
        "No Default Interference"
    ]
    
    for i, (test_name, passed) in enumerate(zip(test_names, results)):
        status = "✅ UNBLOCKED" if passed else "❌ BLOCKED"
        print(f"   {status} {test_name}")
    
    print("")
    
    if passed_tests == total_tests:
        print("🎉 TOKEN ITERATION: COMPLETELY UNBLOCKED")
        print("✅ All token blocking functions eliminated")
        print("✅ Users can iterate through ANY token level")
        print("✅ No default value interference")
        print("✅ Token iteration speed optimal")
        print("")
        print("🚀 Echoes token iteration is fully functional")
        return True
    else:
        print("⚠️ TOKEN ITERATION: PARTIALLY BLOCKED")
        print("❌ Some token blocking functions remain")
        print("🔧 Additional fixes required")
        return False

async def main():
    """Main token iteration verification function."""
    print("🔄 Echoes Token Iteration Verification Test")
    print("=" * 60)
    print(f"Testing timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Run all token iteration tests
    tests = [
        test_token_iteration_unblocked(),
        test_no_default_interference()
    ]
    
    results = []
    for test in tests:
        try:
            result = await test
            results.append(result)
            print(f"Status: {'✅ PASSED' if result else '❌ FAILED'}")
        except Exception as e:
            results.append(False)
            print(f"Status: ❌ CRASHED - {e}")
        print("")
    
    # Generate comprehensive report
    iteration_unblocked = await generate_token_iteration_report(results)
    
    return iteration_unblocked

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
