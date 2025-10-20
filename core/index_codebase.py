#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Codebase Indexing and Analysis Script

Uses UnifiedVectorModule to:
1. Index the codebase (embed code files).
2. Compress chunks.
3. Synthesize a summary via clustering/similarity.
4. Save for future vector analysis.

Run: python automation/scripts/index_codebase.py
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from automation.core.unified_vector_module import UnifiedVectorModule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_codebase_texts(
    base_path: Path, extensions: List[str] = [".py", ".md", ".yml", ".json"]
) -> List[Dict[str, Any]]:
    """Collect texts from codebase files."""
    texts = []
    for ext in extensions:
        for file_path in base_path.rglob(f"*{ext}"):
            if not any(skip in str(file_path) for skip in ["__pycache__", ".git", ".venv", "node_modules"]):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if len(content.strip()) > 50:  # Skip empty/small files
                            texts.append(
                                {
                                    "file": str(file_path.relative_to(base_path)),
                                    "content": content[:2000],  # Limit for embedding
                                    "extension": ext,
                                }
                            )
                except Exception as e:
                    logger.warning(f"Skipping {file_path}: {e}")
    return texts


def synthesize_summary(module: UnifiedVectorModule, texts: List[Dict[str, Any]]) -> str:
    """Synthesize a summary using vector analysis (clustering for themes)."""
    from sklearn.cluster import KMeans

    if module.compressed_vectors is None or len(texts) < 5:
        return "Insufficient data for clustering summary."

    # Cluster compressed vectors
    n_clusters = min(5, len(texts) // 2)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(module.compressed_vectors)

    summary_parts = []
    for cluster_id in range(n_clusters):
        cluster_texts = [texts[i]["content"][:200] for i, c in enumerate(clusters) if c == cluster_id]
        if cluster_texts:
            # Simple theme extraction (most common words)
            words = " ".join(cluster_texts).split()
            common_words = [w for w in set(words) if words.count(w) > 1][:5]
            summary_parts.append(f"Cluster {cluster_id}: Themes - {', '.join(common_words)}")

    return "\n".join(summary_parts)


def main():
    base_path = Path(__file__).parent.parent.parent  # e:\Projects\Development
    output_path = base_path / "codebase_index.pkl"

    logger.info("Collecting codebase texts...")
    texts_data = collect_codebase_texts(base_path)
    logger.info(f"Collected {len(texts_data)} code snippets.")

    # Initialize module
    module = UnifiedVectorModule(compress_dim=128)

    # Pre-chunk texts with metadata alignment
    chunked_texts: List[str] = []
    chunked_metadata: List[Dict[str, Any]] = []
    for item in texts_data:
        content = item["content"]
        file_path = item.get("file")
        extension = item.get("extension")
        if extension == ".py":
            chunks = module.chunk_code_files([content], chunk_size=512)
            if not chunks:
                chunks = [content]
            for chunk_idx, chunk in enumerate(chunks):
                chunked_texts.append(chunk)
                chunked_metadata.append(
                    {
                        "file": file_path,
                        "chunk_index": chunk_idx,
                        "content": chunk,
                    }
                )
        else:
            chunked_texts.append(content)
            chunked_metadata.append(
                {
                    "file": file_path,
                    "chunk_index": 0,
                    "content": content,
                }
            )

    for idx, meta in enumerate(chunked_metadata):
        meta["id"] = idx

    logger.info(f"Prepared {len(chunked_texts)} chunks for embedding.")

    # Unified processing with optimizations
    logger.info("Processing with optimized unified vector module")
    module.unified_batch_process(
        chunked_texts,
        metadata=chunked_metadata,
        compress=True,
        compress_method="quantization",
        chunk_code=False,
    )

    # Synthesize summary with clustering on compressed vectors
    logger.info("Synthesizing summary...")
    summary = synthesize_summary(module, chunked_metadata)
    print("Codebase Summary (Optimized):")
    print(summary)

    # Save for future use
    module.save_module(str(output_path))
    logger.info(f"Optimized index saved to {output_path}")

    # Demo: Hybrid search
    query = "assistant workflow"
    matches = module.hybrid_search(query, top_k=3)
    print(f"\nHybrid search results for '{query}':")
    for match in matches:
        print(f"- {match.get('file', 'unknown')}: {match.get('score', 0):.2f}")

    # Evaluate quality (sample)
    sample_queries = ["health endpoint", "cache metadata"]
    sample_gt = [[0], [1]]  # Placeholder ground truth
    metrics = module.evaluate_quality(sample_queries, sample_gt)
    print(f"\nQuality Metrics: MRR={metrics['MRR']:.2f}, NDCG={metrics['NDCG']:.2f}")


if __name__ == "__main__":
    main()
