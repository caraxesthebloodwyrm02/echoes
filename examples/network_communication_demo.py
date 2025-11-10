#!/usr/bin/env python3
"""
Network Communication Demo - Archer Framework

This demo shows how to use the Archer Framework for network communication
with a working server-client example.
"""

import socket
import sys
import threading
import time
from pathlib import Path

# Add the parent directory to the path to import communication module
sys.path.append(str(Path(__file__).parent.parent))

from communication import (
    ArcherFramework,
    CommunicationMessage,
    CommunicationType,
    create_communicator,
)


def start_simple_server(host="localhost", port=8080):
    """Start a simple echo server for testing"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"🌐 Server started on {host}:{port}")

        def handle_client(client_socket):
            """Handle individual client connections"""
            try:
                while True:
                    data = client_socket.recv(4096)
                    if not data:
                        break

                    # Echo the data back
                    response = f"ACK: {data.decode('utf-8')}"
                    client_socket.send(response.encode("utf-8"))
                    print(f"📨 Received and echoed: {data.decode('utf-8')[:50]}...")

            except Exception as e:
                print(f"❌ Client handler error: {e}")
            finally:
                client_socket.close()

        # Accept connections in a separate thread
        def accept_connections():
            try:
                while True:
                    client_socket, addr = server_socket.accept()
                    print(f"🔗 New connection from {addr}")

                    # Start client handler in a new thread
                    client_thread = threading.Thread(
                        target=handle_client, args=(client_socket,), daemon=True
                    )
                    client_thread.start()

            except Exception as e:
                print(f"❌ Server error: {e}")

        # Start accepting connections
        accept_thread = threading.Thread(target=accept_connections, daemon=True)
        accept_thread.start()

        return server_socket

    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None


def demo_network_communication():
    """Demonstrate working network communication"""
    print("🤖 Network Communication Demo - Archer Framework")
    print("=" * 60)

    # Start a simple server
    server_socket = start_simple_server()
    if not server_socket:
        print("❌ Failed to start server, exiting demo")
        return

    # Give the server time to start
    time.sleep(1)

    try:
        # Initialize the Archer Framework
        framework = ArcherFramework()

        # Create and register network communicator
        network_comm = create_communicator(
            CommunicationType.NETWORK,
            {"host": "localhost", "port": 8080, "protocol": "tcp"},
        )
        framework.register_communicator(CommunicationType.NETWORK, network_comm)

        print("\n📡 Testing Network Communication")
        print("-" * 40)

        # Test messages
        test_messages = [
            {"content": "Hello from Archer Framework!", "priority": 8},
            {"content": "Testing network reliability", "priority": 6},
            {
                "content": "Multi-domain communication test",
                "priority": 7,
                "metadata": {"test_type": "network", "iteration": 3},
            },
        ]

        # Send messages and measure performance
        for i, test_msg in enumerate(test_messages, 1):
            print(f"\n📤 Sending message {i}:")

            message = CommunicationMessage(
                content=test_msg["content"],
                sender="archer_client",
                receiver="echo_server",
                message_type=CommunicationType.NETWORK,
                priority=test_msg.get("priority", 5),
                metadata=test_msg.get("metadata", {}),
            )

            # Send message
            time.time()
            result = framework.send_message(message)
            time.time()

            # Display results
            if result.success:
                print(f"   ✅ Success: {result.message}")
                print(f"   ⏱️  Response Time: {result.response_time:.4f}s")
                print(f"   🆔 Message ID: {message.id[:8]}...")
                print(f"   🔐 Checksum: {message.checksum}")
            else:
                print(f"   ❌ Failed: {result.message}")
                if result.error_code:
                    print(f"   🚨 Error Code: {result.error_code}")

            # Small delay between messages
            time.sleep(0.5)

        # Performance analysis
        print("\n📊 Network Communication Performance:")
        print("-" * 45)

        metrics = framework.get_metrics()
        network_metrics = {k: v for k, v in metrics.items() if "network" in k}

        for key, value in network_metrics.items():
            if "avg_response" in key:
                print(f"   ⏱️  Average Response Time: {value:.4f}s")
            elif "success_rate" in key:
                print(f"   ✅ Success Rate: {value:.2%}")

        print(f"   📨 Total Messages: {len(framework.message_history)}")

        # Test message reception
        print("\n🔍 Testing Message Reception:")
        print("-" * 35)

        received_message = network_comm.receive(timeout=2.0)
        if received_message:
            print(f"   📬 Received: {received_message.content}")
            print(f"   📅 Timestamp: {received_message.timestamp}")
            print(f"   👤 Sender: {received_message.sender}")
        else:
            print("   ⏳ No message received (server may be processing)")

    except Exception as e:
        print(f"❌ Demo error: {e}")

    finally:
        # Cleanup
        if server_socket:
            server_socket.close()
            print("\n🔌 Server closed")

        print("\n🎯 Network Communication Demo Complete!")


def demo_multiple_clients():
    """Demonstrate multiple clients communicating with the server"""
    print("\n🌐 Multiple Client Demo")
    print("=" * 30)

    # Start server
    server_socket = start_simple_server()
    if not server_socket:
        return

    time.sleep(1)

    try:

        def client_worker(client_id: int, message_count: int = 3):
            """Worker function for each client"""
            framework = ArcherFramework()
            network_comm = create_communicator(
                CommunicationType.NETWORK,
                {"host": "localhost", "port": 8080, "protocol": "tcp"},
            )
            framework.register_communicator(CommunicationType.NETWORK, network_comm)

            for i in range(message_count):
                message = CommunicationMessage(
                    content=f"Client {client_id} - Message {i+1}",
                    sender=f"client_{client_id}",
                    receiver="server",
                    message_type=CommunicationType.NETWORK,
                    metadata={"client_id": client_id, "message_num": i + 1},
                )

                result = framework.send_message(message)
                if result.success:
                    print(f"   📤 Client {client_id}: Message {i+1} sent")
                else:
                    print(f"   ❌ Client {client_id}: Failed to send message {i+1}")

                time.sleep(0.2)

        # Start multiple client threads
        client_threads = []
        num_clients = 3

        print(f"🚀 Starting {num_clients} concurrent clients...")

        for client_id in range(1, num_clients + 1):
            thread = threading.Thread(
                target=client_worker, args=(client_id, 3), daemon=True
            )
            client_threads.append(thread)
            thread.start()
            time.sleep(0.1)  # Stagger client starts

        # Wait for all clients to complete
        for thread in client_threads:
            thread.join()

        print(f"✅ All {num_clients} clients completed their messages")

    except Exception as e:
        print(f"❌ Multiple client demo error: {e}")

    finally:
        if server_socket:
            server_socket.close()


def main():
    """Run all network communication demos"""
    print("🌐 Archer Framework - Network Communication Suite")
    print("=" * 60)
    print()

    try:
        # Demo 1: Basic network communication
        demo_network_communication()

        print("\n" + "=" * 60)

        # Demo 2: Multiple concurrent clients
        demo_multiple_clients()

        print("\n" + "=" * 60)
        print("🎉 All Network Demos Completed Successfully!")

        print("\n💡 Key Demonstrations:")
        print("   • Server-client communication using Archer Framework")
        print("   • Real-time performance monitoring")
        print("   • Message integrity with checksums")
        print("   • Concurrent client handling")
        print("   • Comprehensive error handling")
        print("   • Graceful connection management")

    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo suite error: {e}")


if __name__ == "__main__":
    main()
