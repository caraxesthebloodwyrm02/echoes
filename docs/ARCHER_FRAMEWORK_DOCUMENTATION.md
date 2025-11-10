# Archer Framework - Advanced Communication System

## Overview

The Archer Framework is a comprehensive, optimized communication model supporting multiple domains of communication. Built on the grounding principles of **Simplicity, Precision, Structure, Repetition, and Feedback**, it provides a unified interface for diverse communication needs.

## 🏗️ Architecture

### Core Components

1. **ArcherFramework** - Central orchestrator managing all communication types
2. **BaseCommunicator** - Abstract base class defining communication interface
3. **CommunicationMessage** - Standardized message structure with metadata
4. **CommunicationResult** - Result structure with performance metrics
5. **Communicator Implementations** - Domain-specific communication handlers

### Supported Communication Types

| Type | Description | Implementation |
|------|-------------|----------------|
| **Network** | TCP/UDP, HTTP client-server communication | `NetworkCommunicator` |
| **Interprocess** | Shared memory, pipes, message queues | `InterprocessCommunicator` |
| **Serial** | RS232, USB device communication | `SerialCommunicator` |
| **Email** | SMTP/IMAP email transmission | `EmailCommunicator` |
| **Physics** | Signal transmission through various media | `PhysicsCommunicator` |
| **Psychological** | Emotion-aware communication analysis | `PsychologicalCommunicator` |
| **Programmatic** | Event-driven, callback-based communication | `ProgrammaticCommunicator` |

## 🚀 Quick Start

### Basic Usage

```python
from communication import ArcherFramework, CommunicationMessage, CommunicationType, create_communicator

# Initialize framework
framework = ArcherFramework()

# Create and register communicators
network_comm = create_communicator(CommunicationType.NETWORK, {
    'host': 'localhost',
    'port': 8080,
    'protocol': 'tcp'
})
framework.register_communicator(CommunicationType.NETWORK, network_comm)

# Send message
message = CommunicationMessage(
    content="Hello World!",
    sender="client",
    receiver="server",
    message_type=CommunicationType.NETWORK
)

result = framework.send_message(message)
if result.success:
    framework.print_output(f"✅ Message sent: {result.message}")
else:
    framework.print_output(f"❌ Failed: {result.message}")
```

### Advanced Configuration

```python
# Psychological communication with emotional intelligence
psych_comm = create_communicator(CommunicationType.PSYCHOLOGICAL, {
    'style': 'assertive',
    'ei_level': 0.9
})

# Physics communication with custom medium
physics_comm = create_communicator(CommunicationType.PHYSICS, {
    'medium': 'fiber',
    'frequency': 1.55e9,  # 1.55 GHz
    'power': 10.0,        # 10 Watts
    'distance': 1000      # 1 km
})

# Email communication with SMTP settings
email_comm = create_communicator(CommunicationType.EMAIL, {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'your_email@gmail.com',
    'password': 'your_app_password'
})
```

## 📊 Features

### 1. **Unified Message Structure**

All communication types use the same `CommunicationMessage` structure:

```python
@dataclass
class CommunicationMessage:
    id: str                    # Unique identifier
    content: Any              # Message payload
    sender: str               # Sender identifier
    receiver: str             # Receiver identifier
    timestamp: float          # Creation timestamp
    message_type: CommunicationType  # Type of communication
    direction: CommunicationDirection  # Flow direction
    metadata: Dict[str, Any]  # Additional context
    priority: int             # 1-10 priority level
    requires_ack: bool        # Acknowledgment required
    encrypted: bool           # Encryption flag
    checksum: str             # Integrity verification
```

### 2. **Performance Monitoring**

Built-in performance metrics tracking:

- **Response Time**: Average response time per communication type
- **Success Rate**: Success percentage with exponential moving average
- **Message History**: Complete audit trail of all communications
- **Error Tracking**: Detailed error codes and messages

```python
# Get performance metrics
metrics = framework.get_metrics()
print(f"Network avg response: {metrics['network_avg_response']:.4f}s")
print(f"IPC success rate: {metrics['interprocess_success_rate']:.2%}")
```

### 3. **Graceful Error Handling**

Comprehensive error handling with detailed feedback:

```python
result = framework.send_message(message)
if not result.success:
    print(f"Error: {result.message}")
    print(f"Error Code: {result.error_code}")
    print(f"Response Time: {result.response_time:.4f}s")
```

### 4. **Extensible Architecture**

Easy to add new communication types:

```python
class CustomCommunicator(BaseCommunicator):
    def send(self, message: CommunicationMessage) -> CommunicationResult:
        # Custom implementation
        return CommunicationResult(success=True, message="Custom send successful")
    
    def receive(self, timeout: float = 5.0) -> Optional[CommunicationMessage]:
        # Custom receive logic
        return None
    
    def initialize(self) -> CommunicationResult:
        # Custom initialization
        return CommunicationResult(success=True, message="Custom initialized")
    
    def cleanup(self) -> CommunicationResult:
        # Custom cleanup
        return CommunicationResult(success=True, message="Custom cleaned up")

# Register custom communicator
framework.register_communicator(CommunicationType.CUSTOM, CustomCommunicator())
```

## 🔧 Communication Type Details

### Network Communication

- **Protocols**: TCP, UDP, HTTP
- **Features**: Auto-reconnection, timeout handling, JSON serialization
- **Use Cases**: Client-server applications, microservices, web APIs

```python
network_comm = create_communicator(CommunicationType.NETWORK, {
    'host': 'api.example.com',
    'port': 443,
    'protocol': 'tcp'
})
```

### Interprocess Communication

- **Methods**: Queues, Pipes, Shared Memory
- **Features**: Thread-safe operations, timeout support
- **Use Cases**: Process coordination, data sharing, parallel processing

```python
ipc_comm = create_communicator(CommunicationType.INTERPROCESS, {
    'method': 'queue'  # or 'pipe'
})
```

### Serial Communication

- **Standards**: RS232, USB, TTL
- **Features**: Configurable baud rates, timeout handling
- **Use Cases**: Hardware communication, IoT devices, sensors

```python
serial_comm = create_communicator(CommunicationType.SERIAL, {
    'port': 'COM3',
    'baudrate': 115200
})
```

### Email Communication

- **Protocols**: SMTP for sending, IMAP for receiving
- **Features**: TLS support, HTML/text messages
- **Use Cases**: Notifications, reports, automated messaging

```python
email_comm = create_communicator(CommunicationType.EMAIL, {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'sender@example.com',
    'password': 'app_password'
})
```

### Physics Communication

- **Media**: Air, Cable, Fiber, Vacuum
- **Features**: Signal strength calculation, attenuation modeling
- **Use Cases**: RF communication, optical transmission, signal analysis

```python
physics_comm = create_communicator(CommunicationType.PHYSICS, {
    'medium': 'fiber',
    'frequency': 1.55e9,
    'power': 10.0,
    'distance': 1000
})
```

### Psychological Communication

- **Styles**: Assertive, Passive, Aggressive
- **Features**: Emotional tone analysis, clarity assessment, empathy scoring
- **Use Cases**: User interfaces, chatbots, communication coaching

```python
psych_comm = create_communicator(CommunicationType.PSYCHOLOGICAL, {
    'style': 'assertive',
    'ei_level': 0.8
})
```

### Programmatic Communication

- **Patterns**: Events, Callbacks, Message Queues
- **Features**: Event handlers, background processing, async support
- **Use Cases**: Application events, plugin systems, reactive programming

```python
prog_comm = create_communicator(CommunicationType.PROGRAMMATIC)

# Register event handler
def handle_message(message: CommunicationMessage):
    print(f"Received: {message.content}")

prog_comm.register_handler('user_input', handle_message)
```

## 📈 Performance Optimization

### 1. **Connection Pooling**

Network connections are reused when possible to reduce overhead.

### 2. **Async Processing**

Background threads handle event processing and message queuing.

### 3. **Metrics Caching**

Performance metrics use exponential moving averages for efficiency.

### 4. **Memory Management**

Message history can be configured for automatic cleanup.

## 🛡️ Security Features

### 1. **Checksum Verification**

All messages include SHA-256 checksums for integrity verification.

### 2. **Encryption Support**

Messages can be flagged for encryption (implementation-dependent).

### 3. **Access Control**

Communicator registration provides controlled access to communication channels.

## 🧪 Testing

### Unit Tests

```python
import unittest
from communication import ArcherFramework, CommunicationMessage, CommunicationType

class TestArcherFramework(unittest.TestCase):
    def setUp(self):
        self.framework = ArcherFramework()
        
    def test_message_creation(self):
        message = CommunicationMessage(
            content="Test",
            sender="test_sender",
            receiver="test_receiver"
        )
        self.assertIsNotNone(message.id)
        self.assertIsNotNone(message.checksum)
        
    def test_framework_metrics(self):
        metrics = self.framework.get_metrics()
        self.assertIsInstance(metrics, dict)

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

```python
def test_ipc_communication():
    framework = ArcherFramework()
    ipc_comm = create_communicator(CommunicationType.INTERPROCESS, {'method': 'queue'})
    framework.register_communicator(CommunicationType.INTERPROCESS, ipc_comm)
    
    message = CommunicationMessage(
        content="IPC Test",
        sender="test_process",
        receiver="target_process",
        message_type=CommunicationType.INTERPROCESS
    )
    
    result = framework.send_message(message)
    assert result.success
    assert result.response_time < 1.0
```

## 📚 API Reference

### ArcherFramework

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `register_communicator()` | Register a communicator | `comm_type`, `communicator` | `None` |
| `send_message()` | Send a message | `message` | `CommunicationResult` |
| `get_metrics()` | Get performance metrics | None | `Dict[str, float]` |
| `print_output()` | Print formatted output | `message`, `level` | `None` |

### CommunicationMessage

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique identifier |
| `content` | `Any` | Message payload |
| `sender` | `str` | Sender identifier |
| `receiver` | `str` | Receiver identifier |
| `timestamp` | `float` | Creation timestamp |
| `message_type` | `CommunicationType` | Type of communication |
| `direction` | `CommunicationDirection` | Flow direction |
| `metadata` | `Dict[str, Any]` | Additional context |
| `priority` | `int` | Priority level (1-10) |
| `requires_ack` | `bool` | Acknowledgment required |
| `encrypted` | `bool` | Encryption flag |
| `checksum` | `str` | Integrity checksum |

### CommunicationResult

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Operation success status |
| `message` | `str` | Result message |
| `data` | `Any` | Additional data |
| `error_code` | `Optional[str]` | Error identifier |
| `response_time` | `float` | Operation duration |
| `metadata` | `Dict[str, Any]` | Additional metadata |

## 🔮 Future Enhancements

### Planned Features

1. **WebSocket Support** - Real-time bidirectional communication
2. **Message Queue Integration** - RabbitMQ, Apache Kafka support
3. **Advanced Encryption** - End-to-end encryption implementation
4. **Load Balancing** - Multiple server endpoint management
5. **Circuit Breaker** - Fault tolerance for distributed systems
6. **Message Persistence** - Database-backed message storage
7. **GraphQL Integration** - Query-based communication protocols
8. **Machine Learning** - Intelligent message routing and optimization

### Extension Points

- **Custom Communicators** - Easy addition of new communication types
- **Message Transformers** - Content processing and adaptation
- **Middleware Support** - Request/response interception
- **Plugin Architecture** - Modular feature extensions

## 🤝 Contributing

The Archer Framework follows these principles:

1. **Simplicity** - Keep APIs intuitive and documentation clear
2. **Precision** - Use type hints and comprehensive error handling
3. **Structure** - Maintain clean, modular architecture
4. **Repetition** - Apply consistent patterns across implementations
5. **Feedback** - Provide detailed result reporting and metrics

### Development Guidelines

- Follow PEP 8 style guidelines
- Include comprehensive docstrings
- Write unit tests for new features
- Update documentation for API changes
- Use semantic versioning for releases

## 📄 License

This framework is part of the Echoes project and follows the same licensing terms.

---

**Archer Framework** - Precision Communication for Complex Systems

*Built on the principles of Simplicity, Precision, Structure, Repetition, and Feedback*
