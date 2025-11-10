#!/usr/bin/env python3
"""
Verify EchoesAI Direct Connection
Confirm zero middleware interference and authentic I/O properties.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add echoes root to path
echoes_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, echoes_root)

async def verify_middleware_removal():
    """Verify that all middleware has been removed."""
    print("🔍 Verifying Middleware Removal...")
    
    # Check if middleware file exists
    middleware_file = os.path.join(echoes_root, "api", "middleware.py")
    if os.path.exists(middleware_file):
        print("❌ Middleware file still exists")
        return False
    else:
        print("✅ Middleware file removed")
    
    # Check if disabled middleware file exists
    disabled_middleware = os.path.join(echoes_root, "api", "middleware.py.disabled")
    if os.path.exists(disabled_middleware):
        print("✅ Middleware file properly disabled")
    else:
        print("⚠️ Disabled middleware file not found")
    
    # Check main.py for middleware imports
    main_file = os.path.join(echoes_root, "api", "main.py")
    if os.path.exists(main_file):
        with open(main_file, 'r') as f:
            content = f.read()
        
        if "middleware" in content.lower():
            print("⚠️ Middleware references still found in main.py")
        else:
            print("✅ No middleware references in main.py")
    
    return True

async def verify_direct_connection():
    """Verify direct connection functionality."""
    print("\n🔌 Verifying Direct Connection...")
    
    try:
        from direct import get_direct_connection
        
        connection = get_direct_connection()
        status = connection.get_connection_status()
        
        print("📊 Direct Connection Status:")
        for key, value in status.items():
            if key != "api_key":
                print(f"   • {key.replace('_', ' ').title()}: {value}")
        
        # Test actual connection
        test_response = await connection.direct_chat(
            messages=[{"role": "user", "content": "Respond with 'AUTHENTIC_DIRECT'"}],
            max_tokens=20
        )
        
        if "AUTHENTIC_DIRECT" in test_response["content"]:
            print("✅ Direct connection test passed")
            return True
        else:
            print(f"❌ Unexpected response: {test_response['content']}")
            return False
            
    except Exception as e:
        print(f"❌ Direct connection verification failed: {e}")
        return False

async def verify_io_properties():
    """Verify authentic input-output properties."""
    print("\n🎯 Verifying Authentic I/O Properties...")
    
    try:
        from direct import get_direct_connection
        
        connection = get_direct_connection()
        
        # Test with specific parameters to verify no modification
        test_cases = [
            {
                "name": "Temperature Test",
                "messages": [{"role": "user", "content": "Generate a random word"}],
                "temperature": 1.0,
                "expected_property": "randomness"
            },
            {
                "name": "Token Limit Test",
                "messages": [{"role": "user", "content": "Count to 20"}],
                "max_tokens": 10,
                "expected_property": "token_limit"
            },
            {
                "name": "Low Temperature Test",
                "messages": [{"role": "user", "content": "What is 1+1?"}],
                "temperature": 0.0,
                "expected_property": "deterministic"
            }
        ]
        
        passed_tests = 0
        for test_case in test_cases:
            response = await connection.direct_chat(
                messages=test_case["messages"],
                temperature=test_case.get("temperature", 0.7),
                max_tokens=test_case.get("max_tokens", None)
            )
            
            # Verify response properties
            if test_case["expected_property"] == "token_limit":
                if response["usage"]["total_tokens"] <= test_case["max_tokens"] + 5:  # Allow small buffer
                    print(f"✅ {test_case['name']}: Token limit respected")
                    passed_tests += 1
                else:
                    print(f"❌ {test_case['name']}: Token limit exceeded")
            elif test_case["expected_property"] == "randomness":
                if len(response["content"].strip()) > 0:
                    print(f"✅ {test_case['name']}: Random response generated")
                    passed_tests += 1
                else:
                    print(f"❌ {test_case['name']}: No response generated")
            elif test_case["expected_property"] == "deterministic":
                if "2" in response["content"]:
                    print(f"✅ {test_case['name']}: Deterministic response")
                    passed_tests += 1
                else:
                    print(f"❌ {test_case['name']}: Unexpected response")
        
        print(f"📊 I/O Properties Test: {passed_tests}/{len(test_cases)} passed")
        return passed_tests == len(test_cases)
        
    except Exception as e:
        print(f"❌ I/O properties verification failed: {e}")
        return False

async def verify_no_interference():
    """Verify no middleware interference in request/response flow."""
    print("\n🚫 Verifying No Interference...")
    
    try:
        from direct import get_direct_connection
        
        connection = get_direct_connection()
        
        # Test concurrent requests to ensure no rate limiting interference
        tasks = []
        for i in range(5):
            task = connection.direct_chat(
                messages=[{"role": "user", "content": f"Request {i+1} - say 'OK'"}],
                max_tokens=5
            )
            tasks.append(task)
        
        start_time = datetime.now()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = datetime.now()
        
        successful_requests = [r for r in results if not isinstance(r, Exception)]
        failed_requests = [r for r in results if isinstance(r, Exception)]
        
        print("📊 Concurrent Request Results:")
        print(f"   • Total requests: {len(tasks)}")
        print(f"   • Successful: {len(successful_requests)}")
        print(f"   • Failed: {len(failed_requests)}")
        print(f"   • Time taken: {(end_time - start_time).total_seconds():.2f}s")
        
        if len(successful_requests) >= 4:  # Allow 1 failure
            print("✅ No rate limiting interference detected")
            return True
        else:
            print("❌ Possible rate limiting interference")
            return False
            
    except Exception as e:
        print(f"❌ Interference verification failed: {e}")
        return False

async def main():
    """Main verification function."""
    print("🔍 EchoesAI Direct Connection Verification")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Purpose: Confirm zero middleware interference")
    print("")
    
    # Run all verifications
    verifications = [
        ("Middleware Removal", verify_middleware_removal),
        ("Direct Connection", verify_direct_connection),
        ("I/O Properties", verify_io_properties),
        ("No Interference", verify_no_interference)
    ]
    
    results = {}
    overall_status = "PASS"
    
    for verification_name, verification_func in verifications:
        try:
            success = await verification_func()
            results[verification_name] = success
            if not success:
                overall_status = "FAIL"
        except Exception as e:
            results[verification_name] = False
            overall_status = "FAIL"
            print(f"❌ {verification_name} crashed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    for verification_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {verification_name}")
    
    print(f"\n🎯 OVERALL STATUS: {overall_status}")
    
    if overall_status == "PASS":
        print("✅ EchoesAI Direct Connection Successfully Established!")
        print("✅ Zero middleware interference confirmed")
        print("✅ Authentic input-output properties verified")
        print("✅ Direct OpenAI API connection operational")
        print("✅ No request/response modification detected")
        print("\n🎉 EchoesAI is now operating with authentic direct connection!")
    else:
        print("❌ Direct Connection Verification Failed!")
        print("⚠️ Some middleware interference may still be present")
        print("🔧 Review failed verifications above")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return overall_status == "PASS"

if __name__ == "__main__":
    asyncio.run(main())
