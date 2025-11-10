"""
Catch and Release System - Intelligent caching for quick cross-referencing
Maintains conversation continuity while enabling rapid context switching and retrieval
"""

import hashlib
import json
import logging
import pickle
import threading
import time
from collections import OrderedDict, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Levels of caching with different retention policies"""

    SESSION = "session"  # Current session only
    SHORT_TERM = "short_term"  # Few hours
    LONG_TERM = "long_term"  # Days to weeks
    PERMANENT = "permanent"  # Until manually cleared


class ContentType(Enum):
    """Types of content that can be cached"""

    CONVERSATION = "conversation"
    ENTITY = "entity"
    CONCEPT = "concept"
    THOUGHT_CHAIN = "thought_chain"
    CROSS_REFERENCE = "cross_reference"
    CONTEXT = "context"
    RESPONSE = "response"
    PATTERN = "pattern"


@dataclass
class CacheEntry:
    """A cached entry with metadata"""

    key: str
    content: Any
    content_type: ContentType
    cache_level: CacheLevel
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0
    tags: set[str] = field(default_factory=set)
    related_keys: set[str] = field(default_factory=set)
    importance_score: float = 0.5
    expiration: datetime | None = None

    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at
        if self.size_bytes == 0:
            self.size_bytes = len(pickle.dumps(self.content))


@dataclass
class CrossReferenceResult:
    """Result of a cross-reference lookup"""

    content: Any
    source_key: str
    relevance_score: float
    context_info: dict[str, Any]
    retrieval_path: list[str]
    confidence: float


class LRUCache:
    """Thread-safe LRU cache implementation"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any | None:
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                value = self.cache.pop(key)
                self.cache[key] = value
                self.hits += 1
                return value
            else:
                self.misses += 1
                return None

    def put(self, key: str, value: Any):
        with self.lock:
            if key in self.cache:
                # Update existing
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # Remove least recently used
                self.cache.popitem(last=False)

            self.cache[key] = value

    def remove(self, key: str) -> bool:
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False

    def clear(self):
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0

    def get_stats(self) -> dict[str, Any]:
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
            }


class CatchAndReleaseSystem:
    """Intelligent caching system for quick cross-referencing and continuity"""

    def __init__(self, max_cache_size: int = 5000, default_ttl_hours: int = 24):
        # Multi-level caching
        self.session_cache = LRUCache(max_size=1000)
        self.short_term_cache = LRUCache(max_size=2000)
        self.long_term_cache = LRUCache(max_size=2000)
        self.permanent_cache = LRUCache(max_size=1000)

        # Cross-reference index
        self.entity_index = defaultdict(set)  # entity -> cache keys
        self.concept_index = defaultdict(set)  # concept -> cache keys
        self.tag_index = defaultdict(set)  # tag -> cache keys
        self.temporal_index = defaultdict(list)  # time bucket -> cache keys

        # Relationship tracking
        self.relationship_graph = defaultdict(set)  # key -> related keys

        # Configuration
        self.default_ttl = timedelta(hours=default_ttl_hours)
        self.max_cache_size = max_cache_size

        # Statistics
        self.stats = {
            "total_catches": 0,
            "total_releases": 0,
            "cross_references": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "evictions": 0,
        }

        # Cleanup thread
        self.cleanup_thread = None
        self.running = True
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """Start background cleanup thread"""

        def cleanup():
            while self.running:
                try:
                    self._cleanup_expired_entries()
                    time.sleep(300)  # Cleanup every 5 minutes
                except Exception as e:
                    logger.warning(f"Cleanup thread error: {e}")

        self.cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        self.cleanup_thread.start()

    def _generate_cache_key(
        self, content: Any, content_type: ContentType, context: dict[str, Any] = None
    ) -> str:
        """Generate a unique cache key for content"""
        # Create a deterministic key based on content and context
        key_data = {
            "content_hash": hashlib.md5(str(content).encode()).hexdigest()[:16],
            "type": content_type.value,
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]

    def catch(
        self,
        content: Any,
        content_type: ContentType,
        cache_level: CacheLevel = CacheLevel.SHORT_TERM,
        tags: set[str] = None,
        importance: float = 0.5,
        context: dict[str, Any] = None,
        ttl_hours: int | None = None,
    ) -> str:
        """Catch and cache content for quick retrieval"""

        # Generate cache key
        cache_key = self._generate_cache_key(content, content_type, context)

        # Create cache entry
        now = datetime.now()
        expiration = (
            now + timedelta(hours=ttl_hours) if ttl_hours else (now + self.default_ttl)
        )

        entry = CacheEntry(
            key=cache_key,
            content=content,
            content_type=content_type,
            cache_level=cache_level,
            created_at=now,
            last_accessed=now,
            tags=tags or set(),
            importance_score=importance,
            expiration=expiration if cache_level != CacheLevel.PERMANENT else None,
        )

        # Store in appropriate cache
        cache = self._get_cache_by_level(cache_level)
        cache.put(cache_key, entry)

        # Update indexes
        self._update_indexes(entry, context)

        # Update statistics
        self.stats["total_catches"] += 1

        logger.debug(f"Caught content: {cache_key} ({content_type.value})")
        return cache_key

    def release(self, cache_key: str, update_access: bool = True) -> Any | None:
        """Release (retrieve) cached content"""

        # Try all caches in order of priority
        for cache in [
            self.session_cache,
            self.short_term_cache,
            self.long_term_cache,
            self.permanent_cache,
        ]:
            entry = cache.get(cache_key)
            if entry:
                # Update access statistics
                if update_access:
                    entry.last_accessed = datetime.now()
                    entry.access_count += 1
                    # Put back to update LRU order
                    cache.put(cache_key, entry)

                self.stats["total_releases"] += 1
                self.stats["cache_hits"] += 1

                logger.debug(f"Released content: {cache_key}")
                return entry.content

        self.stats["cache_misses"] += 1
        logger.debug(f"Cache miss: {cache_key}")
        return None

    def cross_reference(
        self,
        query: str,
        content_types: list[ContentType] = None,
        max_results: int = 10,
        min_relevance: float = 0.3,
    ) -> list[CrossReferenceResult]:
        """Quick cross-reference lookup across cached content"""

        results = []
        query.lower()

        # Search all caches
        all_entries = []
        for cache in [
            self.session_cache,
            self.short_term_cache,
            self.long_term_cache,
            self.permanent_cache,
        ]:
            for _key, entry in cache.cache.items():
                if not content_types or entry.content_type in content_types:
                    all_entries.append(entry)

        # Calculate relevance scores
        for entry in all_entries:
            relevance = self._calculate_relevance(query, entry)
            if relevance >= min_relevance:
                # Build retrieval path
                path = self._build_retrieval_path(entry.key)

                result = CrossReferenceResult(
                    content=entry.content,
                    source_key=entry.key,
                    relevance_score=relevance,
                    context_info={
                        "type": entry.content_type.value,
                        "tags": list(entry.tags),
                        "created_at": entry.created_at.isoformat(),
                        "access_count": entry.access_count,
                        "importance": entry.importance_score,
                    },
                    retrieval_path=path,
                    confidence=min(relevance * entry.importance_score, 1.0),
                )
                results.append(result)

        # Sort by relevance and return top results
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        self.stats["cross_references"] += 1

        logger.debug(f"Cross-reference for '{query}': {len(results)} results")
        return results[:max_results]

    def _calculate_relevance(self, query: str, entry: CacheEntry) -> float:
        """Calculate relevance score for query against cached entry"""
        query_lower = query.lower()
        content_str = str(entry.content).lower()

        # Text matching
        text_score = 0.0
        if query_lower in content_str:
            text_score = 0.8
        else:
            # Partial word matching
            query_words = query_lower.split()
            content_words = content_str.split()
            matches = sum(
                1 for qw in query_words if any(qw in cw for cw in content_words)
            )
            text_score = matches / max(len(query_words), 1) * 0.5

        # Tag matching
        tag_score = 0.0
        for tag in entry.tags:
            if query_lower in tag.lower():
                tag_score = 0.3

        # Recency bonus
        recency_bonus = 0.0
        time_diff = datetime.now() - entry.created_at
        if time_diff < timedelta(hours=1):
            recency_bonus = 0.2
        elif time_diff < timedelta(days=1):
            recency_bonus = 0.1

        # Importance bonus
        importance_bonus = entry.importance_score * 0.2

        # Frequency bonus
        frequency_bonus = min(entry.access_count / 10.0, 0.2)

        total_score = (
            text_score + tag_score + recency_bonus + importance_bonus + frequency_bonus
        )
        return min(total_score, 1.0)

    def _build_retrieval_path(self, cache_key: str) -> list[str]:
        """Build the retrieval path for a cache entry"""
        path = [cache_key]

        # Add related keys
        related = self.relationship_graph.get(cache_key, set())
        path.extend(list(related)[:3])  # Limit to 3 related keys

        return path

    def _get_cache_by_level(self, level: CacheLevel) -> LRUCache:
        """Get the appropriate cache for a given level"""
        mapping = {
            CacheLevel.SESSION: self.session_cache,
            CacheLevel.SHORT_TERM: self.short_term_cache,
            CacheLevel.LONG_TERM: self.long_term_cache,
            CacheLevel.PERMANENT: self.permanent_cache,
        }
        return mapping.get(level, self.short_term_cache)

    def _update_indexes(self, entry: CacheEntry, context: dict[str, Any] = None):
        """Update search indexes for a cache entry"""
        content_str = str(entry.content).lower()

        # Entity indexing
        if context and "entities" in context:
            for entity in context["entities"]:
                self.entity_index[entity.lower()].add(entry.key)

        # Concept indexing (simple keyword extraction)
        concepts = self._extract_concepts(content_str)
        for concept in concepts:
            self.concept_index[concept].add(entry.key)

        # Tag indexing
        for tag in entry.tags:
            self.tag_index[tag.lower()].add(entry.key)

        # Temporal indexing
        time_bucket = entry.created_at.strftime("%Y%m%d_%H")  # Hour buckets
        self.temporal_index[time_bucket].append(entry.key)

    def _extract_concepts(self, text: str) -> list[str]:
        """Extract key concepts from text"""
        # Simple concept extraction - could be enhanced with NLP
        import re

        # Find potential concepts (capitalized words, technical terms)
        concepts = []

        # Technical terms
        tech_terms = re.findall(
            r"\b(AI|ML|API|SQL|JSON|XML|HTML|CSS|JS|Python|Java|C\+\+|React|Vue|Angular|Docker|Kubernetes|AWS|Azure|GCP)\b",
            text,
            re.IGNORECASE,
        )
        concepts.extend(tech_terms)

        # Capitalized terms (potential concepts)
        cap_terms = re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b", text)
        concepts.extend(cap_terms)

        # Return unique concepts
        return list({c.lower() for c in concepts if len(c) > 2})

    def find_related(
        self, cache_key: str, max_depth: int = 2
    ) -> list[CrossReferenceResult]:
        """Find related cached content"""

        visited = set()
        results = []

        def traverse(key: str, depth: int):
            if depth > max_depth or key in visited:
                return

            visited.add(key)

            # Get entry
            entry = None
            for cache in [
                self.session_cache,
                self.short_term_cache,
                self.long_term_cache,
                self.permanent_cache,
            ]:
                entry = cache.get(key)
                if entry:
                    break

            if entry and depth > 0:  # Don't include the original entry
                result = CrossReferenceResult(
                    content=entry.content,
                    source_key=key,
                    relevance_score=1.0
                    - (depth * 0.2),  # Decrease relevance with depth
                    context_info={
                        "type": entry.content_type.value,
                        "depth": depth,
                        "created_at": entry.created_at.isoformat(),
                    },
                    retrieval_path=[key],
                    confidence=0.8,
                )
                results.append(result)

            # Traverse related keys
            for related_key in self.relationship_graph.get(key, set()):
                traverse(related_key, depth + 1)

        traverse(cache_key, 0)

        return sorted(results, key=lambda x: x.relevance_score, reverse=True)

    def create_relationship(self, key1: str, key2: str, strength: float = 1.0):
        """Create a relationship between two cached entries"""
        self.relationship_graph[key1].add(key2)
        self.relationship_graph[key2].add(key1)
        logger.debug(f"Created relationship: {key1} <-> {key2}")

    def get_conversation_continuity(self, session_id: str = None) -> dict[str, Any]:
        """Get conversation continuity information"""

        # Find recent conversation entries
        recent_conversations = []
        current_time = datetime.now()

        for cache in [self.session_cache, self.short_term_cache]:
            for key, entry in cache.cache.items():
                if entry.content_type == ContentType.CONVERSATION:
                    time_diff = current_time - entry.created_at
                    if time_diff < timedelta(hours=2):  # Last 2 hours
                        recent_conversations.append(
                            {
                                "key": key,
                                "content": entry.content,
                                "created_at": entry.created_at,
                                "access_count": entry.access_count,
                                "tags": list(entry.tags),
                            }
                        )

        # Sort by recency
        recent_conversations.sort(key=lambda x: x["created_at"], reverse=True)

        return {
            "session_id": session_id,
            "recent_entries": recent_conversations[:10],
            "total_recent": len(recent_conversations),
            "continuity_score": min(len(recent_conversations) / 10.0, 1.0),
        }

    def _cleanup_expired_entries(self):
        """Clean up expired cache entries"""
        now = datetime.now()
        expired_count = 0

        for cache in [self.short_term_cache, self.long_term_cache]:
            expired_keys = []

            for key, entry in cache.cache.items():
                if entry.expiration and now > entry.expiration:
                    expired_keys.append(key)

            for key in expired_keys:
                if cache.remove(key):
                    expired_count += 1
                    # Remove from indexes
                    self._remove_from_indexes(key)

        if expired_count > 0:
            self.stats["evictions"] += expired_count
            logger.debug(f"Cleaned up {expired_count} expired entries")

    def _remove_from_indexes(self, cache_key: str):
        """Remove a cache key from all indexes"""
        # Remove from entity index
        for _entity, keys in self.entity_index.items():
            keys.discard(cache_key)

        # Remove from concept index
        for _concept, keys in self.concept_index.items():
            keys.discard(cache_key)

        # Remove from tag index
        for _tag, keys in self.tag_index.items():
            keys.discard(cache_key)

        # Remove from relationship graph
        if cache_key in self.relationship_graph:
            del self.relationship_graph[cache_key]

        # Remove from other relationships
        for related_keys in self.relationship_graph.values():
            related_keys.discard(cache_key)

    def get_cache_statistics(self) -> dict[str, Any]:
        """Get comprehensive cache statistics"""

        total_size = 0
        total_entries = 0

        cache_stats = {}
        for name, cache in [
            ("session", self.session_cache),
            ("short_term", self.short_term_cache),
            ("long_term", self.long_term_cache),
            ("permanent", self.permanent_cache),
        ]:
            stats = cache.get_stats()
            cache_stats[name] = stats
            total_size += stats["size"]
            total_entries += stats["size"]

        # Calculate overall hit rate
        total_hits = sum(
            cache.get_stats()["hits"]
            for cache in [
                self.session_cache,
                self.short_term_cache,
                self.long_term_cache,
                self.permanent_cache,
            ]
        )
        total_requests = total_hits + self.stats["cache_misses"]
        overall_hit_rate = total_hits / total_requests if total_requests > 0 else 0

        return {
            "total_entries": total_entries,
            "total_size": total_size,
            "max_size": self.max_cache_size,
            "overall_hit_rate": overall_hit_rate,
            "cache_breakdown": cache_stats,
            "indexes": {
                "entities": len(self.entity_index),
                "concepts": len(self.concept_index),
                "tags": len(self.tag_index),
                "relationships": len(self.relationship_graph),
            },
            "operations": self.stats,
        }

    def clear_cache(self, level: CacheLevel = None):
        """Clear cache at specified level or all caches"""
        if level:
            cache = self._get_cache_by_level(level)
            cache.clear()
            logger.info(f"Cleared {level.value} cache")
        else:
            for cache in [
                self.session_cache,
                self.short_term_cache,
                self.long_term_cache,
                self.permanent_cache,
            ]:
                cache.clear()

            # Clear indexes
            self.entity_index.clear()
            self.concept_index.clear()
            self.tag_index.clear()
            self.relationship_graph.clear()

            logger.info("Cleared all caches")

    def export_cache(self, filepath: str, level: CacheLevel = None):
        """Export cache contents to file"""

        cache_data = {"export_timestamp": datetime.now().isoformat(), "entries": []}

        caches_to_export = []
        if level:
            caches_to_export.append((level.value, self._get_cache_by_level(level)))
        else:
            caches_to_export = [
                ("session", self.session_cache),
                ("short_term", self.short_term_cache),
                ("long_term", self.long_term_cache),
                ("permanent", self.permanent_cache),
            ]

        for cache_name, cache in caches_to_export:
            for _key, entry in cache.cache.items():
                entry_data = asdict(entry)
                entry_data["cache_name"] = cache_name
                cache_data["entries"].append(entry_data)

        with open(filepath, "w") as f:
            json.dump(cache_data, f, indent=2, default=str)

        logger.info(f"Exported {len(cache_data['entries'])} entries to {filepath}")

    def shutdown(self):
        """Shutdown the catch and release system"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        logger.info("Catch and release system shutdown")


# Global catch and release system
catch_release = CatchAndReleaseSystem()
