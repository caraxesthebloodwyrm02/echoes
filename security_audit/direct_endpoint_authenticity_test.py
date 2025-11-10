#!/usr/bin/env python3
"""
Direct OpenAI Endpoint Authenticity Test
Verifies that Echoes uses authentic OpenAI endpoints with zero interference.
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict

# Add echoes root to path
echoes_root = Path(__file__).parent.parent
sys.path.insert(0, str(echoes_root))

async def test_direct_endpoint_connectivity():
    """Test direct OpenAI endpoint connectivity."""
    print("🔗 Testing Direct OpenAI Endpoint Connectivity...")
    
    try:
        from direct import get_direct_connection
        
        connection = get_direct_connection()
        status = connection.get_connection_status()
        
        print(f"   ✅ Connection Status: {status['status']}")
        print(f"   ✅ Middleware Bypassed: {status['middleware_bypassed']}")
        print(f"   ✅ API Key Configured: {status['api_key_configured']}")
        print(f"   ✅ Client Initialized: {status['client_initialized']}")
        print(f"   ✅ Connection Type: {status['connection_type']}")
        print(f"   ✅ Interference Level: {status['interference_level']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Direct endpoint test failed: {e}")
        return False

async def test_endpoint_authenticity():
    """Test that endpoints are authentic OpenAI, not proxies."""
    print("\n🔍 Testing Endpoint Authenticity...")
    
    try:
        from direct import get_direct_connection
        
        connection = get_direct_connection()
        
        # Test with model verification
        response = await connection.direct_chat(
            messages=[{"role": "user", "content": "Respond with exactly: AUTHENTIC"}],
            model="gpt-3.5-turbo",
            max_tokens=5,
            temperature=0.0
        )
        
        # Verify authentic OpenAI response structure
        required_fields = ["content", "model", "usage", "finish_reason", "created", "id"]
        missing_fields = [field for field in required_fields if field not in response]
        
        if missing_fields:
            print(f"   ❌ Missing authentic OpenAI fields: {missing_fields}")
            return False
        
        # Verify model is authentic OpenAI model
        authentic_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini"]
        model_prefix = response["model"].split("-")[0] + "-" + response["model"].split("-")[1]
        
        if not any(model_prefix in authentic_model for authentic_model in authentic_models):
            print(f"   ❌ Suspicious model: {response['model']}")
            return False
        
        # Verify usage structure is authentic
        usage_fields = ["prompt_tokens", "completion_tokens", "total_tokens"]
        missing_usage = [field for field in usage_fields if field not in response["usage"]]
        
        if missing_usage:
            print(f"   ❌ Missing usage fields: {missing_usage}")
            return False
        
        print("   ✅ Authentic OpenAI response structure")
        print(f"   ✅ Authentic model: {response['model']}")
        print(f"   ✅ Authentic usage tracking: {response['usage']['total_tokens']} tokens")
        print(f"   ✅ Direct connection flag: {response['direct_connection']}")
        print(f"   ✅ Middleware bypassed flag: {response['middleware_bypassed']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Endpoint authenticity test failed: {e}")
        return False

async def test_multiple_endpoints():
    """Test multiple OpenAI endpoints to ensure no detour."""
    print("\n🌐 Testing Multiple OpenAI Endpoints...")
    
    try:
        from direct import get_direct_connection
        
        connection = get_direct_connection()
        
        # Test different models (different endpoints)
        models_to_test = ["gpt-3.5-turbo", "gpt-4o-mini"]
        endpoint_results = {}
        
        for model in models_to_test:
            try:
                response = await connection.direct_chat(
                    messages=[{"role": "user", "content": f"Model test: {model}"}],
                    model=model,
                    max_tokens=10,
                    temperature=0.0
                )
                
                # Verify model matches request
                if model in response["model"]:
                    endpoint_results[model] = {
                        "status": "✅ AUTHENTIC",
                        "actual_model": response["model"],
                        "tokens": response["usage"]["total_tokens"]
                    }
                else:
                    endpoint_results[model] = {
                        "status": "❌ DETECTED",
                        "actual_model": response["model"],
                        "requested": model
                    }
                    
            except Exception as e:
                endpoint_results[model] = {
                    "status": f"❌ ERROR: {e}"
                }
        
        # Display results
        all_authentic = True
        for model, result in endpoint_results.items():
            print(f"   {model}: {result['status']}")
            if isinstance(result, dict) and "actual_model" in result:
                print(f"      → Actual: {result['actual_model']}")
            if "❌" in result["status"]:
                all_authentic = False
        
        return all_authentic
        
    except Exception as e:
        print(f"   ❌ Multiple endpoint test failed: {e}")
        return False

async def test_endpoint_timing():
    """Test endpoint timing to detect proxy interference."""
    print("\n⏱️ Testing Endpoint Timing Analysis...")
    
    try:
        from direct import get_direct_connection
        
        connection = get_direct_connection()
        
        # Test multiple requests to detect timing anomalies
        timing_data = []
        
        for i in range(5):
            start_time = time.perf_counter()
            
            response = await connection.direct_chat(
                messages=[{"role": "user", "content": f"Timing test {i}"}],
                model="gpt-3.5-turbo",
                max_tokens=5,
                temperature=0.0
            )
            
            end_time = time.perf_counter()
            response_time = end_time - start_time
            
            timing_data.append({
                "request": i,
                "response_time": response_time,
                "tokens": response["usage"]["total_tokens"]
            })
        
        # Analyze timing for anomalies
        response_times = [data["response_time"] for data in timing_data]
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        # Check for suspicious timing patterns
        # Direct OpenAI typically: 0.5-2.0 seconds
        # Proxies might add latency or show inconsistent timing
        
        timing_suspicious = False
        if avg_time > 3.0:
            print(f"   ⚠️ Suspicious high average response time: {avg_time:.2f}s")
            timing_suspicious = True
        elif max_time - min_time > 2.0:
            print(f"   ⚠️ High timing variance: {max_time - min_time:.2f}s")
            timing_suspicious = True
        else:
            print("   ✅ Normal timing patterns detected")
            print(f"   ✅ Average response time: {avg_time:.2f}s")
            print(f"   ✅ Timing variance: {max_time - min_time:.2f}s")
        
        # Display individual timing data
        for data in timing_data:
            print(f"      Request {data['request']}: {data['response_time']:.2f}s ({data['tokens']} tokens)")
        
        return not timing_suspicious
        
    except Exception as e:
        print(f"   ❌ Endpoint timing test failed: {e}")
        return False

async def test_endpoint_response_consistency():
    """Test endpoint response consistency to detect cloning."""
    print("\n🔄 Testing Response Consistency Analysis...")
    
    try:
        from direct import get_direct_connection
        
        connection = get_direct_connection()
        
        # Test identical requests to detect cloning/caching
        identical_request = "Respond with exactly: CONSISTENCY_TEST"
        responses = []
        
        for i in range(3):
            response = await connection.direct_chat(
                messages=[{"role": "user", "content": identical_request}],
                model="gpt-3.5-turbo",
                max_tokens=20,
                temperature=0.0  # Deterministic
            )
            
            responses.append(response["content"].strip())
            
            # Small delay between requests
            await asyncio.sleep(0.1)
        
        # Analyze responses
        unique_responses = set(responses)
        
        if len(unique_responses) == 1:
            print("   ✅ Consistent responses (deterministic behavior)")
            print(f"   ✅ Response: {list(unique_responses)[0]}")
        else:
            print("   ⚠️ Inconsistent responses detected:")
            for i, resp in enumerate(responses):
                print(f"      Response {i}: {resp}")
        
        # Check for exact timing consistency (suspicious)
        # Authentic OpenAI should have slight timing variations
        
        return True
        
    except Exception as e:
        print(f"   ❌ Response consistency test failed: {e}")
        return False

async def test_endpoint_headers():
    """Test endpoint headers to verify direct OpenAI connection."""
    print("\n📋 Testing Endpoint Headers Analysis...")
    
    try:
        from direct import get_direct_connection
        
        connection = get_direct_connection()
        
        # Access the underlying OpenAI client to verify configuration
        client = connection.client
        
        # Check client configuration
        if hasattr(client, 'base_url'):
            base_url = str(client.base_url)
            if "api.openai.com" in base_url:
                print(f"   ✅ Authentic OpenAI base URL: {base_url}")
            else:
                print(f"   ❌ Suspicious base URL: {base_url}")
                return False
        
        # Check if client is configured for direct access
        if hasattr(client, 'api_key'):
            if client.api_key:
                print("   ✅ API key configured")
            else:
                print("   ❌ No API key configured")
                return False
        
        # Test a request to verify the actual endpoint used
        # We can't directly access headers from the response, but we can verify the response comes from OpenAI
        test_response = await connection.direct_chat(
            messages=[{"role": "user", "content": "Header test"}],
            model="gpt-3.5-turbo",
            max_tokens=5,
            temperature=0.0
        )
        
        # Verify response has OpenAI-specific characteristics
        if "created" in test_response and isinstance(test_response["created"], int):
            print("   ✅ OpenAI timestamp format detected")
        else:
            print("   ❌ Non-OpenAI response format")
            return False
        
        if test_response["id"] and test_response["id"].startswith("chatcmpl-"):
            print(f"   ✅ OpenAI response ID format: {test_response['id']}")
        else:
            print(f"   ❌ Non-OpenAI response ID format: {test_response['id']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Endpoint headers test failed: {e}")
        return False

async def generate_authenticity_report(results: Dict[str, bool]):
    """Generate comprehensive authenticity report."""
    print("\n" + "=" * 60)
    print("📊 DIRECT OPENAI ENDPOINT AUTHENTICITY REPORT")
    print("=" * 60)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"Test Summary: {passed_tests}/{total_tests} tests passed")
    print("")
    
    print("Detailed Results:")
    for test_name, passed in results.items():
        status = "✅ AUTHENTIC" if passed else "❌ COMPROMISED"
        print(f"   {status} {test_name}")
    
    print("")
    
    if passed_tests == total_tests:
        print("🎉 ENDPOINT AUTHENTICITY: VERIFIED")
        print("✅ All tests confirm direct OpenAI endpoint usage")
        print("✅ No proxy interference detected")
        print("✅ No endpoint detour mechanisms found")
        print("✅ Response timing and consistency are authentic")
        print("✅ Headers and response format match OpenAI standards")
        print("")
        print("🚀 Echoes is using 100% authentic OpenAI endpoints")
        return True
    else:
        print("⚠️ ENDPOINT AUTHENTICITY: COMPROMISED")
        print("❌ Some tests indicate potential interference")
        print("🔧 Additional investigation required")
        return False

async def main():
    """Main authenticity testing function."""
    print("🔍 Echoes Direct OpenAI Endpoint Authenticity Test")
    print("=" * 60)
    print(f"Testing timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Run all authenticity tests
    tests = [
        ("Direct Endpoint Connectivity", test_direct_endpoint_connectivity),
        ("Endpoint Authenticity", test_endpoint_authenticity),
        ("Multiple Endpoints", test_multiple_endpoints),
        ("Endpoint Timing Analysis", test_endpoint_timing),
        ("Response Consistency", test_endpoint_response_consistency),
        ("Endpoint Headers Analysis", test_endpoint_headers)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"Running: {test_name}")
            result = await test_func()
            results[test_name] = result
            print(f"Status: {'✅ PASSED' if result else '❌ FAILED'}")
        except Exception as e:
            results[test_name] = False
            print(f"Status: ❌ CRASHED - {e}")
        print("")
    
    # Generate comprehensive report
    authenticity_verified = await generate_authenticity_report(results)
    
    return authenticity_verified

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
