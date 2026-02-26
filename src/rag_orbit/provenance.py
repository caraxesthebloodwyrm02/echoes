from dataclasses import dataclass, field
from hashlib import md5
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ProvenanceRecord:
    record_id: str
    operation_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    parent_record_id: Optional[str] = None


class ProvenanceTracker:
    def __init__(self):
        self.records: Dict[str, ProvenanceRecord] = {}

    def _new_id(self, seed: str) -> str:
        return md5(seed.encode("utf-8")).hexdigest()

    def record_chunking(self, source_document: str, num_chunks: int, chunk_ids: List[str], chunker_config: Dict[str, Any], text_checksum: str):
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

    def record_retrieval(self, query: str, query_checksum: str, num_results: int, result_chunk_ids: List[str], retrieval_metrics: Dict[str, Any], parent_record_id: Optional[str] = None):
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

    def validate_record(self, record_id: str) -> Tuple[bool, Optional[str]]:
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
