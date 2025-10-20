"""
Provenance tracking module for RAG Orbit.

Maintains complete audit trail of all RAG operations with SHA-256 checksums,
timestamps, and operation metadata for reproducibility and validation.
"""

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid


@dataclass
class ProvenanceRecord:
    """A single provenance record for an operation."""

    record_id: str
    operation_type: str  # "chunk", "embed", "retrieve", "generate"
    timestamp: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    checksums: Dict[str, str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_records: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def compute_record_checksum(self) -> str:
        """Compute checksum of entire record."""
        # Serialize record (excluding checksums field itself)
        record_data = {
            "record_id": self.record_id,
            "operation_type": self.operation_type,
            "timestamp": self.timestamp,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "metadata": self.metadata,
            "parent_records": self.parent_records,
        }
        serialized = json.dumps(record_data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class ProvenanceTracker:
    """
    Tracks provenance of all RAG operations.

    Maintains a directed acyclic graph (DAG) of operations where each
    operation links to its parent operations, enabling full lineage tracking.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize provenance tracker.

        Args:
            storage_path: Path to store provenance records (optional)
        """
        self.storage_path = storage_path or Path(".cache/provenance")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.records: Dict[str, ProvenanceRecord] = {}
        self.session_id = str(uuid.uuid4())

    def record_chunking(
        self,
        source_document: str,
        num_chunks: int,
        chunk_ids: List[str],
        chunker_config: Dict[str, Any],
        text_checksum: str,
    ) -> str:
        """
        Record a chunking operation.

        Returns:
            Record ID
        """
        record_id = str(uuid.uuid4())

        record = ProvenanceRecord(
            record_id=record_id,
            operation_type="chunk",
            timestamp=datetime.now(timezone.utc).isoformat(),
            inputs={
                "source_document": source_document,
                "text_checksum": text_checksum,
            },
            outputs={
                "num_chunks": num_chunks,
                "chunk_ids": chunk_ids,
            },
            checksums={
                "text": text_checksum,
            },
            metadata={
                "chunker_config": chunker_config,
                "session_id": self.session_id,
            },
        )

        # Add record checksum
        record.checksums["record"] = record.compute_record_checksum()

        self.records[record_id] = record
        self._persist_record(record)

        return record_id

    def record_embedding(
        self,
        chunk_id: str,
        text_checksum: str,
        model_name: str,
        embedding_checksum: str,
        parent_record_id: Optional[str] = None,
    ) -> str:
        """
        Record an embedding operation.

        Returns:
            Record ID
        """
        record_id = str(uuid.uuid4())

        parents = [parent_record_id] if parent_record_id else []

        record = ProvenanceRecord(
            record_id=record_id,
            operation_type="embed",
            timestamp=datetime.now(timezone.utc).isoformat(),
            inputs={
                "chunk_id": chunk_id,
                "text_checksum": text_checksum,
                "model_name": model_name,
            },
            outputs={
                "embedding_checksum": embedding_checksum,
            },
            checksums={
                "text": text_checksum,
                "embedding": embedding_checksum,
            },
            metadata={
                "session_id": self.session_id,
            },
            parent_records=parents,
        )

        record.checksums["record"] = record.compute_record_checksum()

        self.records[record_id] = record
        self._persist_record(record)

        return record_id

    def record_retrieval(
        self,
        query: str,
        query_checksum: str,
        num_results: int,
        result_chunk_ids: List[str],
        retrieval_metrics: Dict[str, Any],
        parent_record_id: Optional[str] = None,
    ) -> str:
        """
        Record a retrieval operation.

        Returns:
            Record ID
        """
        record_id = str(uuid.uuid4())

        parents = [parent_record_id] if parent_record_id else []

        record = ProvenanceRecord(
            record_id=record_id,
            operation_type="retrieve",
            timestamp=datetime.now(timezone.utc).isoformat(),
            inputs={
                "query": query[:100],  # Truncate for storage
                "query_checksum": query_checksum,
            },
            outputs={
                "num_results": num_results,
                "result_chunk_ids": result_chunk_ids,
            },
            checksums={
                "query": query_checksum,
            },
            metadata={
                "retrieval_metrics": retrieval_metrics,
                "session_id": self.session_id,
            },
            parent_records=parents,
        )

        record.checksums["record"] = record.compute_record_checksum()

        self.records[record_id] = record
        self._persist_record(record)

        return record_id

    def record_generation(
        self,
        prompt: str,
        response: str,
        model_name: str,
        context_chunk_ids: List[str],
        parent_record_ids: List[str],
    ) -> str:
        """
        Record a generation operation.

        Returns:
            Record ID
        """
        record_id = str(uuid.uuid4())

        prompt_checksum = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        response_checksum = hashlib.sha256(response.encode("utf-8")).hexdigest()

        record = ProvenanceRecord(
            record_id=record_id,
            operation_type="generate",
            timestamp=datetime.now(timezone.utc).isoformat(),
            inputs={
                "prompt": prompt[:200],  # Truncate
                "prompt_checksum": prompt_checksum,
                "model_name": model_name,
                "context_chunk_ids": context_chunk_ids,
            },
            outputs={
                "response": response[:500],  # Truncate
                "response_checksum": response_checksum,
            },
            checksums={
                "prompt": prompt_checksum,
                "response": response_checksum,
            },
            metadata={
                "session_id": self.session_id,
            },
            parent_records=parent_record_ids,
        )

        record.checksums["record"] = record.compute_record_checksum()

        self.records[record_id] = record
        self._persist_record(record)

        return record_id

    def get_record(self, record_id: str) -> Optional[ProvenanceRecord]:
        """Retrieve a record by ID."""
        return self.records.get(record_id)

    def get_lineage(self, record_id: str) -> List[ProvenanceRecord]:
        """
        Get full lineage (ancestry) of a record.

        Returns records in topological order (parents before children).
        """
        lineage: List[ProvenanceRecord] = []
        visited: set = set()

        def traverse(rid: str) -> None:
            if rid in visited or rid not in self.records:
                return

            visited.add(rid)
            record = self.records[rid]

            # Traverse parents first
            for parent_id in record.parent_records:
                traverse(parent_id)

            lineage.append(record)

        traverse(record_id)
        return lineage

    def validate_record(self, record_id: str) -> tuple[bool, Optional[str]]:
        """
        Validate a record's integrity.

        Returns:
            (is_valid, error_message)
        """
        record = self.records.get(record_id)
        if not record:
            return False, f"Record {record_id} not found"

        # Recompute record checksum
        computed = record.compute_record_checksum()
        stored = record.checksums.get("record", "")

        if computed != stored:
            return False, f"Checksum mismatch: expected {stored}, got {computed}"

        # Validate parent records exist
        for parent_id in record.parent_records:
            if parent_id not in self.records:
                return False, f"Parent record {parent_id} not found"

        return True, None

    def export_session(self, output_path: Path) -> None:
        """Export all records from current session."""
        session_records = [
            r.to_dict() for r in self.records.values() if r.metadata.get("session_id") == self.session_id
        ]

        with open(output_path, "w") as f:
            json.dump(
                {
                    "session_id": self.session_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "num_records": len(session_records),
                    "records": session_records,
                },
                f,
                indent=2,
            )

    def _persist_record(self, record: ProvenanceRecord) -> None:
        """Persist a single record to disk."""
        record_path = self.storage_path / f"{record.record_id}.json"
        with open(record_path, "w") as f:
            json.dump(record.to_dict(), f, indent=2)

    def load_session(self, session_path: Path) -> None:
        """Load a previously exported session."""
        with open(session_path, "r") as f:
            data = json.load(f)

        for record_dict in data["records"]:
            record = ProvenanceRecord(**record_dict)
            self.records[record.record_id] = record
