#!/usr/bin/env python3
"""
Simple test server for Archer Framework v2.0 integration testing
"""

import json
import socket
import threading
from datetime import datetime


class SimpleTestServer:
    """Simple TCP server for testing Archer Framework network communication"""

    def __init__(self, host="localhost", port=8080):
        self.host = host
        self.port = port
        self.server = None
        self.running = False

    def handle_client(self, conn, addr):
        """Handle incoming client connections"""
        print(f"🔗 New connection from {addr}")

        try:
            while self.running:
                data = conn.recv(8192)
                if not data:
                    break

                try:
                    # Parse and echo back the message with metadata
                    message_data = json.loads(data.decode("utf-8"))
                    response = {
                        "echo": message_data,
                        "server_time": datetime.now().isoformat(),
                        "server_info": {
                            "host": self.host,
                            "port": self.port,
                            "framework": "Archer Framework v2.0 Test Server",
                        },
                        "status": "received",
                        "processing_time": 0.001,
                    }
                    conn.send(json.dumps(response).encode("utf-8"))
                    print(
                        f"📨 Echoed message to {addr}: {message_data.get('content', 'unknown')[:50]}..."
                    )

                except json.JSONDecodeError:
                    # Send simple echo for non-JSON data
                    simple_response = {
                        "echo": data.decode("utf-8", errors="ignore"),
                        "server_time": datetime.now().isoformat(),
                        "status": "received",
                    }
                    conn.send(json.dumps(simple_response).encode("utf-8"))

        except Exception as e:
            print(f"❌ Error handling client {addr}: {e}")
        finally:
            conn.close()
            print(f"🔌 Connection closed: {addr}")

    def start(self):
        """Start the test server"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            self.running = True

            print(f"🚀 Simple Test Server started on {self.host}:{self.port}")
            print("📡 Ready to receive Archer Framework messages...")

            while self.running:
                try:
                    conn, addr = self.server.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client, args=(conn, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except OSError:
                    if self.running:
                        print("❌ Server socket error")
                    break

        except KeyboardInterrupt:
            print("\n🛑 Server shutting down...")
        except Exception as e:
            print(f"❌ Server error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the test server"""
        self.running = False
        if self.server:
            self.server.close()
        print("✅ Test server stopped")


def main():
    """Main function to run the test server"""
    server = SimpleTestServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
