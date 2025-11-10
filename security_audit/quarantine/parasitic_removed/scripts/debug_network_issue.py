#!/usr/bin/env python3
"""
Debug Network Communication Issue
"""

import json
import socket
from datetime import datetime


def test_simple_network():
    """Test simple network connection without framework"""
    print("🔍 Testing Simple Network Connection...")

    try:
        # Create simple TCP client
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect(("localhost", 8080))

        # Send simple message
        message = {"test": "simple_network", "timestamp": datetime.now().isoformat()}

        data = json.dumps(message).encode("utf-8")
        sock.send(data)

        # Receive response
        response = sock.recv(1024)
        print(f"✅ Simple network success: {response.decode('utf-8')}")

        sock.close()
        return True

    except Exception as e:
        print(f"❌ Simple network failed: {e}")
        return False


def test_network_communicator_direct():
    """Test NetworkCommunicator directly"""
    print("\n🔍 Testing NetworkCommunicator Directly...")

    try:
        import sys

        sys.path.append(".")
        from communication import (
            CommunicationMessage,
            CommunicationType,
            NetworkCommunicator,
        )

        # Create communicator
        config = {
            "host": "localhost",
            "port": 8080,
            "protocol": "tcp",
            "timeout": 5.0,
            "retry_count": 2,
            "pool_size": 3,
        }

        comm = NetworkCommunicator(config)

        # Initialize
        init_result = comm.initialize()
        print(f"   Initialization: {init_result.success} - {init_result.message}")

        if not init_result.success:
            return False

        # Create test message
        message = CommunicationMessage(
            content="Direct test message",
            sender="direct_client",
            receiver="direct_server",
            message_type=CommunicationType.NETWORK,
        )

        # Send message
        result = comm.send(message)
        print(f"   Send result: {result.success} - {result.message}")

        # Cleanup
        comm.cleanup()
        return result.success

    except Exception as e:
        print(f"❌ Direct communicator test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main debug function"""
    print("🔧 Archer Framework v2.0 - Network Issue Debug")
    print("=" * 50)

    # Test simple network first
    simple_success = test_simple_network()

    if not simple_success:
        print("\n❌ Simple network failed - server may not be running")
        print("💡 Start the test server first:")
        print(
            "   python -c \"import socket; s=socket.socket(); s.bind(('localhost',8080)); s.listen(); print('Server ready'); conn,addr=s.accept(); print('Connected'); data=conn.recv(1024); conn.send(b'OK'); conn.close()\""
        )
        return False

    # Test communicator directly
    comm_success = test_network_communicator_direct()

    print("\n" + "=" * 50)
    print("📊 DEBUG RESULTS")
    print("=" * 50)
    print(f"Simple Network: {'✅ PASS' if simple_success else '❌ FAIL'}")
    print(f"Network Communicator: {'✅ PASS' if comm_success else '❌ FAIL'}")

    if comm_success:
        print("\n🎉 Network communicator is working!")
        print("💡 The issue may be in the framework integration")
    else:
        print("\n⚠️  Network communicator has issues")
        print("🔧 Check the implementation above")

    return comm_success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
