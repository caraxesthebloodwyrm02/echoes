#!/usr/bin/env python3
"""
Simple test server for demonstrating Archer Framework network communication
"""

import json
import socket
import threading
import time


def handle_client(conn, addr):
    """Handle incoming client connections"""
    print(f"🔗 New connection from {addr}")

    try:
        while True:
            data = conn.recv(8192)
            if not data:
                break

            try:
                # Parse and echo back the message
                message_data = json.loads(data.decode("utf-8"))
                response = {
                    "echo": message_data,
                    "server_time": time.time(),
                    "status": "received",
                }
                conn.send(json.dumps(response).encode("utf-8"))
                print(
                    f"📨 Echoed message to {addr}: {message_data.get('content', 'unknown')[:50]}..."
                )

            except json.JSONDecodeError:
                # Send simple echo for non-JSON data
                conn.send(b"Echo: " + data)

    except Exception as e:
        print(f"❌ Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"🔌 Connection closed: {addr}")


def start_test_server(host="localhost", port=8080):
    """Start a simple test server"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((host, port))
        server.listen(5)
        print(f"🚀 Test server started on {host}:{port}")
        print("📡 Ready to receive Archer Framework messages...")

        while True:
            conn, addr = server.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()

    except KeyboardInterrupt:
        print("\n🛑 Server shutting down...")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        server.close()


if __name__ == "__main__":
    start_test_server()
