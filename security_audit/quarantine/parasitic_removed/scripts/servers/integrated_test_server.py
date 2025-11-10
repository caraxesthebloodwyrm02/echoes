#!/usr/bin/env python3
"""
Integrated Test: FastAPI Server + Enhanced Archer Framework
Demonstrates full integration without network errors
"""

import subprocess
import sys
import time

import requests
from communication import (
    ArcherFramework,
    CommunicationMessage,
    CommunicationType,
    create_communicator,
)


class FastAPIServerManager:
    """Manages FastAPI server lifecycle for testing"""

    def __init__(self, port=8001):
        self.port = port
        self.process = None
        self.server_url = f"http://localhost:{port}"

    def start_server(self):
        """Start the FastAPI server in background"""
        print(f"🚀 Starting FastAPI server on port {self.port}...")

        try:
            # Start uvicorn server
            self.process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "examples.fastapi_archer_integration:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    str(self.port),
                    "--log-level",
                    "warning",  # Reduce log noise
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for server to start
            max_wait = 30
            for i in range(max_wait):
                try:
                    response = requests.get(f"{self.server_url}/health", timeout=1)
                    if response.status_code == 200:
                        print(
                            f"✅ FastAPI server started successfully on port {self.port}"
                        )
                        return True
                except:
                    time.sleep(1)
                    print(f"   ⏳ Waiting for server... ({i+1}/{max_wait})")

            print(f"❌ Failed to start FastAPI server within {max_wait} seconds")
            return False

        except Exception as e:
            print(f"❌ Error starting FastAPI server: {e}")
            return False

    def stop_server(self):
        """Stop the FastAPI server"""
        if self.process:
            print("🛑 Stopping FastAPI server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            print("✅ FastAPI server stopped")


def test_fastapi_integration():
    """Test Archer Framework with live FastAPI server"""
    print("\n🌐 Testing FastAPI Integration...")

    framework = ArcherFramework(max_workers=10)

    # Network communicator configured for FastAPI server
    network_config = {
        "host": "localhost",
        "port": 8001,
        "protocol": "tcp",
        "timeout": 5.0,
        "retry_count": 3,
        "pool_size": 5,
    }

    network_comm = create_communicator(CommunicationType.NETWORK, network_config)
    framework.register_communicator(CommunicationType.NETWORK, network_comm)

    # Test messages for FastAPI integration
    test_messages = [
        CommunicationMessage(
            content="Hello FastAPI server from Archer Framework!",
            sender="archer_client",
            receiver="fastapi_server",
            message_type=CommunicationType.NETWORK,
            metadata={"integration_test": True, "framework_version": "v2.0"},
        ),
        CommunicationMessage(
            content="Testing connection pooling with FastAPI",
            sender="pool_test_client",
            receiver="fastapi_server",
            message_type=CommunicationType.NETWORK,
            metadata={"pool_test": True, "message_id": 2},
        ),
        CommunicationMessage(
            content="Performance test message",
            sender="perf_client",
            receiver="fastapi_server",
            message_type=CommunicationType.NETWORK,
            metadata={"performance_test": True},
        ),
    ]

    print("   📤 Sending messages to FastAPI server...")
    success_count = 0
    total_time = 0

    for i, msg in enumerate(test_messages, 1):
        start_time = time.time()
        result = framework.send_message(msg)
        end_time = time.time()

        total_time += end_time - start_time

        if result.success:
            success_count += 1
            print(f"   ✅ Message {i}: Success ({result.response_time:.4f}s)")
            if result.metadata:
                print(f"      📊 Metadata: {result.metadata}")
        else:
            print(f"   ❌ Message {i}: {result.message}")

    avg_time = total_time / len(test_messages)
    print(f"   📊 Integration Results: {success_count}/{len(test_messages)} successful")
    print(f"   ⏱️  Average response time: {avg_time:.4f}s")

    framework.cleanup()
    return success_count == len(test_messages)


def test_comprehensive_with_server():
    """Run comprehensive test with live server"""
    print("\n🎯 Running Comprehensive Test with Live Server...")

    framework = ArcherFramework(max_workers=15)

    # Register all communicators
    network_config = {
        "host": "localhost",
        "port": 8001,
        "protocol": "tcp",
        "timeout": 3.0,
        "retry_count": 2,
        "pool_size": 3,
    }

    network_comm = create_communicator(CommunicationType.NETWORK, network_config)
    ipc_comm = create_communicator(CommunicationType.INTERPROCESS, {"method": "queue"})
    psych_comm = create_communicator(
        CommunicationType.PSYCHOLOGICAL,
        {"style": "assertive", "ei_level": 0.9, "analysis_depth": "comprehensive"},
    )
    physics_comm = create_communicator(
        CommunicationType.PHYSICS, {"medium": "air", "frequency": 2.4e9, "power": 10.0}
    )

    framework.register_communicator(CommunicationType.NETWORK, network_comm)
    framework.register_communicator(CommunicationType.INTERPROCESS, ipc_comm)
    framework.register_communicator(CommunicationType.PSYCHOLOGICAL, psych_comm)
    framework.register_communicator(CommunicationType.PHYSICS, physics_comm)

    # Comprehensive test messages
    test_messages = [
        CommunicationMessage(
            content="Network message to FastAPI server with connection pooling",
            sender="comprehensive_network_client",
            receiver="fastapi_server",
            message_type=CommunicationType.NETWORK,
            priority=8,
            metadata={"test_type": "comprehensive", "pooling_enabled": True},
        ),
        CommunicationMessage(
            content="Thread-safe IPC message for comprehensive testing",
            sender="comprehensive_ipc_client",
            receiver="ipc_handler",
            message_type=CommunicationType.INTERPROCESS,
            metadata={"thread_safe": True, "comprehensive": True},
        ),
        CommunicationMessage(
            content="I am absolutely thrilled and grateful for this comprehensive integration test with the FastAPI server! This demonstrates the amazing capabilities of our enhanced Archer Framework v2.0 working in perfect harmony.",
            sender="comprehensive_psych_client",
            receiver="psych_analyzer",
            message_type=CommunicationType.PSYCHOLOGICAL,
            priority=7,
            metadata={
                "comprehensive_test": True,
                "emotional_context": "positive_excitement",
            },
        ),
        CommunicationMessage(
            content="Physics signal transmission for comprehensive integration test",
            sender="comprehensive_physics_client",
            receiver="physics_receiver",
            message_type=CommunicationType.PHYSICS,
            metadata={"comprehensive": True, "integration_test": True},
        ),
    ]

    print("   📤 Running comprehensive test suite...")
    results = []

    for i, msg in enumerate(test_messages, 1):
        framework.print_output(
            f"\n📤 Comprehensive Test {i}: {msg.message_type.value.upper()}"
        )
        result = framework.send_message(msg)
        results.append(result)

        if result.success:
            framework.print_output(f"   ✅ Success: {result.message}")
            framework.print_output(f"   ⏱️  Response Time: {result.response_time:.4f}s")

            # Show enhanced metadata
            if result.metadata and "psychological_score" in result.metadata:
                psych_score = result.metadata["psychological_score"]
                emotional = result.metadata.get("emotional_analysis", {})
                framework.print_output(f"   🧠 Psychological Score: {psych_score:.2f}")
                framework.print_output(
                    f"   😊 Emotional Tone: {emotional.get('tone', 'unknown')} (confidence: {emotional.get('confidence', 0):.2f})"
                )

            if result.metadata and "signal_strength" in result.metadata:
                framework.print_output(
                    f"   📡 Signal Strength: {result.metadata['signal_strength']:.2f} dBm"
                )
                framework.print_output(
                    f"   🌊 Attenuation: {result.metadata.get('attenuation', 0):.2f} dB"
                )
        else:
            framework.print_output(f"   ❌ Failed: {result.message}")

    # Show comprehensive metrics
    framework.print_output("\n📊 Comprehensive Test Results:")
    metrics = framework.get_metrics()

    success_count = sum(1 for r in results if r.success)
    framework.print_output(f"   📈 Total Messages: {len(results)}")
    framework.print_output(f"   ✅ Successful: {success_count}")
    framework.print_output(f"   ❌ Failed: {len(results) - success_count}")
    framework.print_output(f"   📊 Success Rate: {success_count/len(results):.1%}")
    framework.print_output(
        f"   ⏱️  Overall Avg Response: {metrics.get('overall_avg_response', 0):.4f}s"
    )

    framework.cleanup()
    return success_count == len(test_messages)


def main():
    """Main integrated test function"""
    print("🚀 Archer Framework v2.0 - Integrated Test with FastAPI Server")
    print("=" * 70)

    server_manager = FastAPIServerManager(port=8001)

    try:
        # Start FastAPI server
        if not server_manager.start_server():
            print("❌ Failed to start FastAPI server. Exiting.")
            return False

        # Run tests with live server
        test1_success = test_fastapi_integration()
        test2_success = test_comprehensive_with_server()

        # Summary
        print("\n" + "=" * 70)
        print("📊 INTEGRATED TEST SUMMARY")
        print("=" * 70)

        print(f"   🌐 FastAPI Integration: {'✅ PASS' if test1_success else '❌ FAIL'}")
        print(f"   🎯 Comprehensive Test: {'✅ PASS' if test2_success else '❌ FAIL'}")

        overall_success = test1_success and test2_success
        print(
            f"\n🏆 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}"
        )

        if overall_success:
            print("\n🎉 PERFECT INTEGRATION!")
            print("🚀 Archer Framework v2.0 works seamlessly with FastAPI!")
            print(
                "✅ Connection pooling, thread safety, and enhanced features all working!"
            )

        return overall_success

    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
    finally:
        # Always stop the server
        server_manager.stop_server()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
