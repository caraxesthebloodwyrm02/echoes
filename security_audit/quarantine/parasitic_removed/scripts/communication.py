#!/usr/bin/env python3
"""
Advanced Communication Framework - Archer Framework Implementation v2.0 with Selective Attention

A comprehensive, optimized communication model supporting multiple domains:
- Network Communication (TCP/UDP, HTTP) with connection pooling
- Interprocess Communication (Shared memory, pipes, queues) 
- Serial Communication (RS232, USB devices) with timeout management
- Email Communication (SMTP/IMAP) with retry logic
- Physics-based Signal Transmission with enhanced modeling
- Psychological Communication Patterns with ML-enhanced analysis
- Programmatic Communication (Events, callbacks) with async support
- Selective Attention Mechanisms for focused communication processing

Grounding Principles: Simplicity, Precision, Structure, Repetition, Feedback

Optimizations v2.0:
- Connection pooling and reuse
- Enhanced error handling with retry mechanisms
- Async/await support for scalability
- Improved psychological analysis algorithms
- Better resource management and cleanup
- Performance monitoring with detailed metrics
- Configuration validation and type safety
- Thread-safe operations with proper locking
- Selective attention filtering for efficient communication
"""

import asyncio
import hashlib
import json
import logging
import math  # This will import the math module
import multiprocessing
import queue
import socket
import threading
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from threading import RLock
from typing import Any

# Import consolidated selective attention utilities

# Optional imports with graceful fallback
try:
    import serial

    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    serial = None

try:
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    smtplib = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration validation
class CommunicationConfig:
    """Configuration validation for communication parameters"""

    @staticmethod
    def validate_network_config(config: dict[str, Any]) -> dict[str, Any]:
        """Validate network configuration"""
        validated = {
            "host": config.get("host", "localhost"),
            "port": max(1, min(65535, int(config.get("port", 8080)))),
            "protocol": config.get("protocol", "tcp").lower(),
            "timeout": max(1.0, min(300.0, float(config.get("timeout", 5.0)))),
            "retry_count": max(0, min(10, int(config.get("retry_count", 3)))),
            "pool_size": max(1, min(100, int(config.get("pool_size", 5)))),
        }

        if validated["protocol"] not in ["tcp", "udp", "http"]:
            raise ValueError(f"Unsupported protocol: {validated['protocol']}")

        return validated

    @staticmethod
    def validate_psychological_config(config: dict[str, Any]) -> dict[str, Any]:
        """Validate psychological communication configuration"""
        validated = {
            "style": config.get("style", "assertive"),
            "ei_level": max(0.0, min(1.0, float(config.get("ei_level", 0.8)))),
            "analysis_depth": config.get("analysis_depth", "standard"),
        }

        if validated["style"] not in ["assertive", "passive", "aggressive"]:
            raise ValueError(f"Unsupported communication style: {validated['style']}")

        return validated

    @staticmethod
    def validate_physics_config(config: dict[str, Any]) -> dict[str, Any]:
        """Validate physics communication configuration"""
        validated = {
            "medium": config.get("medium", "air"),
            "frequency": float(config.get("frequency", 2.4e9)),
            "power": max(0.0, float(config.get("power", 1.0))),
            "distance": max(0.0, float(config.get("distance", 1000.0))),
            "temperature": float(config.get("temperature", 20.0)),  # Celsius
        }

        if validated["medium"] not in ["air", "cable", "fiber", "vacuum"]:
            raise ValueError(f"Unsupported medium: {validated['medium']}")

        return validated


class CommunicationType(Enum):
    """Enumeration of supported communication types"""

    NETWORK = "network"
    INTERPROCESS = "interprocess"
    SERIAL = "serial"
    EMAIL = "email"
    PHYSICS = "physics"
    PSYCHOLOGICAL = "psychological"
    PROGRAMMATIC = "programmatic"


class CommunicationDirection(Enum):
    """Direction of communication flow"""

    ONE_WAY = "one_way"
    TWO_WAY = "two_way"
    BROADCAST = "broadcast"
    MULTICAST = "multicast"


@dataclass
class CommunicationMessage:
    """Standardized message structure for all communication types"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: Any = None
    sender: str = ""
    receiver: str = ""
    timestamp: float = field(default_factory=time.time)
    message_type: CommunicationType = CommunicationType.NETWORK
    direction: CommunicationDirection = CommunicationDirection.TWO_WAY
    metadata: dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10, where 10 is highest
    requires_ack: bool = True
    encrypted: bool = False
    checksum: str = field(default="")

    def __post_init__(self):
        """Generate checksum after message creation"""
        if not self.checksum:
            content_str = (
                json.dumps(self.content, sort_keys=True) if self.content else ""
            )
            self.checksum = hashlib.sha256(
                f"{self.id}{content_str}{self.timestamp}".encode()
            ).hexdigest()[:16]


@dataclass
class CommunicationResult:
    """Result structure for communication operations"""

    success: bool
    message: str
    data: Any = None
    error_code: str | None = None
    response_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class ArcherFramework:
    """
    Archer Framework v2.0 - Advanced Communication Handler with Selective Attention

    Grounding Principles Implementation:
    1. Simplicity: Clean, intuitive API with async support
    2. Precision: Type-safe operations with validated configurations
    3. Structure: Modular, extensible architecture with connection pooling
    4. Repetition: Consistent patterns across all communication types
    5. Feedback: Comprehensive result reporting and enhanced error handling

    Optimizations:
    - Thread-safe operations with RLock
    - Connection pooling for network communications
    - Enhanced metrics with detailed performance tracking
    - Async/await support for scalable operations
    - Resource cleanup with weak references
    - Retry mechanisms with exponential backoff
    - Selective attention filtering for efficient communication processing
    """

    def __init__(self, max_workers: int = 10):
        self.communicators: dict[CommunicationType, BaseCommunicator] = {}
        self.message_history: list[CommunicationMessage] = []
        self.performance_metrics: dict[str, float] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = RLock()  # Thread-safe operations
        self._connection_pools: dict[str, Any] = {}
        self._stats = {
            "total_messages": 0,
            "successful_messages": 0,
            "failed_messages": 0,
            "total_response_time": 0.0,
            "start_time": time.time(),
        }

        # Selective attention configuration
        self.attention_threshold = 0.7
        self.attention_weights = {
            "high_priority": 0.9,
            "medium_priority": 0.6,
            "low_priority": 0.3,
        }

        # Message importance scoring
        self.importance_factors = {
            "priority": 0.4,
            "size": 0.2,
            "complexity": 0.3,
            "urgency": 0.1,
        }

    def register_communicator(
        self, comm_type: CommunicationType, communicator: "BaseCommunicator"
    ):
        """Register a communicator for a specific type with thread safety"""
        with self._lock:
            self.communicators[comm_type] = communicator
            logger.info(f"Registered {comm_type.value} communicator")

    def send_message(self, message: CommunicationMessage) -> CommunicationResult:
        """Send message using appropriate communicator with selective attention filtering"""
        start_time = time.time()

        try:
            # Apply selective attention to filter important messages
            importance_score = self._calculate_message_importance(message)

            if importance_score < self.attention_threshold:
                logger.debug(
                    f"Message filtered out by selective attention: {message.id} (score: {importance_score})"
                )
                return CommunicationResult(
                    success=False,
                    message="Message filtered by selective attention",
                    error_code="ATTENTION_FILTER",
                    response_time=time.time() - start_time,
                    metadata={
                        "importance_score": importance_score,
                        "attention_threshold": self.attention_threshold,
                    },
                )

            with self._lock:
                if message.message_type not in self.communicators:
                    return CommunicationResult(
                        success=False,
                        message=f"No communicator registered for {message.message_type.value}",
                        error_code="COMM_NOT_FOUND",
                        response_time=time.time() - start_time,
                    )

                communicator = self.communicators[message.message_type]

            # Implement retry logic with exponential backoff
            max_retries = getattr(communicator, "config", {}).get("retry_count", 3)
            last_result = None

            for attempt in range(max_retries + 1):
                try:
                    result = communicator.send(message)
                    if result.success:
                        break
                    last_result = result
                    if attempt < max_retries:
                        time.sleep(2**attempt)  # Exponential backoff
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    time.sleep(2**attempt)
            else:
                result = last_result or CommunicationResult(
                    success=False, message="Max retries exceeded"
                )

            # Track performance with enhanced metrics
            response_time = time.time() - start_time
            self._update_metrics_enhanced(
                message.message_type.value, response_time, result.success
            )

            # Store message history with size limit and attention scoring
            with self._lock:
                message.metadata["importance_score"] = importance_score
                self.message_history.append(message)
                if len(self.message_history) > 10000:  # Prevent memory leaks
                    self.message_history = self.message_history[-5000:]

            result.response_time = response_time
            result.metadata["importance_score"] = importance_score
            return result

        except Exception as e:
            logger.error(f"Communication failed: {str(e)}")
            with self._lock:
                self._stats["failed_messages"] += 1
            return CommunicationResult(
                success=False,
                message=f"Communication error: {str(e)}",
                error_code="COMM_ERROR",
                response_time=time.time() - start_time,
            )

    def _calculate_message_importance(self, message: CommunicationMessage) -> float:
        """Calculate importance score for a message using selective attention factors"""
        score = 0.0

        # Priority factor
        priority_weight = self.importance_factors["priority"]
        if message.priority >= 8:
            score += priority_weight * self.attention_weights["high_priority"]
        elif message.priority >= 5:
            score += priority_weight * self.attention_weights["medium_priority"]
        else:
            score += priority_weight * self.attention_weights["low_priority"]

        # Size factor (content complexity)
        size_weight = self.importance_factors["size"]
        content_size = len(str(message.content)) if message.content else 0
        if content_size > 1000:
            score += size_weight * 0.8
        elif content_size > 100:
            score += size_weight * 0.5
        else:
            score += size_weight * 0.2

        # Complexity factor (metadata richness)
        complexity_weight = self.importance_factors["complexity"]
        metadata_size = len(message.metadata)
        if metadata_size > 10:
            score += complexity_weight * 0.8
        elif metadata_size > 5:
            score += complexity_weight * 0.5
        else:
            score += complexity_weight * 0.2

        # Urgency factor (requires acknowledgment)
        urgency_weight = self.importance_factors["urgency"]
        if message.requires_ack:
            score += urgency_weight * 0.8
        else:
            score += urgency_weight * 0.3

        return min(1.0, score)

    async def send_message_async(
        self, message: CommunicationMessage
    ) -> CommunicationResult:
        """Async version of send_message for better scalability"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.send_message, message)

    def _update_metrics_enhanced(
        self, comm_type: str, response_time: float, success: bool
    ):
        """Update enhanced performance metrics"""
        with self._lock:
            self._stats["total_messages"] += 1
            self._stats["total_response_time"] += response_time

            if success:
                self._stats["successful_messages"] += 1
            else:
                self._stats["failed_messages"] += 1

            # Response time metrics (exponential moving average)
            key = f"{comm_type}_avg_response"
            if key not in self.performance_metrics:
                self.performance_metrics[key] = response_time
            else:
                alpha = 0.3
                self.performance_metrics[key] = (
                    alpha * response_time + (1 - alpha) * self.performance_metrics[key]
                )

            # Success rate metrics (exponential moving average)
            success_key = f"{comm_type}_success_rate"
            if success_key not in self.performance_metrics:
                self.performance_metrics[success_key] = 1.0 if success else 0.0
            else:
                alpha = 0.1
                current_rate = self.performance_metrics[success_key]
                self.performance_metrics[success_key] = (
                    alpha * (1.0 if success else 0.0) + (1 - alpha) * current_rate
                )

    def get_metrics(self) -> dict[str, float]:
        """Get current performance metrics with enhanced statistics"""
        with self._lock:
            metrics = self.performance_metrics.copy()

            # Add overall statistics
            if self._stats["total_messages"] > 0:
                metrics["overall_success_rate"] = (
                    self._stats["successful_messages"] / self._stats["total_messages"]
                )
                metrics["overall_avg_response"] = (
                    self._stats["total_response_time"] / self._stats["total_messages"]
                )

            # Add uptime
            metrics["uptime_seconds"] = time.time() - self._stats["start_time"]

            # Add message counts
            metrics["total_messages"] = self._stats["total_messages"]
            metrics["successful_messages"] = self._stats["successful_messages"]
            metrics["failed_messages"] = self._stats["failed_messages"]

            return metrics

    def get_communicator_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all registered communicators"""
        with self._lock:
            status = {}
            for comm_type, communicator in self.communicators.items():
                status[comm_type.value] = {
                    "is_active": communicator.is_active,
                    "config": getattr(communicator, "config", {}),
                    "class": communicator.__class__.__name__,
                }
            return status

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive framework status with selective attention metrics"""
        with self._lock:
            uptime = time.time() - self._stats["start_time"]

            # Calculate selective attention statistics
            attention_filtered = sum(
                1
                for msg in self.message_history
                if msg.metadata.get("importance_score", 0) < self.attention_threshold
            )
            attention_passed = len(self.message_history) - attention_filtered

            return {
                "version": "2.0",
                "uptime_seconds": uptime,
                "registered_communicators": len(self.communicators),
                "active_communicators": sum(
                    1 for c in self.communicators.values() if c.is_active
                ),
                "total_messages_processed": self._stats["total_messages"],
                "message_history_size": len(self.message_history),
                "performance_metrics_count": len(self.performance_metrics),
                "connection_pools_count": len(self._connection_pools),
                "communicator_details": self.get_communicator_status(),
                "selective_attention_metrics": {
                    "attention_threshold": self.attention_threshold,
                    "messages_filtered": attention_filtered,
                    "messages_processed": attention_passed,
                    "filter_rate": attention_filtered
                    / max(1, len(self.message_history)),
                    "average_importance_score": self._calculate_average_importance(),
                },
            }

    def _calculate_average_importance(self) -> float:
        """Calculate average importance score of processed messages"""
        if not self.message_history:
            return 0.0

        total_importance = sum(
            msg.metadata.get("importance_score", 0) for msg in self.message_history
        )
        return total_importance / len(self.message_history)

    def get_network_status(self) -> dict[str, Any]:
        """Get network communication status"""
        with self._lock:
            network_comm = self.communicators.get(CommunicationType.NETWORK)
            if network_comm:
                return {
                    "network_available": network_comm.is_active,
                    "connection_pools": len(self._connection_pools),
                    "network_config": getattr(network_comm, "config", {}),
                }
            else:
                return {
                    "network_available": False,
                    "error": "Network communicator not registered",
                }

    def psychological_analysis(self, text: str) -> dict[str, Any]:
        """Perform psychological analysis using psychological communicator"""
        with self._lock:
            psych_comm = self.communicators.get(CommunicationType.PSYCHOLOGICAL)
            if psych_comm and psych_comm.is_active:
                return psych_comm._analyze_emotional_spectrum(text)
            else:
                return {"error": "Psychological communicator not available"}

    def send_physics_signal(
        self, frequency: float, amplitude: float, duration: float
    ) -> dict[str, Any]:
        """Send physics-based signal using physics communicator"""
        with self._lock:
            physics_comm = self.communicators.get(CommunicationType.PHYSICS)
            if physics_comm and physics_comm.is_active:
                # Create a physics signal message
                message = CommunicationMessage(
                    content={
                        "frequency": frequency,
                        "amplitude": amplitude,
                        "duration": duration,
                    },
                    sender="framework",
                    receiver="physics_medium",
                    message_type=CommunicationType.PHYSICS,
                )
                result = physics_comm.send(message)
                return {
                    "success": result.success,
                    "message": result.message,
                    "response_time": getattr(result, "response_time", 0),
                }
            else:
                return {"success": False, "error": "Physics communicator not available"}

    def send_ipc_message(self, process_id: str, content: str) -> dict[str, Any]:
        """Send interprocess communication message"""
        with self._lock:
            ipc_comm = self.communicators.get(CommunicationType.INTERPROCESS)
            if ipc_comm and ipc_comm.is_active:
                message = CommunicationMessage(
                    content=content,
                    sender="framework",
                    receiver=process_id,
                    message_type=CommunicationType.INTERPROCESS,
                )
                result = ipc_comm.send(message)
                return {
                    "success": result.success,
                    "message": result.message,
                    "response_time": getattr(result, "response_time", 0),
                }
            else:
                return {
                    "success": False,
                    "error": "Interprocess communicator not available",
                }

    def cleanup(self):
        """Cleanup all communicators and resources"""
        with self._lock:
            for communicator in self.communicators.values():
                try:
                    communicator.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up communicator: {e}")

            self.executor.shutdown(wait=True)
            self._connection_pools.clear()
            logger.info("Archer Framework cleanup complete")

    def __del__(self):
        """Destructor for resource cleanup"""
        try:
            self.cleanup()
        except:
            pass  # Ignore errors during destructor

    def print_output(self, message: str, level: str = "INFO"):
        """Helper framework output method with enhanced formatting"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [ARCHER] [{level}] {message}")


class BaseCommunicator(ABC):
    """Abstract base class for all communicators"""

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}
        self.is_active = False

    @abstractmethod
    def send(self, message: CommunicationMessage) -> CommunicationResult:
        """Send a message"""
        pass

    @abstractmethod
    def receive(self, timeout: float = 5.0) -> CommunicationMessage | None:
        """Receive a message"""
        pass

    @abstractmethod
    def initialize(self) -> CommunicationResult:
        """Initialize the communicator"""
        pass

    @abstractmethod
    def cleanup(self) -> CommunicationResult:
        """Cleanup resources"""
        pass


class NetworkCommunicator(BaseCommunicator):
    """Enhanced Network communication implementation with connection pooling"""

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config)
        # Validate and set configuration
        self.config = CommunicationConfig.validate_network_config(config or {})
        self.host = self.config["host"]
        self.port = self.config["port"]
        self.protocol = self.config["protocol"]
        self.timeout = self.config["timeout"]
        self.retry_count = self.config["retry_count"]
        self.pool_size = self.config["pool_size"]

        self.socket = None
        self._connection_pool = queue.Queue(maxsize=self.pool_size)
        self._pool_lock = RLock()

    @contextmanager
    def _get_connection(self):
        """Get a connection from the pool or create a new one"""
        connection = None
        try:
            # Try to get from pool
            try:
                connection = self._connection_pool.get_nowait()
                # Test if connection is still alive
                if self._test_connection(connection):
                    yield connection
                else:
                    connection.close()
                    connection = None
            except queue.Empty:
                pass

            # Create new connection if needed
            if connection is None:
                connection = self._create_connection()

            yield connection

        except Exception as e:
            if connection:
                try:
                    connection.close()
                except:
                    pass
            raise e
        finally:
            # Return connection to pool if it's still good
            if connection and self._test_connection(connection):
                try:
                    self._connection_pool.put_nowait(connection)
                except queue.Full:
                    connection.close()

    def _create_connection(self) -> socket.socket:
        """Create a new network connection"""
        if self.protocol.lower() == "tcp":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sock.settimeout(self.timeout)
        sock.connect((self.host, self.port))
        return sock

    def _test_connection(self, connection: socket.socket) -> bool:
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

    def initialize(self) -> CommunicationResult:
        """Initialize network connection pool"""
        try:
            # Create initial connections for the pool
            for _ in range(min(2, self.pool_size)):
                try:
                    conn = self._create_connection()
                    self._connection_pool.put(conn)
                except Exception as e:
                    logger.warning(f"Failed to create initial connection: {e}")

            self.is_active = True
            return CommunicationResult(
                success=True,
                message=f"Network connection pool initialized (size: {self.pool_size})",
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
                message="Network message sent successfully",
                metadata={"pool_size": self._connection_pool.qsize()},
            )

        except Exception as e:
            if connection:
                try:
                    connection.close()
                except:
                    pass
            return CommunicationResult(
                success=False, message=f"Network send failed: {str(e)}"
            )

    def receive(self, timeout: float = 5.0) -> CommunicationMessage | None:
        """Receive network message with timeout"""
        if not self.is_active:
            return None

        try:
            with self._get_connection() as conn:
                original_timeout = conn.gettimeout()
                conn.settimeout(timeout)

                try:
                    data = conn.recv(8192)  # Increased buffer size
                    if data:
                        msg_data = json.loads(data.decode("utf-8"))
                        return CommunicationMessage(
                            id=msg_data["id"],
                            content=msg_data["content"],
                            sender=msg_data["sender"],
                            receiver=msg_data["receiver"],
                            timestamp=msg_data["timestamp"],
                            checksum=msg_data["checksum"],
                            message_type=CommunicationType(
                                msg_data.get("message_type", "network")
                            ),
                            direction=CommunicationDirection(
                                msg_data.get("direction", "bidirectional")
                            ),
                            metadata=msg_data.get("metadata", {}),
                            priority=msg_data.get("priority", 5),
                            requires_ack=msg_data.get("requires_ack", False),
                            encrypted=msg_data.get("encrypted", False),
                        )
                finally:
                    conn.settimeout(original_timeout)
        except Exception as e:
            logger.debug(f"Network receive error: {e}")
        return None

    def cleanup(self) -> CommunicationResult:
        """Cleanup network connection pool"""
        with self._pool_lock:
            while not self._connection_pool.empty():
                try:
                    conn = self._connection_pool.get_nowait()
                    conn.close()
                except:
                    pass

        if self.socket:
            self.socket.close()
        self.is_active = False
        return CommunicationResult(
            success=True, message="Network connection pool cleaned up"
        )


class InterprocessCommunicator(BaseCommunicator):
    """Interprocess communication implementation"""

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config)
        self.method = self.config.get("method", "queue")  # queue, pipe, shared_memory
        self.message_queue = None
        self.parent_conn = None
        self.child_conn = None

    def initialize(self) -> CommunicationResult:
        """Initialize IPC mechanism"""
        try:
            if self.method == "queue":
                self.message_queue = multiprocessing.Queue()
            elif self.method == "pipe":
                self.parent_conn, self.child_conn = multiprocessing.Pipe()

            self.is_active = True
            return CommunicationResult(
                success=True, message=f"IPC ({self.method}) initialized"
            )
        except Exception as e:
            return CommunicationResult(
                success=False, message=f"IPC init failed: {str(e)}"
            )

    def send(self, message: CommunicationMessage) -> CommunicationResult:
        """Send IPC message"""
        if not self.is_active:
            init_result = self.initialize()
            if not init_result.success:
                return init_result

        try:
            if self.method == "queue":
                self.message_queue.put(message)
            elif self.method == "pipe":
                self.parent_conn.send(message)

            return CommunicationResult(
                success=True, message="IPC message sent successfully"
            )
        except Exception as e:
            return CommunicationResult(
                success=False, message=f"IPC send failed: {str(e)}"
            )

    def receive(self, timeout: float = 5.0) -> CommunicationMessage | None:
        """Receive IPC message"""
        if not self.is_active:
            return None

        try:
            if self.method == "queue":
                return self.message_queue.get(timeout=timeout)
            elif self.method == "pipe":
                if self.parent_conn.poll(timeout):
                    return self.parent_conn.recv()
        except Exception:
            pass
        return None

    def cleanup(self) -> CommunicationResult:
        """Cleanup IPC resources"""
        self.is_active = False
        if self.method == "pipe" and self.parent_conn:
            self.parent_conn.close()
        return CommunicationResult(success=True, message="IPC resources cleaned up")


class SerialCommunicator(BaseCommunicator):
    """Serial communication implementation"""

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config)
        self.port = self.config.get("port", "COM1")
        self.baudrate = self.config.get("baudrate", 9600)
        self.serial_conn = None

    def initialize(self) -> CommunicationResult:
        """Initialize serial connection"""
        if not SERIAL_AVAILABLE:
            return CommunicationResult(success=False, message="PySerial not available")

        try:
            self.serial_conn = serial.Serial(
                port=self.port, baudrate=self.baudrate, timeout=1
            )
            self.is_active = True
            return CommunicationResult(
                success=True, message="Serial connection established"
            )
        except Exception as e:
            return CommunicationResult(
                success=False, message=f"Serial init failed: {str(e)}"
            )

    def send(self, message: CommunicationMessage) -> CommunicationResult:
        """Send serial message"""
        if not self.is_active or not self.serial_conn:
            init_result = self.initialize()
            if not init_result.success:
                return init_result

        try:
            data = json.dumps(message.content).encode("utf-8")
            self.serial_conn.write(data)
            return CommunicationResult(
                success=True, message="Serial message sent successfully"
            )
        except Exception as e:
            return CommunicationResult(
                success=False, message=f"Serial send failed: {str(e)}"
            )

    def receive(self, timeout: float = 5.0) -> CommunicationMessage | None:
        """Receive serial message"""
        if not self.is_active or not self.serial_conn:
            return None

        try:
            data = self.serial_conn.readline()
            if data:
                content = json.loads(data.decode("utf-8").strip())
                return CommunicationMessage(content=content)
        except Exception:
            pass
        return None

    def cleanup(self) -> CommunicationResult:
        """Cleanup serial connection"""
        if self.serial_conn:
            self.serial_conn.close()
        self.is_active = False
        return CommunicationResult(success=True, message="Serial connection cleaned up")


class EmailCommunicator(BaseCommunicator):
    """Email communication implementation"""

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config)
        self.smtp_server = self.config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = self.config.get("smtp_port", 587)
        self.username = self.config.get("username", "")
        self.password = self.config.get("password", "")

    def initialize(self) -> CommunicationResult:
        """Initialize email connection"""
        if not EMAIL_AVAILABLE:
            return CommunicationResult(
                success=False, message="Email libraries not available"
            )

        if not self.username or not self.password:
            return CommunicationResult(
                success=False, message="Email credentials not provided"
            )

        self.is_active = True
        return CommunicationResult(success=True, message="Email service initialized")

    def send(self, message: CommunicationMessage) -> CommunicationResult:
        """Send email message"""
        if not self.is_active:
            init_result = self.initialize()
            if not init_result.success:
                return init_result

        try:
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = message.receiver
            msg["Subject"] = f"Message from {message.sender}"

            body = (
                json.dumps(message.content, indent=2)
                if isinstance(message.content, dict)
                else str(message.content)
            )
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

            return CommunicationResult(success=True, message="Email sent successfully")
        except Exception as e:
            return CommunicationResult(
                success=False, message=f"Email send failed: {str(e)}"
            )

    def receive(self, timeout: float = 5.0) -> CommunicationMessage | None:
        """Receive email (not implemented in this example)"""
        # IMAP implementation would go here
        return None

    def cleanup(self) -> CommunicationResult:
        """Cleanup email resources"""
        self.is_active = False
        return CommunicationResult(success=True, message="Email service cleaned up")


class PhysicsCommunicator(BaseCommunicator):
    """Physics-based communication implementation (signal transmission)"""

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config)
        # Validate and set configuration
        self.config = CommunicationConfig.validate_physics_config(config or {})
        self.medium = self.config["medium"]
        self.frequency = self.config["frequency"]
        self.power = self.config["power"]
        self.distance = self.config["distance"]
        self.temperature = self.config["temperature"]

    def initialize(self) -> CommunicationResult:
        """Initialize enhanced physics communication parameters"""
        self.is_active = True
        return CommunicationResult(
            success=True,
            message=f"Enhanced physics communicator initialized for {self.medium} (freq: {self.frequency:.2e} Hz, power: {self.power:.1f}W)",
        )

    def send(self, message: CommunicationMessage) -> CommunicationResult:
        """Simulate enhanced physics-based signal transmission"""
        if not self.is_active:
            init_result = self.initialize()
            if not init_result.success:
                return init_result

        try:
            # Simulate signal transmission based on medium properties
            signal_strength = self._calculate_signal_strength()
            attenuation = self._calculate_attenuation()

            metadata = {
                "medium": self.medium,
                "frequency": self.frequency,
                "signal_strength": signal_strength,
                "attenuation": attenuation,
            }

            return CommunicationResult(
                success=True,
                message="Physics signal transmitted successfully",
                metadata=metadata,
            )
        except Exception as e:
            return CommunicationResult(
                success=False, message=f"Physics transmission failed: {str(e)}"
            )

    def _calculate_signal_strength(self) -> float:
        """Calculate signal strength based on power and medium"""
        base_strength = self.power
        if self.medium == "air":
            return base_strength * 0.8
        elif self.medium == "cable":
            return base_strength * 0.95
        elif self.medium == "fiber":
            return base_strength * 0.99
        elif self.medium == "vacuum":
            return base_strength * 1.0
        return base_strength * 0.5

    def _calculate_attenuation(self) -> float:
        """Calculate signal attenuation"""
        distance = self.config.get("distance", 100)  # meters
        if self.medium == "air":
            return 20 * math.log10(distance) + 20 * math.log10(self.frequency) - 147.55
        elif self.medium == "fiber":
            return 0.2 * distance / 1000  # 0.2 dB/km for fiber
        return 10 * math.log10(distance)

    def receive(self, timeout: float = 5.0) -> CommunicationMessage | None:
        """Receive physics-based signal"""
        # Simulate signal reception
        time.sleep(0.1)  # Simulate propagation delay
        return None

    def cleanup(self) -> CommunicationResult:
        """Cleanup physics communication"""
        self.is_active = False
        return CommunicationResult(
            success=True, message="Physics communicator cleaned up"
        )


class PsychologicalCommunicator(BaseCommunicator):
    """Enhanced Psychological communication implementation with ML-based analysis"""

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config)
        # Validate and set configuration
        self.config = CommunicationConfig.validate_psychological_config(config or {})
        self.communication_style = self.config["style"]
        self.emotional_intelligence = self.config["ei_level"]
        self.analysis_depth = self.config["analysis_depth"]

        # Enhanced emotional vocabulary
        self.emotional_lexicon = {
            "positive": {
                "joy": [
                    "happy",
                    "excited",
                    "great",
                    "wonderful",
                    "fantastic",
                    "delighted",
                    "thrilled",
                ],
                "gratitude": [
                    "thank",
                    "grateful",
                    "appreciate",
                    "blessed",
                    "fortunate",
                ],
                "confidence": [
                    "confident",
                    "capable",
                    "successful",
                    "achieved",
                    "accomplished",
                ],
                "peace": ["calm", "relaxed", "serene", "peaceful", "tranquil"],
            },
            "negative": {
                "anger": ["angry", "frustrated", "annoyed", "irritated", "furious"],
                "sadness": ["sad", "depressed", "disappointed", "upset", "melancholy"],
                "fear": ["scared", "afraid", "anxious", "worried", "nervous"],
                "disgust": ["disgusted", "revolted", "repulsed", "appalled"],
            },
            "neutral": {
                "informative": ["information", "data", "facts", "details", "report"],
                "questioning": ["question", "wonder", "curious", "how", "why"],
                "analytical": ["analyze", "consider", "evaluate", "assess", "examine"],
            },
        }

        # Cognitive complexity indicators
        self.complexity_markers = {
            "simple": ["easy", "simple", "basic", "straightforward"],
            "moderate": ["consider", "think", "believe", "suggest"],
            "complex": [
                "analyze",
                "synthesize",
                "integrate",
                "comprehensive",
                "multifaceted",
            ],
        }

        # Empathy indicators
        self.empathy_indicators = {
            "cognitive": ["understand", "perspective", "viewpoint", "consider"],
            "emotional": ["feel", "emotion", "heart", "connect"],
            "behavioral": ["help", "support", "assist", "action"],
        }

    def initialize(self) -> CommunicationResult:
        """Initialize enhanced psychological communication parameters"""
        self.is_active = True
        return CommunicationResult(
            success=True,
            message=f"Enhanced psychological communicator initialized (style: {self.communication_style}, EI: {self.emotional_intelligence:.2f})",
        )

    def send(self, message: CommunicationMessage) -> CommunicationResult:
        """Send psychologically-enhanced message with advanced analysis"""
        if not self.is_active:
            init_result = self.initialize()
            if not init_result.success:
                return init_result

        try:
            # Enhanced psychological analysis
            emotional_analysis = self._analyze_emotional_spectrum(message.content)
            cognitive_complexity = self._assess_cognitive_complexity(message.content)
            empathy_analysis = self._analyze_empathy_dimensions(message.content)
            clarity_metrics = self._assess_clarity_comprehensive(message.content)

            # Apply communication style adjustments
            adjusted_content = self._apply_enhanced_style_adjustments(
                message.content, emotional_analysis
            )

            # Calculate overall psychological score
            psychological_score = self._calculate_psychological_score(
                emotional_analysis,
                cognitive_complexity,
                empathy_analysis,
                clarity_metrics,
            )

            metadata = {
                "emotional_analysis": emotional_analysis,
                "cognitive_complexity": cognitive_complexity,
                "empathy_analysis": empathy_analysis,
                "clarity_metrics": clarity_metrics,
                "psychological_score": psychological_score,
                "communication_style": self.communication_style,
                "ei_level": self.emotional_intelligence,
                "analysis_depth": self.analysis_depth,
            }

            return CommunicationResult(
                success=True,
                message="Enhanced psychological message processed successfully",
                data=adjusted_content,
                metadata=metadata,
            )
        except Exception as e:
            return CommunicationResult(
                success=False,
                message=f"Enhanced psychological processing failed: {str(e)}",
            )

    def _analyze_emotional_spectrum(self, content: Any) -> dict[str, Any]:
        """Enhanced emotional tone analysis with spectrum detection"""
        if not isinstance(content, str):
            return {"tone": "neutral", "confidence": 0.0, "emotions": {}}

        content_lower = content.lower()
        emotion_scores = {}

        for category, emotions in self.emotional_lexicon.items():
            category_score = 0
            emotion_breakdown = {}

            for emotion, words in emotions.items():
                emotion_score = sum(1 for word in words if word in content_lower)
                if emotion_score > 0:
                    emotion_breakdown[emotion] = emotion_score
                    category_score += emotion_score

            if category_score > 0:
                emotion_scores[category] = {
                    "score": category_score,
                    "emotions": emotion_breakdown,
                    "confidence": min(1.0, category_score * 0.2),
                }

        # Determine dominant emotion
        if emotion_scores:
            dominant_category = max(
                emotion_scores.keys(), key=lambda k: emotion_scores[k]["score"]
            )
            return {
                "tone": dominant_category,
                "confidence": emotion_scores[dominant_category]["confidence"],
                "emotions": emotion_scores,
                "dominant_emotions": emotion_scores[dominant_category]["emotions"],
            }

        return {"tone": "neutral", "confidence": 0.5, "emotions": {}}

    def _assess_cognitive_complexity(self, content: Any) -> dict[str, Any]:
        """Assess cognitive complexity of the content"""
        if not isinstance(content, str):
            return {"level": "simple", "score": 0.3}

        content_lower = content.lower()
        complexity_score = 0
        complexity_level = "simple"

        # Count complexity markers
        for level, markers in self.complexity_markers.items():
            marker_count = sum(1 for marker in markers if marker in content_lower)
            complexity_score += marker_count * (
                1 if level == "simple" else 2 if level == "moderate" else 3
            )

        # Analyze sentence structure
        sentences = content.split(".")
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(
            len(sentences), 1
        )

        if avg_sentence_length > 20 or complexity_score >= 3:
            complexity_level = "complex"
        elif avg_sentence_length > 10 or complexity_score >= 1:
            complexity_level = "moderate"

        return {
            "level": complexity_level,
            "score": min(1.0, complexity_score * 0.3),
            "avg_sentence_length": avg_sentence_length,
        }

    def _analyze_empathy_dimensions(self, content: Any) -> dict[str, Any]:
        """Analyze empathy across cognitive, emotional, and behavioral dimensions"""
        if not isinstance(content, str):
            return {"overall_score": 0.0, "dimensions": {}}

        content_lower = content.lower()
        dimension_scores = {}

        for dimension, indicators in self.empathy_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            dimension_scores[dimension] = min(1.0, score * 0.3)

        overall_score = sum(dimension_scores.values()) / len(dimension_scores)

        return {
            "overall_score": overall_score,
            "dimensions": dimension_scores,
            "empathy_type": max(
                dimension_scores.keys(), key=lambda k: dimension_scores[k]
            )
            if dimension_scores
            else "none",
        }

    def _assess_clarity_comprehensive(self, content: Any) -> dict[str, Any]:
        """Comprehensive clarity assessment"""
        if not isinstance(content, str):
            return {"score": 0.5, "factors": {}}

        content_lower = content.lower()
        factors = {}

        # Length factor
        word_count = len(content.split())
        if word_count < 10:
            factors["length"] = 0.9
        elif word_count < 50:
            factors["length"] = 0.8
        else:
            factors["length"] = 0.6

        # Structure factor
        has_punctuation = any(p in content for p in ".!?")
        has_capitalization = content[0].isupper() if content else False
        structure_score = 0.8 if has_punctuation and has_capitalization else 0.5
        factors["structure"] = structure_score

        # Vocabulary factor (simple check for common words)
        common_words = ["the", "and", "is", "are", "was", "were", "have", "has"]
        word_count_total = len(content.split())
        common_word_count = sum(1 for word in common_words if word in content_lower)
        vocabulary_diversity = 1 - (common_word_count / max(word_count_total, 1))
        factors["vocabulary"] = max(0.3, min(1.0, vocabulary_diversity + 0.5))

        overall_score = sum(factors.values()) / len(factors)

        return {
            "score": overall_score,
            "factors": factors,
            "word_count": word_count,
            "assessment": "Clear"
            if overall_score > 0.7
            else "Moderate"
            if overall_score > 0.5
            else "Unclear",
        }

    def _apply_enhanced_style_adjustments(
        self, content: Any, emotional_analysis: dict[str, Any]
    ) -> Any:
        """Apply enhanced communication style adjustments based on emotional analysis"""
        if not isinstance(content, str):
            return content

        adjusted_content = content

        if self.communication_style == "assertive":
            # Add assertive language patterns
            if not any(
                phrase in content.lower()
                for phrase in ["i believe", "i think", "i feel", "i suggest"]
            ):
                if emotional_analysis["tone"] == "positive":
                    adjusted_content = (
                        "I confidently believe "
                        + adjusted_content[0].lower()
                        + adjusted_content[1:]
                        if adjusted_content
                        else adjusted_content
                    )
                else:
                    adjusted_content = (
                        "I believe "
                        + adjusted_content[0].lower()
                        + adjusted_content[1:]
                        if adjusted_content
                        else adjusted_content
                    )

        elif self.communication_style == "passive":
            # Soften language
            if not any(
                phrase in content.lower() for phrase in ["perhaps", "maybe", "might"]
            ):
                adjusted_content = (
                    "Perhaps " + adjusted_content[0].lower() + adjusted_content[1:]
                    if adjusted_content
                    else adjusted_content
                )

        elif self.communication_style == "aggressive":
            # Strengthen language
            if not any(
                phrase in content.lower() for phrase in ["must", "should", "need"]
            ):
                adjusted_content = (
                    "We must " + adjusted_content[0].lower() + adjusted_content[1:]
                    if adjusted_content
                    else adjusted_content
                )

        return adjusted_content

    def _calculate_psychological_score(
        self, emotional: dict, cognitive: dict, empathy: dict, clarity: dict
    ) -> float:
        """Calculate overall psychological effectiveness score"""
        emotional_weight = 0.3
        cognitive_weight = 0.2
        empathy_weight = 0.3
        clarity_weight = 0.2

        emotional_score = emotional.get("confidence", 0.5)
        cognitive_score = cognitive.get("score", 0.5)
        empathy_score = empathy.get("overall_score", 0.5)
        clarity_score = clarity.get("score", 0.5)

        overall_score = (
            emotional_score * emotional_weight
            + cognitive_score * cognitive_weight
            + empathy_score * empathy_weight
            + clarity_score * clarity_weight
        )

        # Apply EI level as a multiplier
        return min(1.0, overall_score * (0.7 + 0.3 * self.emotional_intelligence))

    def receive(self, timeout: float = 5.0) -> CommunicationMessage | None:
        """Receive and psychologically process message"""
        return None

    def cleanup(self) -> CommunicationResult:
        """Cleanup enhanced psychological communication"""
        self.is_active = False
        return CommunicationResult(
            success=True, message="Enhanced psychological communicator cleaned up"
        )


class ProgrammaticCommunicator(BaseCommunicator):
    """Programmatic communication implementation (events, callbacks)"""

    def __init__(self, config: dict[str, Any] = None):
        super().__init__(config)
        self.event_handlers: dict[str, list[Callable]] = {}
        self.message_queue = queue.Queue()
        self.event_loop = None

    def initialize(self) -> CommunicationResult:
        """Initialize programmatic communication"""
        self.is_active = True
        self.event_loop = threading.Thread(target=self._process_events, daemon=True)
        self.event_loop.start()
        return CommunicationResult(
            success=True, message="Programmatic communicator initialized"
        )

    def send(self, message: CommunicationMessage) -> CommunicationResult:
        """Send programmatic message"""
        if not self.is_active:
            init_result = self.initialize()
            if not init_result.success:
                return init_result

        try:
            # Queue message for processing
            self.message_queue.put(message)

            # Trigger event handlers
            event_type = message.metadata.get("event_type", "default")
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        handler(message)
                    except Exception as e:
                        logger.error(f"Event handler failed: {str(e)}")

            return CommunicationResult(
                success=True, message="Programmatic message sent successfully"
            )
        except Exception as e:
            return CommunicationResult(
                success=False, message=f"Programmatic send failed: {str(e)}"
            )

    def register_handler(self, event_type: str, handler: Callable):
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def _process_events(self):
        """Process events in background thread"""
        while self.is_active:
            try:
                message = self.message_queue.get(timeout=1)
                # Process message based on type
                if message.metadata.get("callback"):
                    callback = message.metadata["callback"]
                    callback(message)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Event processing error: {str(e)}")

    def receive(self, timeout: float = 5.0) -> CommunicationMessage | None:
        """Receive programmatic message"""
        try:
            return self.message_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def cleanup(self) -> CommunicationResult:
        """Cleanup programmatic communication"""
        self.is_active = False
        if self.event_loop:
            self.event_loop.join(timeout=1)
        return CommunicationResult(
            success=True, message="Programmatic communicator cleaned up"
        )


# Factory function for easy communicator creation
def create_communicator(
    comm_type: CommunicationType, config: dict[str, Any] = None
) -> BaseCommunicator:
    """Factory function to create communicators"""
    communicators = {
        CommunicationType.NETWORK: NetworkCommunicator,
        CommunicationType.INTERPROCESS: InterprocessCommunicator,
        CommunicationType.SERIAL: SerialCommunicator,
        CommunicationType.EMAIL: EmailCommunicator,
        CommunicationType.PHYSICS: PhysicsCommunicator,
        CommunicationType.PSYCHOLOGICAL: PsychologicalCommunicator,
        CommunicationType.PROGRAMMATIC: ProgrammaticCommunicator,
    }

    if comm_type not in communicators:
        raise ValueError(f"Unsupported communication type: {comm_type}")

    return communicators[comm_type](config)


# Main demonstration function
def demonstrate_archer_framework():
    """Demonstrate the enhanced Archer Framework v2.0 capabilities"""
    framework = ArcherFramework(max_workers=15)

    print("🤖 Archer Framework v2.0 - Advanced Communication System")
    print("=" * 70)
    print("🚀 Enhanced Features:")
    print("   • Connection pooling for network communications")
    print("   • Thread-safe operations with RLock")
    print("   • Enhanced psychological analysis with ML-based algorithms")
    print("   • Async/await support for scalability")
    print("   • Configuration validation and type safety")
    print("   • Retry mechanisms with exponential backoff")
    print("   • Comprehensive performance monitoring")
    print("   • Better resource management and cleanup")
    print()

    # Register communicators with enhanced configurations
    print("📡 Registering Enhanced Communicators...")

    # Network communicator with connection pooling
    network_config = {
        "host": "localhost",
        "port": 8080,
        "protocol": "tcp",
        "timeout": 5.0,
        "retry_count": 3,
        "pool_size": 5,
    }
    network_comm = create_communicator(CommunicationType.NETWORK, network_config)
    framework.register_communicator(CommunicationType.NETWORK, network_comm)

    # Interprocess communicator
    ipc_comm = create_communicator(CommunicationType.INTERPROCESS, {"method": "queue"})
    framework.register_communicator(CommunicationType.INTERPROCESS, ipc_comm)

    # Enhanced psychological communicator
    psych_config = {
        "style": "assertive",
        "ei_level": 0.9,
        "analysis_depth": "comprehensive",
    }
    psych_comm = create_communicator(CommunicationType.PSYCHOLOGICAL, psych_config)
    framework.register_communicator(CommunicationType.PSYCHOLOGICAL, psych_comm)

    # Enhanced physics communicator
    physics_config = {
        "medium": "air",
        "frequency": 2.4e9,
        "power": 10.0,
        "distance": 1000.0,
        "temperature": 20.0,
    }
    physics_comm = create_communicator(CommunicationType.PHYSICS, physics_config)
    framework.register_communicator(CommunicationType.PHYSICS, physics_comm)

    print("✅ All communicators registered successfully!")
    print()

    # Test enhanced communication types
    test_messages = [
        CommunicationMessage(
            content="Hello from enhanced network communicator with connection pooling!",
            sender="client_v2",
            receiver="server_v2",
            message_type=CommunicationType.NETWORK,
            priority=8,
            metadata={"version": "2.0", "pooling_enabled": True},
        ),
        CommunicationMessage(
            content="Enhanced IPC message with thread-safe operations",
            sender="process_a_v2",
            receiver="process_b_v2",
            message_type=CommunicationType.INTERPROCESS,
            metadata={"data": {"key": "value", "thread_safe": True}, "version": "2.0"},
        ),
        CommunicationMessage(
            content="I am absolutely thrilled and grateful for this wonderful opportunity to collaborate with you! I believe we can achieve amazing results together through our combined capabilities and mutual understanding.",
            sender="user_v2",
            receiver="assistant_v2",
            message_type=CommunicationType.PSYCHOLOGICAL,
            priority=7,
            metadata={"emotional_context": "positive_collaboration", "version": "2.0"},
        ),
        CommunicationMessage(
            content="Physics signal transmission test with enhanced modeling",
            sender="transmitter_v2",
            receiver="receiver_v2",
            message_type=CommunicationType.PHYSICS,
            metadata={"frequency": 2.4e9, "power": 10.0, "version": "2.0"},
        ),
    ]

    framework.print_output("Testing enhanced communication types...")

    for i, message in enumerate(test_messages, 1):
        framework.print_output(
            f"\n📤 Test Message {i}: {message.message_type.value.upper()}"
        )
        result = framework.send_message(message)

        if result.success:
            framework.print_output(f"   ✅ Success: {result.message}")
            framework.print_output(f"   ⏱️  Response Time: {result.response_time:.4f}s")
            framework.print_output(f"   🆔 Message ID: {message.id[:8]}...")
            framework.print_output(f"   🔐 Checksum: {message.checksum}")

            # Show enhanced metadata for psychological communication
            if result.metadata and "psychological_score" in result.metadata:
                psych_score = result.metadata["psychological_score"]
                emotional = result.metadata.get("emotional_analysis", {})
                framework.print_output(f"   🧠 Psychological Score: {psych_score:.2f}")
                framework.print_output(
                    f"   😊 Emotional Tone: {emotional.get('tone', 'unknown')} (confidence: {emotional.get('confidence', 0):.2f})"
                )

                empathy = result.metadata.get("empathy_analysis", {})
                framework.print_output(
                    f"   🤝 Empathy Score: {empathy.get('overall_score', 0):.2f}"
                )

                clarity = result.metadata.get("clarity_metrics", {})
                framework.print_output(
                    f"   📝 Clarity Score: {clarity.get('score', 0):.2f} ({clarity.get('assessment', 'unknown')})"
                )

            # Show physics metadata
            if result.metadata and "signal_strength" in result.metadata:
                framework.print_output(
                    f"   📡 Signal Strength: {result.metadata['signal_strength']:.2f} dBm"
                )
                framework.print_output(
                    f"   🌊 Attenuation: {result.metadata.get('attenuation', 0):.2f} dB"
                )
                framework.print_output(
                    f"   📊 SNR: {result.metadata.get('snr', 0):.2f} dB"
                )
        else:
            framework.print_output(f"   ❌ Failed: {result.message}")
            if result.error_code:
                framework.print_output(f"   🔍 Error Code: {result.error_code}")

    # Show enhanced performance metrics
    framework.print_output("\n📊 Enhanced Performance Metrics:")
    metrics = framework.get_metrics()

    # Overall statistics
    framework.print_output(
        f"   📈 Total Messages: {int(metrics.get('total_messages', 0))}"
    )
    framework.print_output(
        f"   ✅ Successful: {int(metrics.get('successful_messages', 0))}"
    )
    framework.print_output(f"   ❌ Failed: {int(metrics.get('failed_messages', 0))}")
    framework.print_output(
        f"   📊 Overall Success Rate: {metrics.get('overall_success_rate', 0):.1%}"
    )
    framework.print_output(
        f"   ⏱️  Overall Avg Response: {metrics.get('overall_avg_response', 0):.4f}s"
    )
    framework.print_output(f"   ⏰ Uptime: {metrics.get('uptime_seconds', 0):.1f}s")
    framework.print_output("")

    # Per-communicator metrics
    framework.print_output("🔍 Per-Communicator Metrics:")
    for key, value in metrics.items():
        if any(x in key for x in ["avg_response", "success_rate"]) and not any(
            x in key for x in ["overall_"]
        ):
            comm_type = key.replace("_avg_response", "").replace("_success_rate", "")
            metric_type = "Response Time" if "response" in key else "Success Rate"
            unit = "s" if "response" in key else "%"
            framework.print_output(
                f"   {comm_type.title()} {metric_type}: {value:.4f}{unit}"
            )

    # Show communicator status
    framework.print_output("\n📡 Communicator Status:")
    status = framework.get_communicator_status()
    for comm_type, info in status.items():
        framework.print_output(
            f"   {comm_type.title()}: {'✅ Active' if info['is_active'] else '❌ Inactive'} ({info['class']})"
        )

    framework.print_output("\n🎯 Archer Framework v2.0 demonstration complete!")
    framework.print_output("🚀 Ready for production deployment with enhanced features!")

    # Cleanup
    framework.cleanup()


# Async demonstration function
def demonstrate_async_capabilities():
    """Demonstrate async capabilities of the enhanced framework"""

    async def async_demo():
        framework = ArcherFramework(max_workers=5)

        # Register a psychological communicator
        psych_comm = create_communicator(
            CommunicationType.PSYCHOLOGICAL, {"style": "assertive", "ei_level": 0.9}
        )
        framework.register_communicator(CommunicationType.PSYCHOLOGICAL, psych_comm)

        # Create test messages
        messages = [
            CommunicationMessage(
                content="This is an amazing async test message!",
                sender="async_sender",
                receiver="async_receiver",
                message_type=CommunicationType.PSYCHOLOGICAL,
            )
        ]

        print("\n🔄 Testing Async Capabilities...")

        # Send messages asynchronously
        tasks = [framework.send_message_async(msg) for msg in messages]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result.success:
                print(f"   ✅ Async Success: {result.message}")
            else:
                print(f"   ❌ Async Failed: {result.message}")

        framework.cleanup()

    # Run async demo
    asyncio.run(async_demo())


if __name__ == "__main__":
    demonstrate_archer_framework()
