# ----------------------------------------------------------------------
# Comprehensive test suite for the modular Echoes Assistant V2
# ----------------------------------------------------------------------
import tempfile

import pytest

from echoes import EchoesAssistantV2, RuntimeOptions
from echoes.models.items import Draft, InventoryItem
from echoes.services.filesystem import FilesystemTools
from echoes.services.inventory import InventoryService
from echoes.services.knowledge import KnowledgeManager
from echoes.services.quantum import QuantumStateManager
from echoes.utils.context_manager import ContextManager
from echoes.utils.import_helpers import safe_import
from echoes.utils.memory_store import MemoryStore
from echoes.utils.status_indicator import EnhancedStatusIndicator


class TestImportHelpers:
    """Test the safe_import utility."""

    def test_safe_import_success(self):
        """Test successful import."""
        os_module, available = safe_import("os")
        assert available is True
        assert hasattr(os_module, "path")

    def test_safe_import_failure(self):
        """Test failed import with fallback."""
        fake_module, available = safe_import("nonexistent_module_xyz")
        assert available is False
        assert fake_module is not None  # Should return SimpleNamespace

    def test_safe_import_with_fallback(self):
        """Test import with custom fallback."""
        fallback = {"custom": "data"}
        module, available = safe_import("nonexistent_module", fallback)
        assert available is False
        assert module == fallback


class TestStatusIndicator:
    """Test the status indicator utility."""

    def test_status_indicator_creation(self):
        """Test status indicator initialization."""
        indicator = EnhancedStatusIndicator(enabled=False)
        assert indicator.enabled is False
        assert indicator.current_phase is None

    def test_status_indicator_disabled(self):
        """Test that disabled indicator doesn't print."""
        indicator = EnhancedStatusIndicator(enabled=False)
        # These should not raise errors or print anything
        indicator.start_phase("test")
        indicator.update_step("testing")
        indicator.complete_phase("done")
        indicator.error("error")


class TestContextManager:
    """Test the context manager."""

    def test_context_manager_creation(self):
        """Test context manager initialization."""
        manager = ContextManager()
        assert isinstance(manager.conversations, dict)

    def test_add_and_get_messages(self):
        """Test adding and retrieving messages."""
        manager = ContextManager()
        session_id = "test_session"

        manager.add_message(session_id, "user", "Hello")
        manager.add_message(session_id, "assistant", "Hi there!")

        messages = manager.get_messages(session_id)
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"

    def test_clear_session(self):
        """Test clearing a session."""
        manager = ContextManager()
        session_id = "test_session"

        manager.add_message(session_id, "user", "Hello")
        assert len(manager.get_messages(session_id)) == 1

        manager.clear_session(session_id)
        assert len(manager.get_messages(session_id)) == 0


class TestMemoryStore:
    """Test the memory store."""

    def test_memory_store_creation(self, tmp_path):
        """Test memory store initialization."""
        store = MemoryStore(storage_dir=str(tmp_path))
        assert store.storage_dir == tmp_path

    def test_save_and_load_conversation(self, tmp_path):
        """Test saving and loading conversations."""
        store = MemoryStore(storage_dir=str(tmp_path))
        session_id = "test_session"
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]

        # Save conversation
        success = store.save_conversation(session_id, messages)
        assert success is True

        # Load conversation
        loaded = store.load_conversation(session_id)
        assert loaded == messages

    def test_list_sessions(self, tmp_path):
        """Test listing sessions."""
        store = MemoryStore(storage_dir=str(tmp_path))

        # Save multiple sessions
        store.save_conversation("session1", [{"role": "user", "content": "test1"}])
        store.save_conversation("session2", [{"role": "user", "content": "test2"}])

        sessions = store.list_sessions()
        assert set(sessions) == {"session1", "session2"}


class TestInventoryService:
    """Test the inventory service."""

    def test_add_and_get_item(self):
        """Test adding and retrieving items."""
        service = InventoryService()

        item = service.add_item(
            sku="TEST-001",
            name="Test Item",
            category="Testing",
            quantity=10,
            location="Warehouse",
        )

        assert isinstance(item, InventoryItem)
        assert item.sku == "TEST-001"
        assert item.name == "Test Item"

        # Retrieve item
        retrieved = service.get_item("TEST-001")
        assert retrieved.sku == item.sku
        assert retrieved.name == item.name

    def test_update_item(self):
        """Test updating items."""
        service = InventoryService()

        # Add item
        service.add_item("TEST-002", "Original", "Testing", 5, "A")

        # Update item
        updated = service.update_item("TEST-002", quantity=15, name="Updated")
        assert updated is not None
        assert updated.quantity == 15
        assert updated.name == "Updated"

    def test_search_items(self):
        """Test searching items."""
        service = InventoryService()

        service.add_item("SEARCH-001", "Widget A", "Hardware", 5, "A")
        service.add_item("SEARCH-002", "Widget B", "Hardware", 10, "B")
        service.add_item("SEARCH-003", "Gadget A", "Electronics", 3, "C")

        # Search by name
        results = service.search_items("Widget")
        assert len(results) == 2

        # Search by category
        results = service.search_items("Electronics")
        assert len(results) == 1


class TestKnowledgeManager:
    """Test the knowledge manager."""

    def test_add_and_get_knowledge(self):
        """Test adding and retrieving knowledge."""
        manager = KnowledgeManager()

        success = manager.add_knowledge("test_key", "test_value", {"type": "test"})
        assert success is True

        value = manager.get_knowledge("test_key")
        assert value == "test_value"

    def test_search_knowledge(self):
        """Test searching knowledge."""
        manager = KnowledgeManager()

        manager.add_knowledge("python", "Programming language", {"type": "language"})
        manager.add_knowledge("javascript", "Web language", {"type": "language"})
        manager.add_knowledge("database", "Data storage", {"type": "system"})

        results = manager.search_knowledge("language")
        assert len(results) == 2

        results = manager.search_knowledge("python")
        assert len(results) == 1
        assert results[0]["key"] == "python"


class TestFilesystemTools:
    """Test the filesystem tools."""

    def test_file_operations(self, tmp_path):
        """Test basic file operations."""
        tools = FilesystemTools(root_dir=str(tmp_path))

        # Write file
        content = "Hello, World!"
        success = tools.write_file("test.txt", content)
        assert success is True

        # Read file
        read_content = tools.read_file("test.txt")
        assert read_content == content

        # Get file info
        info = tools.get_file_info("test.txt")
        assert info is not None
        assert info["is_file"] is True
        assert info["size"] == len(content)

        # Delete file
        success = tools.delete_file("test.txt")
        assert success is True

    def test_directory_operations(self, tmp_path):
        """Test directory operations."""
        tools = FilesystemTools(root_dir=str(tmp_path))

        # Create directory
        success = tools.create_directory("test_dir")
        assert success is True

        # List directories
        dirs = tools.list_directories()
        assert "test_dir" in dirs

        # Create file in directory
        tools.write_file("test_dir/test.txt", "content")

        # List files
        files = tools.list_files("test_dir")
        assert len(files) == 1
        assert "test_dir/test.txt" in files

        # Delete directory
        success = tools.delete_directory("test_dir")
        assert success is True


class TestQuantumStateManager:
    """Test the quantum state manager."""

    def test_initialization(self):
        """Test quantum state initialization."""
        manager = QuantumStateManager()

        success = manager.initialize_quantum_states()
        assert success is True
        assert manager.initialized is True

    def test_state_operations(self):
        """Test quantum state operations."""
        manager = QuantumStateManager()
        manager.initialize_quantum_states()

        # Get state
        state = manager.get_quantum_state("superposition")
        assert state is not None
        assert "active" in state

        # Set state
        new_state = {"active": True, "coherence": 0.9}
        success = manager.set_quantum_state("superposition", new_state)
        assert success is True

        # Verify updated state
        updated = manager.get_quantum_state("superposition")
        assert updated["coherence"] == 0.9

    def test_entanglement(self):
        """Test quantum entanglement."""
        manager = QuantumStateManager()
        manager.initialize_quantum_states()

        success = manager.create_entanglement("state1", "state2")
        assert success is True

        metrics = manager.get_quantum_metrics()
        assert metrics["total_states"] >= 1


class TestEchoesAssistantV2:
    """Test the main EchoesAssistantV2 class."""

    def test_assistant_creation_minimal(self):
        """Test creating assistant with minimal configuration."""
        opts = RuntimeOptions(
            enable_rag=False,
            enable_glimpse=False,
            enable_multimodal=False,
            enable_legal=False,
            enable_tools=False,
        )

        # Should not raise an error even without optional dependencies
        assistant = EchoesAssistantV2(opts=opts)

        assert assistant.session_id is not None
        assert assistant.model is not None
        assert assistant.context_manager is not None
        assert assistant.memory_store is not None

    def test_assistant_creation_full(self):
        """Test creating assistant with all features enabled."""
        opts = RuntimeOptions(
            enable_rag=True,
            enable_glimpse=True,
            enable_multimodal=True,
            enable_legal=True,
            enable_tools=True,
        )

        # Should work with fallbacks when dependencies are missing
        assistant = EchoesAssistantV2(opts=opts)

        assert assistant.enable_rag is not None  # May be False if RAG not available
        assert assistant.enable_glimpse is True
        assert assistant.inventory_service is not None
        assert assistant.knowledge_manager is not None

    def test_knowledge_operations(self):
        """Test assistant knowledge operations."""
        assistant = EchoesAssistantV2()

        success = assistant.add_knowledge("test", "value", {"meta": "data"})
        assert success is True

        value = assistant.knowledge_manager.get_knowledge("test")
        assert value == "value"

    def test_conversation_history(self):
        """Test conversation history management."""
        assistant = EchoesAssistantV2()

        # Initially empty
        history = assistant.get_conversation_history()
        assert isinstance(history, list)

        # Clear session should work
        success = assistant.clear_session()
        assert success is True

    def test_get_stats(self):
        """Test getting assistant statistics."""
        assistant = EchoesAssistantV2()

        stats = assistant.get_stats()
        assert isinstance(stats, dict)
        assert "session_id" in stats
        assert "model" in stats
        assert "features" in stats
        assert "conversation_length" in stats


class TestModels:
    """Test the data models."""

    def test_inventory_item(self):
        """Test InventoryItem model."""
        item = InventoryItem(
            sku="TEST-001",
            name="Test Item",
            category="Testing",
            quantity=10,
            location="Warehouse",
        )

        assert item.sku == "TEST-001"
        assert item.min_stock == 0  # Default value

        # Test to_dict conversion
        item_dict = item.to_dict()
        assert isinstance(item_dict, dict)
        assert item_dict["sku"] == "TEST-001"

    def test_draft_model(self):
        """Test Draft model."""
        draft = Draft(
            input_text="Test input", goal="Test goal", constraints="Test constraints"
        )

        assert draft.input_text == "Test input"
        assert draft.goal == "Test goal"
        assert draft.constraints == "Test constraints"


# Integration tests
class TestIntegration:
    """Integration tests for the complete system."""

    def test_full_workflow(self):
        """Test a complete workflow with multiple components."""
        # Create assistant
        opts = RuntimeOptions(
            enable_rag=False, enable_glimpse=False, enable_tools=False
        )
        assistant = EchoesAssistantV2(opts=opts)

        # Add knowledge
        assistant.add_knowledge("project", "Echoes V2", {"type": "metadata"})

        # Use inventory
        item = assistant.inventory_service.add_item(
            "ECHOES-001", "Core Module", "Software", 1, "Main"
        )

        # Use filesystem (in temp directory)
        with tempfile.TemporaryDirectory() as tmp_dir:
            fs_tools = FilesystemTools(root_dir=tmp_dir)
            fs_tools.write_file("test.txt", "Integration test")

            # Verify file exists
            info = fs_tools.get_file_info("test.txt")
            assert info is not None

        # Get stats
        stats = assistant.get_stats()
        assert stats["knowledge_items"] >= 1

        # Verify all components are working
        assert assistant.knowledge_manager.get_knowledge("project") == "Echoes V2"
        assert assistant.inventory_service.get_item("ECHOES-001") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
