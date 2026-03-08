import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass
class ProvenanceRecord:
    record_id: str
    operation_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    parent_record_id: str | None = None

    @property
    def outputs(self) -> dict[str, Any]:
        return self.payload

    @property
    def inputs(self) -> dict[str, Any]:
        return self.payload


class ProvenanceTracker:
    def __init__(self, storage_path: Path | str | None = None):
        self.storage_path = Path(storage_path) if storage_path else None
        self.session_id = str(uuid4())
        self.records: dict[str, ProvenanceRecord] = {}

    def get_record(self, record_id: str) -> ProvenanceRecord | None:
        return self.records.get(record_id)

    def _new_id(self, seed: str) -> str:
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()

    def record_chunking(
        self,
        source_document: str,
        num_chunks: int,
        chunk_ids: list[str],
        chunker_config: dict[str, Any],
        text_checksum: str,
    ):
        rid = self._new_id(f"chunk:{source_document}:{num_chunks}:{text_checksum}")
        self.records[rid] = ProvenanceRecord(
            record_id=rid,
            operation_type="chunk",
            payload={
                "source_document": source_document,
                "num_chunks": num_chunks,
                "chunk_ids": chunk_ids,
                "chunker_config": chunker_config,
                "text_checksum": text_checksum,
            },
        )
        return rid

    def record_embedding(
        self,
        chunk_id: str,
        text_checksum: str,
        model_name: str,
        embedding_checksum: str,
        parent_record_id: str | None = None,
    ) -> str:
        rid = self._new_id(f"embed:{chunk_id}:{text_checksum}:{embedding_checksum}")
        self.records[rid] = ProvenanceRecord(
            record_id=rid,
            operation_type="embed",
            payload={
                "chunk_id": chunk_id,
                "text_checksum": text_checksum,
                "model_name": model_name,
                "embedding_checksum": embedding_checksum,
            },
            parent_record_id=parent_record_id,
        )
        return rid

    def record_retrieval(
        self,
        query: str,
        query_checksum: str,
        num_results: int,
        result_chunk_ids: list[str],
        retrieval_metrics: dict[str, Any],
        parent_record_id: str | None = None,
    ):
        rid = self._new_id(f"retrieve:{query}:{query_checksum}:{num_results}")
        self.records[rid] = ProvenanceRecord(
            record_id=rid,
            operation_type="retrieve",
            payload={
                "query": query,
                "query_checksum": query_checksum,
                "num_results": num_results,
                "result_chunk_ids": result_chunk_ids,
                "retrieval_metrics": retrieval_metrics,
            },
            parent_record_id=parent_record_id,
        )
        return rid

    def validate_record(self, record_id: str) -> tuple[bool, str | None]:
        if record_id not in self.records:
            return False, "record_not_found"
        return True, None

    def get_lineage(self, record_id: str):
        lineage = []
        current = self.records.get(record_id)
        while current is not None:
            lineage.insert(0, current)
            if current.parent_record_id is None:
                break
            current = self.records.get(current.parent_record_id)
        return lineage

    def export_session(self, export_path: Path | str) -> None:
        path = Path(export_path)
        data = {
            "session_id": self.session_id,
            "num_records": len(self.records),
            "records": [
                {
                    "record_id": r.record_id,
                    "operation_type": r.operation_type,
                    "payload": r.payload,
                    "parent_record_id": r.parent_record_id,
                }
                for r in self.records.values()
            ],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
