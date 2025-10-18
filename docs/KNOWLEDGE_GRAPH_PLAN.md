# Knowledge Graph & Semantic Learning - Implementation Plan

## Overview

Build an intelligent knowledge graph system that learns the codebase structure, semantics, and patterns, enabling context-aware code understanding and retrieval.

## Architecture

```
┌────────────────────────────────────────────────────────┐
│         Knowledge Graph System                         │
├────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │   Learning   │  │   Knowledge  │  │   Semantic   ││
│  │   Pipeline   │→ │     Graph    │ ← │    Index     ││
│  └──────────────┘  └──────────────┘  └──────────────┘│
│                           ↓                            │
│                  ┌──────────────┐                      │
│                  │Query Engine  │                      │
│                  └──────────────┘                      │
└────────────────────────────────────────────────────────┘
```

## 1. Knowledge Graph Schema

```python
from app.core.knowledge_graph_memory import MemoryMCPServer
from typing import List, Dict, Set
import networkx as nx

class CodebaseKnowledgeGraph(MemoryMCPServer):
    """
    Enhanced knowledge graph for codebase.
    """

    def __init__(self):
        super().__init__("codebase_knowledge.json")
        self.graph = nx.MultiDiGraph()
        self.embeddings = {}

    # Node Types
    NODE_TYPES = {
        "module": "Python module/package",
        "class": "Class definition",
        "function": "Function/method",
        "variable": "Variable/constant",
        "concept": "Abstract concept",
        "pattern": "Design pattern",
        "task": "Automation task",
        "tool": "Available tool",
        "bug": "Known issue/bug",
        "feature": "Feature implementation",
    }

    # Relation Types
    RELATION_TYPES = {
        "imports": "Module imports",
        "inherits": "Class inheritance",
        "calls": "Function calls",
        "uses": "Uses variable/resource",
        "implements": "Implements pattern",
        "depends_on": "Dependency",
        "related_to": "Semantic relation",
        "fixes": "Bug fix",
        "enhances": "Feature enhancement",
        "tested_by": "Test relationship",
    }

    def add_code_entity(
        self,
        name: str,
        entity_type: str,
        file_path: str,
        line_number: int,
        code_snippet: str,
        docstring: str = None,
        metadata: Dict = None,
    ):
        """Add code entity to graph."""
        entity = {
            "name": name,
            "type": entity_type,
            "file": file_path,
            "line": line_number,
            "code": code_snippet,
            "docs": docstring,
            "metadata": metadata or {},
        }

        self.graph.add_node(name, **entity)

        # Generate embedding
        embedding = self._generate_embedding(
            f"{name} {docstring} {code_snippet}"
        )
        self.embeddings[name] = embedding

    def add_semantic_relation(
        self,
        from_entity: str,
        to_entity: str,
        relation_type: str,
        confidence: float = 1.0,
        metadata: Dict = None,
    ):
        """Add semantic relationship."""
        self.graph.add_edge(
            from_entity,
            to_entity,
            type=relation_type,
            confidence=confidence,
            metadata=metadata or {},
        )

    def query_semantic(
        self,
        query: str,
        k: int = 10,
    ) -> List[Dict]:
        """Semantic search in knowledge graph."""
        query_embedding = self._generate_embedding(query)

        # Find similar entities
        similarities = {}
        for name, embedding in self.embeddings.items():
            sim = self._cosine_similarity(query_embedding, embedding)
            similarities[name] = sim

        # Get top-k
        top_entities = sorted(
            similarities.items(),
            key=lambda x: x[1],
            reverse=True
        )[:k]

        results = []
        for name, score in top_entities:
            node_data = self.graph.nodes[name]
            results.append({
                **node_data,
                "similarity_score": score,
            })

        return results
```

## 2. Learning Pipeline

```python
from pathlib import Path
import ast
from typing import Iterator

class CodebaseLearningPipeline:
    """
    Multi-stage pipeline to learn codebase.
    """

    def __init__(self, knowledge_graph: CodebaseKnowledgeGraph):
        self.kg = knowledge_graph
        self.analyzers = [
            StaticAnalyzer(self.kg),
            SemanticEmbedder(self.kg),
            PatternRecognizer(self.kg),
            DocumentationExtractor(self.kg),
            DependencyTracker(self.kg),
        ]

    def learn_project(self, project_root: Path):
        """Learn entire project."""
        python_files = project_root.rglob("*.py")

        for file_path in python_files:
            self.learn_file(file_path)

        # Post-processing
        self._extract_patterns()
        self._build_dependency_graph()
        self._generate_summaries()

    def learn_file(self, file_path: Path):
        """Learn single file."""
        code = file_path.read_text()

        # Run all analyzers
        for analyzer in self.analyzers:
            analyzer.process(file_path, code)

class StaticAnalyzer:
    """Extract entities from AST."""

    def __init__(self, kg: CodebaseKnowledgeGraph):
        self.kg = kg

    def process(self, file_path: Path, code: str):
        """Process file with AST."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return

        # Extract modules
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._process_class(node, file_path)
            elif isinstance(node, ast.FunctionDef):
                self._process_function(node, file_path)
            elif isinstance(node, ast.Import):
                self._process_import(node, file_path)

    def _process_class(self, node: ast.ClassDef, file_path: Path):
        """Process class definition."""
        self.kg.add_code_entity(
            name=node.name,
            entity_type="class",
            file_path=str(file_path),
            line_number=node.lineno,
            code_snippet=ast.unparse(node)[:500],
            docstring=ast.get_docstring(node),
        )

        # Add inheritance relations
        for base in node.bases:
            if isinstance(base, ast.Name):
                self.kg.add_semantic_relation(
                    node.name,
                    base.id,
                    "inherits",
                )
```

## 3. Semantic Indexer

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class SemanticCodeIndexer:
    """
    Vector search for code semantics.
    """

    def __init__(self):
        # Use code-specific model
        self.model = SentenceTransformer('microsoft/codebert-base')
        self.dimension = 768
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_to_entity = {}
        self.next_id = 0

    def add_entity(self, entity_name: str, text: str):
        """Add entity to index."""
        # Generate embedding
        embedding = self.model.encode([text])[0]
        embedding = embedding / np.linalg.norm(embedding)  # Normalize

        # Add to FAISS
        self.index.add(np.array([embedding], dtype=np.float32))
        self.id_to_entity[self.next_id] = entity_name
        self.next_id += 1

    def search(self, query: str, k: int = 10) -> List[Dict]:
        """Search for similar code."""
        # Encode query
        query_embedding = self.model.encode([query])[0]
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        # Search
        distances, indices = self.index.search(
            np.array([query_embedding], dtype=np.float32),
            k
        )

        # Format results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0:  # Valid index
                results.append({
                    "entity": self.id_to_entity[idx],
                    "score": float(dist),
                })

        return results
```

## 4. Query Engine

```python
class KnowledgeQueryEngine:
    """
    Natural language query engine for knowledge graph.
    """

    def __init__(
        self,
        knowledge_graph: CodebaseKnowledgeGraph,
        semantic_indexer: SemanticCodeIndexer,
    ):
        self.kg = knowledge_graph
        self.indexer = semantic_indexer

    async def query(self, question: str) -> Dict:
        """Answer question about codebase."""
        # Classify query type
        query_type = self._classify_query(question)

        if query_type == "find_code":
            return await self._handle_find_code(question)
        elif query_type == "explain":
            return await self._handle_explain(question)
        elif query_type == "trace":
            return await self._handle_trace(question)
        else:
            return await self._handle_general(question)

    async def _handle_find_code(self, question: str) -> Dict:
        """Find relevant code."""
        # Semantic search
        results = self.indexer.search(question, k=5)

        # Get full context from graph
        entities = []
        for result in results:
            node = self.kg.graph.nodes[result["entity"]]
            entities.append({
                **node,
                "relevance_score": result["score"],
            })

        return {
            "query_type": "find_code",
            "results": entities,
            "explanation": self._generate_explanation(entities),
        }

    async def _handle_explain(self, question: str) -> Dict:
        """Explain code or concept."""
        # Extract entity name from question
        entity = self._extract_entity(question)

        if entity in self.kg.graph:
            node = self.kg.graph.nodes[entity]

            # Get related nodes
            related = list(self.kg.graph.successors(entity))

            # Generate explanation
            explanation = self._generate_detailed_explanation(
                node,
                related,
            )

            return {
                "query_type": "explain",
                "entity": entity,
                "explanation": explanation,
                "related": related,
            }
        else:
            return {"error": f"Entity '{entity}' not found"}
```

## 5. Implementation Timeline

### Week 1-2: Knowledge Graph Core
- [ ] Enhanced MemoryMCPServer integration
- [ ] Graph schema definition
- [ ] Basic CRUD operations
- [ ] Persistence layer

### Week 3-4: Learning Pipeline
- [ ] Static analyzer (AST)
- [ ] Semantic embedder
- [ ] Pattern recognizer
- [ ] Documentation extractor

### Week 5-6: Semantic Search
- [ ] Vector index setup (FAISS)
- [ ] Embedding generation
- [ ] Semantic search
- [ ] Result ranking

### Week 7-8: Query Engine
- [ ] Natural language query parsing
- [ ] Query type classification
- [ ] Result aggregation
- [ ] Explanation generation

## Success Metrics

- **Coverage**: 100% of codebase indexed
- **Speed**: <100ms semantic search
- **Accuracy**: >90% on relevance
- **Entities**: 1000+ entities tracked
- **Relations**: 5000+ relationships

## Configuration

```yaml
knowledge:
  enabled: true

  graph:
    backend: networkx  # or neo4j for production
    persistence: codebase_knowledge.json

  embedding:
    model: microsoft/codebert-base
    dimension: 768
    device: cuda  # or cpu

  index:
    type: faiss
    metric: cosine
    nlist: 100  # for IVF index

  learning:
    auto_learn_on_startup: true
    watch_files: true
    incremental_updates: true

  query:
    max_results: 10
    min_confidence: 0.7
```

## Next Steps

1. Integrate with existing MemoryMCPServer
2. Implement learning pipeline
3. Set up semantic indexing
4. Build query engine
5. Create monitoring dashboard
