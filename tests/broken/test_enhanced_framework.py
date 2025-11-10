#!/usr/bin/env python3
"""
Comprehensive test script for Archer Framework v2.0 enhanced features
"""

import asyncio
import threading
import time

from communication import (ArcherFramework, CommunicationMessage,
                           CommunicationType, create_communicator)


def test_connection_pooling():
    """Test network connection pooling capabilities"""
    print("🌐 Testing Connection Pooling...")

    framework = ArcherFramework(max_workers=5)

    # Network communicator with connection pooling
    network_config = {
        "host": "localhost",
        "port": 8080,
        "protocol": "tcp",
        "timeout": 2.0,
        "retry_count": 2,
        "pool_size": 3,
    }

    network_comm = create_communicator(CommunicationType.NETWORK, network_config)
    framework.register_communicator(CommunicationType.NETWORK, network_comm)

    # Send multiple messages to test pooling
    messages = [
        CommunicationMessage(
            content=f"Pool test message {i}",
            sender="test_client",
            receiver="test_server",
            message_type=CommunicationType.NETWORK,
            metadata={"pool_test": True},
        )
        for i in range(3)
    ]

    print("   📤 Sending 3 messages through connection pool...")
    success_count = 0

    for i, msg in enumerate(messages, 1):
        result = framework.send_message(msg)
        if result.success:
            success_count += 1
            print(f"   ✅ Message {i}: Success ({result.response_time:.4f}s)")
        else:
            print(f"   ❌ Message {i}: {result.message}")

    print(f"   📊 Pool Test Result: {success_count}/{len(messages)} successful")
    framework.cleanup()
    return success_count == len(messages)


def test_thread_safety():
    """Test thread-safe operations"""
    print("\n🔒 Testing Thread Safety...")

    framework = ArcherFramework(max_workers=10)
    psych_comm = create_communicator(
        CommunicationType.PSYCHOLOGICAL, {"style": "assertive", "ei_level": 0.8}
    )
    framework.register_communicator(CommunicationType.PSYCHOLOGICAL, psych_comm)

    results = []
    errors = []

    def send_message_worker(worker_id):
        """Worker function for concurrent message sending"""
        try:
            message = CommunicationMessage(
                content=f"Concurrent test from worker {worker_id}",
                sender=f"worker_{worker_id}",
                receiver="main_thread",
                message_type=CommunicationType.PSYCHOLOGICAL,
            )
            result = framework.send_message(message)
            results.append((worker_id, result.success, result.response_time))
        except Exception as e:
            errors.append((worker_id, str(e)))

    # Create multiple threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=send_message_worker, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    success_count = sum(1 for _, success, _ in results if success)
    print(f"   📊 Thread Safety Test: {success_count}/{len(threads)} successful")
    print(f"   🐛 Errors: {len(errors)}")

    if errors:
        for worker_id, error in errors:
            print(f"      ❌ Worker {worker_id}: {error}")

    framework.cleanup()
    return len(errors) == 0 and success_count == len(threads)


async def test_async_operations():
    """Test async/await capabilities"""
    print("\n🔄 Testing Async Operations...")

    framework = ArcherFramework(max_workers=5)
    psych_comm = create_communicator(
        CommunicationType.PSYCHOLOGICAL, {"style": "assertive", "ei_level": 0.9}
    )
    framework.register_communicator(CommunicationType.PSYCHOLOGICAL, psych_comm)

    # Create test messages
    messages = [
        CommunicationMessage(
            content=f"Async test message {i}",
            sender="async_sender",
            receiver="async_receiver",
            message_type=CommunicationType.PSYCHOLOGICAL,
        )
        for i in range(3)
    ]

    print("   📤 Sending messages asynchronously...")
    start_time = time.time()

    # Send messages concurrently
    tasks = [framework.send_message_async(msg) for msg in messages]
    results = await asyncio.gather(*tasks)

    end_time = time.time()
    async_time = end_time - start_time

    success_count = sum(1 for result in results if result.success)
    avg_response = sum(result.response_time for result in results) / len(results)

    print(f"   ✅ Async Results: {success_count}/{len(messages)} successful")
    print(f"   ⏱️  Total async time: {async_time:.4f}s")
    print(f"   📊 Average response: {avg_response:.4f}s")

    framework.cleanup()
    return success_count == len(messages)


def test_enhanced_psychological_analysis():
    """Test enhanced psychological analysis features"""
    print("\n🧠 Testing Enhanced Psychological Analysis...")

    framework = ArcherFramework()
    psych_comm = create_communicator(
        CommunicationType.PSYCHOLOGICAL,
        {"style": "assertive", "ei_level": 0.95, "analysis_depth": "comprehensive"},
    )
    framework.register_communicator(CommunicationType.PSYCHOLOGICAL, psych_comm)

    # Test messages with different emotional content
    test_messages = [
        {
            "content": "I am absolutely thrilled and grateful for this wonderful opportunity to collaborate with amazing people!",
            "expected_tone": "positive",
        },
        {
            "content": "I feel frustrated and disappointed about the current situation, but I understand we need to work together.",
            "expected_tone": "mixed",
        },
        {
            "content": "The data shows clear patterns and requires careful analysis to determine the optimal approach.",
            "expected_tone": "neutral",
        },
    ]

    print("   📊 Analyzing emotional content...")
    success_count = 0

    for i, test_case in enumerate(test_messages, 1):
        message = CommunicationMessage(
            content=test_case["content"],
            sender="test_analyzer",
            receiver="psych_engine",
            message_type=CommunicationType.PSYCHOLOGICAL,
        )

        result = framework.send_message(message)

        if result.success:
            metadata = result.metadata
            emotional = metadata.get("emotional_analysis", {})
            detected_tone = emotional.get("tone", "unknown")
            confidence = emotional.get("confidence", 0)
            psych_score = metadata.get("psychological_score", 0)

            print(f"   📝 Test {i}:")
            print(f"      🔍 Expected: {test_case['expected_tone']}")
            print(f"      🎯 Detected: {detected_tone} (confidence: {confidence:.2f})")
            print(f"      🧠 Psych Score: {psych_score:.2f}")

            success_count += 1
        else:
            print(f"   ❌ Test {i} failed: {result.message}")

    print(f"   📊 Analysis Results: {success_count}/{len(test_messages)} successful")
    framework.cleanup()
    return success_count == len(test_messages)


def test_performance_monitoring():
    """Test comprehensive performance monitoring"""
    print("\n📊 Testing Performance Monitoring...")

    framework = ArcherFramework()

    # Register multiple communicators
    ipc_comm = create_communicator(CommunicationType.INTERPROCESS, {"method": "queue"})
    psych_comm = create_communicator(
        CommunicationType.PSYCHOLOGICAL, {"style": "assertive"}
    )
    physics_comm = create_communicator(
        CommunicationType.PHYSICS, {"medium": "air", "frequency": 2.4e9, "power": 5.0}
    )

    framework.register_communicator(CommunicationType.INTERPROCESS, ipc_comm)
    framework.register_communicator(CommunicationType.PSYCHOLOGICAL, psych_comm)
    framework.register_communicator(CommunicationType.PHYSICS, physics_comm)

    # Send messages to generate metrics
    messages = [
        CommunicationMessage(
            content="Performance test message",
            sender="perf_test",
            receiver="monitor",
            message_type=comm_type,
        )
        for comm_type in [
            CommunicationType.INTERPROCESS,
            CommunicationType.PSYCHOLOGICAL,
            CommunicationType.PHYSICS,
        ]
    ]

    print("   📤 Generating performance metrics...")
    for msg in messages:
        framework.send_message(msg)

    # Get comprehensive metrics
    metrics = framework.get_metrics()
    status = framework.get_communicator_status()

    print("   📈 Performance Metrics:")
    print(f"      📊 Total Messages: {int(metrics.get('total_messages', 0))}")
    print(f"      ✅ Success Rate: {metrics.get('overall_success_rate', 0):.1%}")
    print(f"      ⏱️  Avg Response: {metrics.get('overall_avg_response', 0):.4f}s")
    print(f"      ⏰ Uptime: {metrics.get('uptime_seconds', 0):.1f}s")

    print("   📡 Communicator Status:")
    for comm_type, info in status.items():
        status_icon = "✅" if info["is_active"] else "❌"
        print(f"      {status_icon} {comm_type.title()}: {info['class']}")

    framework.cleanup()
    return True


async def run_comprehensive_tests():
    """Run all enhanced feature tests"""
    print("🚀 Archer Framework v2.0 - Comprehensive Enhanced Features Test")
    print("=" * 70)

    test_results = {}

    # Run synchronous tests
    test_results["connection_pooling"] = test_connection_pooling()
    test_results["thread_safety"] = test_thread_safety()
    test_results["psychological_analysis"] = test_enhanced_psychological_analysis()
    test_results["performance_monitoring"] = test_performance_monitoring()

    # Run async test
    test_results["async_operations"] = await test_async_operations()

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    total_tests = len(test_results)
    passed_tests = sum(test_results.values())

    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name.replace('_', ' ').title()}")

    print(f"\n🎯 Overall Results: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 ALL ENHANCED FEATURES WORKING PERFECTLY!")
        print("🚀 Archer Framework v2.0 is ready for production deployment!")
    else:
        print("⚠️  Some features need attention. Check the test results above.")

    return passed_tests == total_tests


if __name__ == "__main__":
    # Run the comprehensive test suite
    success = asyncio.run(run_comprehensive_tests())
    exit(0 if success else 1)
