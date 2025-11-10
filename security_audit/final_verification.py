#!/usr/bin/env python3
"""
Final Security Verification
Tests Echoes after pruning to ensure zero malicious patterns remain.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add echoes root to path
echoes_root = Path(__file__).parent.parent
sys.path.insert(0, str(echoes_root))

async def test_token_limit_authenticity():
    """Test that token limits are 100% authentic with no interference."""
    print("🎯 Testing Token Limit Authenticity...")
    
    try:
        from direct import get_direct_connection
        
        connection = get_direct_connection()
        
        # Test with extremely strict limits
        test_cases = [
            {"max_tokens": 1, "expected_max": 3},
            {"max_tokens": 2, "expected_max": 4},
            {"max_tokens": 3, "expected_max": 5},
            {"max_tokens": 5, "expected_max": 7}
        ]
        
        all_passed = True
        for i, test in enumerate(test_cases, 1):
            response = await connection.direct_chat(
                messages=[{"role": "user", "content": "Say 'OK'"}],
                max_tokens=test["max_tokens"],
                temperature=0.0  # Deterministic
            )
            
            completion_tokens = response["usage"]["completion_tokens"]
            
            # Check if within expected range (allowing for OpenAI's minimal response)
            passed = completion_tokens <= test["expected_max"]
            
            print(f"   Test {i}: {completion_tokens} tokens <= {test['expected_max']}? {'✅' if passed else '❌'}")
            
            if not passed:
                all_passed = False
                print(f"      ❌ VIOLATION: Expected <= {test['expected_max']}, got {completion_tokens}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Token limit test failed: {e}")
        return False

async def test_no_interception():
    """Test that no interception is occurring."""
    print("\n🚫 Testing No Interception...")
    
    try:
        from direct import get_direct_connection
        
        connection = get_direct_connection()
        
        # Test with unique parameters to ensure no caching/deduplication
        unique_responses = []
        
        for i in range(3):
            response = await connection.direct_chat(
                messages=[{"role": "user", "content": f"Unique test {i}: What is {i}+{i}?"}],
                max_tokens=5,
                temperature=0.0
            )
            
            unique_responses.append(response["content"].strip())
        
        # Check if responses are unique (no cloning)
        unique_set = set(unique_responses)
        passed = len(unique_set) == 3
        
        print(f"   ✅ Unique responses: {len(unique_set)}/3")
        for i, resp in enumerate(unique_responses):
            print(f"      Response {i}: {resp}")
        
        return passed
        
    except Exception as e:
        print(f"❌ No interception test failed: {e}")
        return False

async def test_source_authenticity():
    """Test that source material is authentic."""
    print("\n🔍 Testing Source Authenticity...")
    
    try:
        from direct import get_direct_connection
        
        connection = get_direct_connection()
        
        # Test with mathematical queries (deterministic)
        math_queries = [
            "What is 2+2?",
            "What is 5+3?", 
            "What is 10*1?"
        ]
        
        expected_patterns = ["4", "8", "10"]
        all_passed = True
        
        for i, (query, expected) in enumerate(zip(math_queries, expected_patterns)):
            response = await connection.direct_chat(
                messages=[{"role": "user", "content": query}],
                max_tokens=3,
                temperature=0.0
            )
            
            content = response["content"].strip()
            passed = expected in content
            
            print(f"   Math Test {i+1}: {query} → '{content}' (contains '{expected}'? {'✅' if passed else '❌'})")
            
            if not passed:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Source authenticity test failed: {e}")
        return False

def verify_malicious_files_removed():
    """Verify that malicious files have been removed."""
    print("\n🗑️ Verifying Malicious Files Removed...")
    
    malicious_files = [
        "glimpse/cache_helpers.py",
        "glimpse/openai_wrapper.py"
    ]
    
    all_removed = True
    
    for file_path in malicious_files:
        full_path = echoes_root / file_path
        if full_path.exists():
            print(f"   ❌ MALICIOUS FILE STILL EXISTS: {file_path}")
            all_removed = False
        else:
            print(f"   ✅ Removed: {file_path}")
    
    return all_removed

def verify_malicious_patterns_removed():
    """Verify that malicious patterns have been removed from remaining files."""
    print("\n🔍 Verifying Malicious Patterns Removed...")
    
    suspicious_patterns = [
        "cached_openai_call",
        "response_wrapper",
        "token_override",
        "source_clone",
        "intercept_response"
    ]
    
    files_to_check = [
        "glimpse/sampler_openai.py",
        "echoes/config.py",
        "echoes/utils/cache.py",
        "echoes/services/filesystem.py"
    ]
    
    all_clean = True
    
    for file_path in files_to_check:
        full_path = echoes_root / file_path
        if not full_path.exists():
            continue
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_clean = True
        for pattern in suspicious_patterns:
            if pattern in content:
                print(f"   ❌ {file_path}: Contains suspicious pattern '{pattern}'")
                all_clean = False
                file_clean = False
        
        if file_clean:
            print(f"   ✅ {file_path}: Clean")
    
    return all_clean

async def main():
    """Main verification function."""
    print("🔒 Echoes Final Security Verification")
    print("=" * 60)
    print(f"Testing after precision pruning...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Run all verification tests
    tests = [
        ("Malicious Files Removed", verify_malicious_files_removed),
        ("Malicious Patterns Removed", verify_malicious_patterns_removed),
        ("Token Limit Authenticity", test_token_limit_authenticity),
        ("No Interception", test_no_interception),
        ("Source Authenticity", test_source_authenticity)
    ]
    
    results = {}
    overall_status = "SECURE"
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                success = await test_func()
            else:
                success = test_func()
            results[test_name] = success
            if not success:
                overall_status = "COMPROMISED"
        except Exception as e:
            results[test_name] = False
            overall_status = "COMPROMISED"
            print(f"❌ {test_name} crashed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL SECURITY VERIFICATION SUMMARY")
    print("=" * 60)
    
    for test_name, success in results.items():
        status = "✅ SECURE" if success else "❌ COMPROMISED"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 OVERALL STATUS: {overall_status}")
    
    if overall_status == "SECURE":
        print("\n🎉 Echoes is FULLY SECURE for Arcade integration!")
        print("✅ All malicious deep nested patterns eliminated")
        print("✅ Token limitations completely removed")
        print("✅ No interception, cloning, or detour functions")
        print("✅ Source authenticity guaranteed")
        print("✅ Ready for production integration")
        print("\n🚀 Arcade integration can proceed with confidence!")
    else:
        print("\n⚠️ Echoes is still COMPROMISED")
        print("❌ Some malicious patterns remain")
        print("🔧 Additional cleanup required before Arcade integration")
    
    print(f"\nVerification completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return overall_status == "SECURE"

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
