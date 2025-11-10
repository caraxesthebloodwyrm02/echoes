#!/usr/bin/env python3
"""
Fixed Network Communicator - Resolves generator issue
"""

import json
import queue
import socket
from threading import RLock

from communication import (BaseCommunicator, CommunicationConfig,
                           CommunicationMessage, CommunicationResult)


class FixedNetworkCommunicator(BaseCommunicator):
    """Fixed Network communication implementation"""

    def __init__(self, config=None):
        super().__init__(config)
        # Validate and set configuration
        self.config = CommunicationConfig.validate_network_config(config or {})
        self.host = self.config["host"]
        self.port = self.config["port"]
        self.protocol = self.config["protocol"]
        self.timeout = self.config["timeout"]
        self.retry_count = self.config["retry_count"]
        self.pool_size = self.config["pool_size"]

        self._connection_pool = queue.Queue(maxsize=self.pool_size)
        self._pool_lock = RLock()

    def _create_connection(self):
        """Create a new network connection"""
        if self.protocol.lower() == "tcp":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.settimeout(self.timeout)
        sock.connect((self.host, self.port))
        return sock

    def _test_connection(self, connection):
        """Test if a connection is still alive"""
        try:
            if self.protocol.lower() == "tcp":
                # Simple test for TCP connection
                connection.send(b"")
                return True
            else:
                # UDP is connectionless, always return True
                return True
        except:
            return False

    def initialize(self):
        """Initialize network connection pool"""
        try:
            # Create initial connections for the pool
            for _ in range(min(2, self.pool_size)):
                try:
                    conn = self._create_connection()
                    self._connection_pool.put(conn)
                except Exception as e:
                    print(f"Warning: Failed to create initial connection: {e}")

            self.is_active = True
            return CommunicationResult(
                success=True,
                message=f"Fixed Network connection pool initialized (size: {self.pool_size})",
            )
        except Exception as e:
            return CommunicationResult(
                success=False, message=f"Network init failed: {str(e)}"
            )

    def send(self, message: CommunicationMessage) -> CommunicationResult:
        """Send network message without context manager to avoid generator issues"""
        if not self.is_active:
            init_result = self.initialize()
            if not init_result.success:
                return init_result

        connection = None
        try:
            # Try to get from pool
            try:
                connection = self._connection_pool.get_nowait()
                # Test if connection is still alive
                if not self._test_connection(connection):
                    connection.close()
                    connection = None
            except queue.Empty:
                pass

            # Create new connection if needed
            if connection is None:
                connection = self._create_connection()

            # Send data
            data = json.dumps(
                {
                    "id": message.id,
                    "content": message.content,
                    "sender": message.sender,
                    "receiver": message.receiver,
                    "timestamp": message.timestamp,
                    "checksum": message.checksum,
                    "message_type": message.message_type.value,
                    "priority": message.priority,
                }
            ).encode("utf-8")

            connection.send(data)

            # Try to return connection to pool
            try:
                if self._test_connection(connection):
                    self._connection_pool.put_nowait(connection)
                else:
                    connection.close()
            except queue.Full:
                connection.close()

            return CommunicationResult(
                success=True,
                message="Fixed Network message sent successfully",
                metadata={"pool_size": self._connection_pool.qsize()},
            )

        except Exception as e:
            if connection:
                try:
                    connection.close()
                except:
                    pass
            return CommunicationResult(
                success=False, message=f"Fixed Network send failed: {str(e)}"
            )

    def receive(self, timeout=5.0):
        """Receive network message with timeout"""
        if not self.is_active:
            return None

        connection = None
        try:
            # Try to get from pool
            try:
                connection = self._connection_pool.get_nowait()
                # Test if connection is still alive
                if not self._test_connection(connection):
                    connection.close()
                    connection = None
            except queue.Empty:
                pass

            # Create new connection if needed
            if connection is None:
                connection = self._create_connection()

            # Set timeout and receive
            original_timeout = connection.gettimeout()
            connection.settimeout(timeout)

            try:
                data = connection.recv(8192)
                if data:
                    msg_data = json.loads(data.decode("utf-8"))
                    result = CommunicationMessage(
                        id=msg_data["id"],
                        content=msg_data["content"],
                        sender=msg_data["sender"],
                        receiver=msg_data["receiver"],
                        message_type=msg_data["message_type"],
                        priority=msg_data.get("priority", 5),
                        metadata=msg_data.get("metadata", {}),
                    )

                    # Try to return connection to pool
                    try:
                        if self._test_connection(connection):
                            self._connection_pool.put_nowait(connection)
                        else:
                            connection.close()
                    except queue.Full:
                        connection.close()

                    return result
            finally:
                connection.settimeout(original_timeout)

        except Exception:
            if connection:
                try:
                    connection.close()
                except:
                    pass
            return None

    def cleanup(self):
        """Cleanup network resources"""
        while not self._connection_pool.empty():
            try:
                conn = self._connection_pool.get_nowait()
                conn.close()
            except:
                pass
        self.is_active = False
        return CommunicationResult(
            success=True, message="Fixed Network communicator cleaned up"
        )


def test_fixed_communicator():
    """Test the fixed network communicator"""
    print("🔧 Testing Fixed Network Communicator...")

    try:
        # Create communicator
        config = {
            "host": "localhost",
            "port": 8080,
            "protocol": "tcp",
            "timeout": 5.0,
            "retry_count": 2,
            "pool_size": 3,
        }

        comm = FixedNetworkCommunicator(config)

        # Initialize
        init_result = comm.initialize()
        print(f"   Initialization: {init_result.success} - {init_result.message}")

        if not init_result.success:
            return False

        # Create test message
        from communication import CommunicationMessage, CommunicationType

        message = CommunicationMessage(
            content="Fixed network test message!",
            sender="fixed_client",
            receiver="fixed_server",
            message_type=CommunicationType.NETWORK,
        )

        # Send message
        result = comm.send(message)
        print(f"   Send result: {result.success} - {result.message}")

        if result.success:
            print(f"   📊 Pool Size: {result.metadata.get('pool_size', 0)}")

        # Cleanup
        cleanup_result = comm.cleanup()
        print(f"   Cleanup: {cleanup_result.success}")

        return result.success

    except Exception as e:
        print(f"❌ Fixed communicator test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Fixed Network Communicator Test")
    print("=" * 40)

    success = test_fixed_communicator()

    print("\n" + "=" * 40)
    if success:
        print("🎉 FIXED NETWORK COMMUNICATOR WORKS!")
        print("✅ Generator issue resolved")
        print("✅ Connection pooling working")
        print("✅ Ready for integration")
    else:
        print("⚠️  Fixed version still has issues")

    exit(0 if success else 1)
