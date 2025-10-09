"""
DataLaundry - Cleans, deduplicates, and aligns incoming data for ingestion
"""

import hashlib
import re
from datetime import datetime
from typing import Any, Dict, List, Set


class DataLaundry:
    """Cleans and normalizes data from various sources"""

    def __init__(self):
        self.seen_hashes: Set[str] = set()
        self.cleaning_stats = {
            "total_processed": 0,
            "duplicates_removed": 0,
            "low_quality_filtered": 0,
            "normalized": 0,
        }

    def clean_and_filter(
        self, raw_data: Dict[str, Any], quality_threshold: float = 0.6
    ) -> Dict[str, Any]:
        """
        Clean and filter data from DataIntegrationUnit

        Args:
            raw_data: Raw data from data integration
            quality_threshold: Minimum quality score to keep

        Returns:
            Cleaned and filtered data
        """
        cleaned_data = {
            "query": raw_data.get("query"),
            "timestamp": datetime.now().isoformat(),
            "sources": {},
            "summary": {
                "total_items": 0,
                "kept_items": 0,
                "removed_duplicates": 0,
                "removed_low_quality": 0,
            },
        }

        # Process each source
        for source_name, source_data in raw_data.get("sources", {}).items():
            if source_data.get("status") != "success":
                continue

            cleaned_items = []
            for item in source_data.get("data", []):
                self.cleaning_stats["total_processed"] += 1
                cleaned_data["summary"]["total_items"] += 1

                # Check for duplicates
                item_hash = self._compute_hash(item)
                if item_hash in self.seen_hashes:
                    self.cleaning_stats["duplicates_removed"] += 1
                    cleaned_data["summary"]["removed_duplicates"] += 1
                    continue

                # Check quality
                quality_score = self._assess_quality(item)
                if quality_score < quality_threshold:
                    self.cleaning_stats["low_quality_filtered"] += 1
                    cleaned_data["summary"]["removed_low_quality"] += 1
                    continue

                # Clean and normalize
                cleaned_item = self._normalize_item(item, source_name)
                cleaned_item["quality_score"] = quality_score
                cleaned_items.append(cleaned_item)

                self.seen_hashes.add(item_hash)
                self.cleaning_stats["normalized"] += 1
                cleaned_data["summary"]["kept_items"] += 1

            if cleaned_items:
                cleaned_data["sources"][source_name] = {
                    "status": "cleaned",
                    "data": cleaned_items,
                    "original_count": len(source_data.get("data", [])),
                    "cleaned_count": len(cleaned_items),
                }

        return cleaned_data

    def _compute_hash(self, item: Dict[str, Any]) -> str:
        """Compute hash for deduplication"""
        # Create a stable string representation
        key_fields = ["title", "name", "content", "url", "description"]
        hash_input = ""

        for field in key_fields:
            if field in item:
                hash_input += str(item[field]).lower().strip()

        return hashlib.md5(hash_input.encode()).hexdigest()

    def _assess_quality(self, item: Dict[str, Any]) -> float:
        """Assess quality score of an item"""
        score = 0.5  # Base score

        # Check for key fields
        if "title" in item or "name" in item:
            score += 0.1
        if "description" in item or "content" in item or "abstract" in item:
            score += 0.1
        if "url" in item:
            score += 0.05

        # Check relevance score if provided
        if "relevance_score" in item:
            score = (score + item["relevance_score"]) / 2

        # Boost based on engagement metrics
        if "stars" in item and item["stars"] > 100:
            score += 0.1
        if "score" in item and item["score"] > 50:
            score += 0.1
        if "citations" in item and item["citations"] > 10:
            score += 0.15
        if "downloads" in item and item["downloads"] > 1000:
            score += 0.1

        # Penalize very short content
        content_fields = ["description", "content", "abstract", "summary"]
        content_length = 0
        for field in content_fields:
            if field in item:
                content_length += len(str(item[field]))

        if content_length < 50:
            score -= 0.2

        return min(max(score, 0.0), 1.0)  # Clamp to [0, 1]

    def _normalize_item(self, item: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Normalize item structure across different sources"""
        normalized = {
            "source": source,
            "type": item.get("type", "unknown"),
            "timestamp": datetime.now().isoformat(),
        }

        # Normalize title/name
        if "title" in item:
            normalized["title"] = self._clean_text(item["title"])
        elif "name" in item:
            normalized["title"] = self._clean_text(item["name"])

        # Normalize description/content
        if "description" in item:
            normalized["description"] = self._clean_text(item["description"])
        elif "content" in item:
            normalized["description"] = self._clean_text(item["content"])
        elif "abstract" in item:
            normalized["description"] = self._clean_text(item["abstract"])
        elif "summary" in item:
            normalized["description"] = self._clean_text(item["summary"])

        # Normalize URL
        if "url" in item:
            normalized["url"] = item["url"]

        # Preserve metrics
        metric_fields = ["stars", "score", "citations", "downloads", "comments"]
        for field in metric_fields:
            if field in item:
                normalized[field] = item[field]

        # Preserve additional metadata
        if "language" in item:
            normalized["language"] = item["language"]
        if "authors" in item:
            normalized["authors"] = item["authors"]
        if "published" in item:
            normalized["published"] = item["published"]
        if "subreddit" in item:
            normalized["subreddit"] = item["subreddit"]
        if "repository" in item:
            normalized["repository"] = item["repository"]

        # Add relevance score
        if "relevance_score" in item:
            normalized["relevance_score"] = item["relevance_score"]

        return normalized

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""

        # Convert to string if not already
        text = str(text)

        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r"[^\w\s\-.,!?:;()\[\]{}\'\"]+", "", text)

        # Trim
        text = text.strip()

        return text

    def align_vocabulary(
        self, data: Dict[str, Any], domain_vocabulary: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Align data vocabulary with codebase domain

        Args:
            data: Cleaned data
            domain_vocabulary: Domain-specific vocabulary mappings

        Returns:
            Data with aligned vocabulary
        """
        aligned_data = data.copy()

        # Process each source
        for source_name, source_data in aligned_data.get("sources", {}).items():
            for item in source_data.get("data", []):
                # Align title
                if "title" in item:
                    item["title"] = self._align_text(item["title"], domain_vocabulary)

                # Align description
                if "description" in item:
                    item["description"] = self._align_text(
                        item["description"], domain_vocabulary
                    )

                # Add domain tags
                item["domain_tags"] = self._extract_domain_tags(item, domain_vocabulary)

        return aligned_data

    def _align_text(self, text: str, vocabulary: Dict[str, List[str]]) -> str:
        """Align text with domain vocabulary"""
        # Simple term replacement
        aligned_text = text

        for canonical_term, variants in vocabulary.items():
            for variant in variants:
                # Case-insensitive replacement
                pattern = re.compile(re.escape(variant), re.IGNORECASE)
                aligned_text = pattern.sub(canonical_term, aligned_text)

        return aligned_text

    def _extract_domain_tags(
        self, item: Dict[str, Any], vocabulary: Dict[str, List[str]]
    ) -> List[str]:
        """Extract domain tags from item"""
        tags = set()

        # Combine title and description for analysis
        text = ""
        if "title" in item:
            text += item["title"] + " "
        if "description" in item:
            text += item["description"]

        text_lower = text.lower()

        # Check for domain terms
        for canonical_term in vocabulary.keys():
            if canonical_term.lower() in text_lower:
                tags.add(canonical_term)

        return list(tags)

    def get_cleaning_stats(self) -> Dict[str, Any]:
        """Get cleaning statistics"""
        stats = self.cleaning_stats.copy()

        if stats["total_processed"] > 0:
            stats["duplicate_rate"] = (
                stats["duplicates_removed"] / stats["total_processed"]
            )
            stats["quality_filter_rate"] = (
                stats["low_quality_filtered"] / stats["total_processed"]
            )
            stats["success_rate"] = stats["normalized"] / stats["total_processed"]
        else:
            stats["duplicate_rate"] = 0.0
            stats["quality_filter_rate"] = 0.0
            stats["success_rate"] = 0.0

        return stats

    def reset_stats(self):
        """Reset cleaning statistics"""
        self.cleaning_stats = {
            "total_processed": 0,
            "duplicates_removed": 0,
            "low_quality_filtered": 0,
            "normalized": 0,
        }
        self.seen_hashes.clear()
