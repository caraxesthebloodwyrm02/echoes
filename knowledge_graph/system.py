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
Knowledge Graph System with Semantic Reasoning
Ontology-based knowledge management and inference
"""

# removed unused import json
import datetime
import os
from typing import Any, Dict, List, Tuple

import networkx as nx
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD


class KnowledgeGraph:
    """RDF-based knowledge graph with NetworkX integration"""

    def __init__(self):
        self.rdf_graph = Graph()
        self.nx_graph = nx.DiGraph()

        # Define namespaces
        self.ns = {
            "code": Namespace("http://example.org/code#"),
            "metric": Namespace("http://example.org/metric#"),
            "security": Namespace("http://example.org/security#"),
            "ai": Namespace("http://example.org/ai#"),
            "project": Namespace("http://example.org/project#"),
        }

        # Bind namespaces
        for prefix, namespace in self.ns.items():
            self.rdf_graph.bind(prefix, namespace)

    def add_code_entity(
        self, entity_type: str, name: str, properties: Dict[str, Any] = None
    ):
        """Add a code-related entity to the knowledge graph"""

        entity_uri = self.ns["code"][
            f"{entity_type}_{name.replace('/', '_').replace('.', '_')}"
        ]

        # Add type
        self.rdf_graph.add((entity_uri, RDF.type, self.ns["code"][entity_type]))

        # Add properties
        if properties:
            for prop, value in properties.items():
                if isinstance(value, str):
                    self.rdf_graph.add(
                        (entity_uri, self.ns["code"][prop], Literal(value))
                    )
                elif isinstance(value, (int, float)):
                    self.rdf_graph.add(
                        (
                            entity_uri,
                            self.ns["code"][prop],
                            Literal(value, datatype=XSD.float),
                        )
                    )
                elif isinstance(value, bool):
                    self.rdf_graph.add(
                        (
                            entity_uri,
                            self.ns["code"][prop],
                            Literal(value, datatype=XSD.boolean),
                        )
                    )

        return entity_uri

    def add_relationship(
        self, subject_uri, predicate, object_uri, properties: Dict[str, Any] = None
    ):
        """Add relationship between entities"""

        # Add basic relationship
        self.rdf_graph.add((subject_uri, self.ns["code"][predicate], object_uri))

        # Add relationship properties if provided
        if properties:
            rel_node = BNode()
            self.rdf_graph.add(
                (subject_uri, self.ns["code"][f"{predicate}_relation"], rel_node)
            )
            self.rdf_graph.add((rel_node, RDF.type, self.ns["code"]["Relationship"]))
            self.rdf_graph.add((rel_node, self.ns["code"]["target"], object_uri))

            for prop, value in properties.items():
                self.rdf_graph.add((rel_node, self.ns["code"][prop], Literal(value)))

    def add_metric_data(
        self, entity_uri, metric_name: str, value: float, timestamp: str = None
    ):
        """Add metric data to an entity"""

        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat()

        metric_uri = self.ns["metric"][
            f"{metric_name}_{timestamp.replace(':', '').replace('-', '').replace('.', '')}"
        ]

        self.rdf_graph.add((metric_uri, RDF.type, self.ns["metric"]["Metric"]))
        self.rdf_graph.add(
            (metric_uri, self.ns["metric"]["name"], Literal(metric_name))
        )
        self.rdf_graph.add(
            (metric_uri, self.ns["metric"]["value"], Literal(value, datatype=XSD.float))
        )
        self.rdf_graph.add(
            (
                metric_uri,
                self.ns["metric"]["timestamp"],
                Literal(timestamp, datatype=XSD.dateTime),
            )
        )
        self.rdf_graph.add((entity_uri, self.ns["metric"]["has_metric"], metric_uri))

    def add_security_vulnerability(self, entity_uri, vuln_data: Dict[str, Any]):
        """Add security vulnerability information"""

        vuln_uri = self.ns["security"][f"vuln_{hash(str(vuln_data)) % 10000}"]

        self.rdf_graph.add((vuln_uri, RDF.type, self.ns["security"]["Vulnerability"]))
        self.rdf_graph.add(
            (entity_uri, self.ns["security"]["has_vulnerability"], vuln_uri)
        )

        for key, value in vuln_data.items():
            if key == "severity":
                self.rdf_graph.add(
                    (vuln_uri, self.ns["security"]["severity"], Literal(value))
                )
            elif key == "title":
                self.rdf_graph.add(
                    (vuln_uri, self.ns["security"]["title"], Literal(value))
                )
            elif key == "description":
                self.rdf_graph.add(
                    (vuln_uri, self.ns["security"]["description"], Literal(value))
                )
            elif key == "confidence":
                self.rdf_graph.add(
                    (
                        vuln_uri,
                        self.ns["security"]["confidence"],
                        Literal(value, datatype=XSD.float),
                    )
                )

    def infer_relationships(self):
        """Perform basic inference on relationships"""

        # Find files that import from each other
        import_query = """
        SELECT ?file1 ?file2
        WHERE {
            ?file1 code:imports ?module .
            ?file2 code:defines ?module .
        }
        """

        for row in self.rdf_graph.query(import_query):
            file1, file2 = row
            self.add_relationship(file1, "depends_on", file2)

        # Infer high-risk files based on vulnerabilities and complexity
        risk_query = """
        SELECT ?file (COUNT(?vuln) as ?vuln_count) ?complexity
        WHERE {
            ?file security:has_vulnerability ?vuln .
            ?file metric:has_metric ?metric .
            ?metric metric:name "complexity" .
            ?metric metric:value ?complexity .
        }
        GROUP BY ?file ?complexity
        """

        for row in self.rdf_graph.query(risk_query):
            file_uri, vuln_count, complexity = row
            risk_score = float(vuln_count) * float(complexity)
            if risk_score > 10:  # Threshold for high risk
                self.rdf_graph.add(
                    (file_uri, self.ns["security"]["risk_level"], Literal("high"))
                )
            elif risk_score > 5:
                self.rdf_graph.add(
                    (file_uri, self.ns["security"]["risk_level"], Literal("medium"))
                )
            else:
                self.rdf_graph.add(
                    (file_uri, self.ns["security"]["risk_level"], Literal("low"))
                )

    def query_knowledge(self, sparql_query: str) -> List[Dict[str, Any]]:
        """Execute SPARQL query on knowledge graph"""

        results = []
        for row in self.rdf_graph.query(sparql_query):
            result_dict = {}
            for i, var in enumerate(row.labels):
                result_dict[var] = str(row[i])
            results.append(result_dict)

        return results

    def find_similar_entities(
        self, entity_uri, similarity_threshold: float = 0.7
    ) -> List[Tuple[URIRef, float]]:
        """Find entities similar to the given entity"""

        # Convert to NetworkX for similarity analysis
        self._sync_to_networkx()

        similar_entities = []

        # Simple similarity based on shared relationships
        entity_neighbors = set(self.nx_graph.neighbors(str(entity_uri)))

        for node in self.nx_graph.nodes():
            if node != str(entity_uri):
                node_neighbors = set(self.nx_graph.neighbors(node))
                intersection = len(entity_neighbors & node_neighbors)
                union = len(entity_neighbors | node_neighbors)

                if union > 0:
                    similarity = intersection / union
                    if similarity >= similarity_threshold:
                        similar_entities.append((URIRef(node), similarity))

        return sorted(similar_entities, key=lambda x: x[1], reverse=True)

    def _sync_to_networkx(self):
        """Sync RDF graph to NetworkX for analysis"""
        self.nx_graph.clear()

        for subject, predicate, obj in self.rdf_graph:
            self.nx_graph.add_edge(str(subject), str(obj), relation=str(predicate))

    def export_graph(self, fmt: str = "turtle") -> str:
        """Export knowledge graph in specified format"""
        if format == "turtle":
            return self.rdf_graph.serialize(format="turtle")
        elif format == "json-ld":
            return self.rdf_graph.serialize(format="json-ld", indent=2)
        else:
            return self.rdf_graph.serialize(format="xml")

    def save_graph(self, filename: str):
        """Save knowledge graph to file"""
        os.makedirs("knowledge_graph/data", exist_ok=True)

        with open(f"knowledge_graph/data/{filename}.ttl", "w", encoding="utf-8") as f:
            f.write(self.export_graph("turtle"))

    def load_graph(self, filename: str):
        """Load knowledge graph from file"""
        self.rdf_graph.parse(f"knowledge_graph/data/{filename}.ttl", format="turtle")


class OntologyManager:
    """Ontology management for domain-specific knowledge"""

    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg
        self._define_ontology()

    def _define_ontology(self):
        """Define ontology classes and properties"""

        # Code ontology
        self.kg.rdf_graph.add((self.kg.ns["code"]["CodeEntity"], RDF.type, OWL.Class))
        self.kg.rdf_graph.add(
            (
                self.kg.ns["code"]["File"],
                RDFS.subClassOf,
                self.kg.ns["code"]["CodeEntity"],
            )
        )
        self.kg.rdf_graph.add(
            (
                self.kg.ns["code"]["Function"],
                RDFS.subClassOf,
                self.kg.ns["code"]["CodeEntity"],
            )
        )
        self.kg.rdf_graph.add(
            (
                self.kg.ns["code"]["Class"],
                RDFS.subClassOf,
                self.kg.ns["code"]["CodeEntity"],
            )
        )
        self.kg.rdf_graph.add(
            (
                self.kg.ns["code"]["Module"],
                RDFS.subClassOf,
                self.kg.ns["code"]["CodeEntity"],
            )
        )

        # Relationships
        self.kg.rdf_graph.add(
            (self.kg.ns["code"]["imports"], RDF.type, OWL.ObjectProperty)
        )
        self.kg.rdf_graph.add(
            (self.kg.ns["code"]["defines"], RDF.type, OWL.ObjectProperty)
        )
        self.kg.rdf_graph.add(
            (self.kg.ns["code"]["depends_on"], RDF.type, OWL.ObjectProperty)
        )
        self.kg.rdf_graph.add(
            (self.kg.ns["code"]["contains"], RDF.type, OWL.ObjectProperty)
        )

        # Metric ontology
        self.kg.rdf_graph.add((self.kg.ns["metric"]["Metric"], RDF.type, OWL.Class))
        self.kg.rdf_graph.add(
            (self.kg.ns["metric"]["has_metric"], RDF.type, OWL.ObjectProperty)
        )

        # Security ontology
        self.kg.rdf_graph.add(
            (self.kg.ns["security"]["Vulnerability"], RDF.type, OWL.Class)
        )
        self.kg.rdf_graph.add(
            (self.kg.ns["security"]["has_vulnerability"], RDF.type, OWL.ObjectProperty)
        )

    def validate_ontology(self) -> bool:
        """Validate ontology consistency"""
        # Basic validation - check for undefined classes
        undefined_classes = []

        for _subject, predicate, obj in self.kg.rdf_graph:
            if predicate == RDF.type and isinstance(obj, URIRef):
                # Check if class is defined
                class_defined = False
                for _s, _p, _o in self.kg.rdf_graph.triples((obj, RDF.type, OWL.Class)):
                    class_defined = True
                    break

                if not class_defined and str(obj) not in [
                    "http://www.w3.org/2002/07/owl#Class",
                    "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property",
                ]:
                    undefined_classes.append(str(obj))

        if undefined_classes:
            print(f"Ontology validation failed. Undefined classes: {undefined_classes}")
            return False

        return True


class SemanticReasoner:
    """Advanced semantic reasoning capabilities"""

    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg

    def find_code_patterns(self) -> Dict[str, List[str]]:
        """Identify common code patterns and anti-patterns"""

        patterns = {
            "high_risk_files": [],
            "complex_functions": [],
            "security_hotspots": [],
            "dependency_clusters": [],
        }

        # Find high-risk files (high complexity + vulnerabilities)
        risk_query = """
        SELECT ?file ?complexity (COUNT(?vuln) as ?vuln_count)
        WHERE {
            ?file metric:has_metric ?metric .
            ?metric metric:name "complexity" .
            ?metric metric:value ?complexity .
            ?file security:has_vulnerability ?vuln .
        }
        GROUP BY ?file ?complexity
        HAVING (?complexity > 10 && ?vuln_count > 2)
        """

        for row in self.kg.rdf_graph.query(risk_query):
            patterns["high_risk_files"].append(str(row[0]))

        # Find complex functions
        complex_query = """
        SELECT ?entity ?complexity
        WHERE {
            ?entity rdf:type code:Function .
            ?entity metric:has_metric ?metric .
            ?metric metric:name "complexity" .
            ?metric metric:value ?complexity .
        }
        HAVING (?complexity > 15)
        """

        for row in self.kg.rdf_graph.query(complex_query):
            patterns["complex_functions"].append(str(row[0]))

        return patterns

    def recommend_improvements(self) -> List[Dict[str, Any]]:
        """Generate improvement recommendations based on knowledge graph"""

        recommendations = []

        # Complexity reduction recommendations
        complex_files = self.kg.query_knowledge(
            """
        SELECT ?file ?complexity
        WHERE {
            ?file metric:has_metric ?metric .
            ?metric metric:name "complexity" .
            ?metric metric:value ?complexity .
        }
        HAVING (?complexity > 20)
        ORDER BY DESC(?complexity)
        """
        )

        for file in complex_files[:5]:  # Top 5
            recommendations.append(
                {
                    "type": "refactoring",
                    "priority": "high",
                    "target": file["file"],
                    "issue": f"High complexity ({file['complexity']})",
                    "recommendation": "Break down into smaller functions or classes",
                }
            )

        # Security recommendations
        vuln_files = self.kg.query_knowledge(
            """
        SELECT ?file (COUNT(?vuln) as ?count)
        WHERE {
            ?file security:has_vulnerability ?vuln .
        }
        GROUP BY ?file
        HAVING (?count > 3)
        ORDER BY DESC(?count)
        """
        )

        for file in vuln_files[:3]:  # Top 3
            recommendations.append(
                {
                    "type": "security",
                    "priority": "critical",
                    "target": file["file"],
                    "issue": f"Multiple vulnerabilities ({file['count']})",
                    "recommendation": "Conduct security code review and apply fixes",
                }
            )

        return recommendations

    def predict_maintenance_effort(self, file_uri: URIRef) -> Dict[str, Any]:
        """Predict maintenance effort for a file based on knowledge graph"""

        # Gather metrics
        metrics = self.kg.query_knowledge(
            f"""
        SELECT ?name ?value
        WHERE {{
            <{file_uri}> metric:has_metric ?metric .
            ?metric metric:name ?name .
            ?metric metric:value ?value .
        }}
        """
        )

        # Gather vulnerabilities
        vuln_count = len(
            self.kg.query_knowledge(
                f"""
        SELECT ?vuln
        WHERE {{
            <{file_uri}> security:has_vulnerability ?vuln .
        }}
        """
            )
        )

        # Calculate maintenance score
        complexity = next(
            (float(m["value"]) for m in metrics if m["name"] == "complexity"), 0
        )
        coverage = next(
            (float(m["value"]) for m in metrics if m["name"] == "coverage"), 0
        )

        # Simple maintenance effort prediction
        base_effort = complexity * 0.1  # Complexity factor
        security_penalty = vuln_count * 0.5  # Security factor
        coverage_bonus = (100 - coverage) * 0.05  # Coverage factor

        total_effort = base_effort + security_penalty + coverage_bonus

        return {
            "file": str(file_uri),
            "predicted_effort_hours": round(total_effort, 1),
            "complexity_score": complexity,
            "vulnerability_count": vuln_count,
            "coverage_percentage": coverage,
            "risk_level": "high"
            if total_effort > 5
            else "medium"
            if total_effort > 2
            else "low",
        }


def demo_knowledge_graph():
    """Demonstrate knowledge graph capabilities"""

    # Initialize knowledge graph
    kg = KnowledgeGraph()
    ontology = OntologyManager(kg)
    reasoner = SemanticReasoner(kg)

    # Add some sample entities
    file1 = kg.add_code_entity(
        "File",
        "utils.py",
        {
            "language": "python",
            "lines": 150,
            "last_modified": datetime.datetime.now().isoformat(),
        },
    )

    file2 = kg.add_code_entity(
        "File",
        "main.py",
        {
            "language": "python",
            "lines": 80,
            "last_modified": datetime.datetime.now().isoformat(),
        },
    )

    # Add relationships
    kg.add_relationship(file2, "imports", file1)

    # Add metrics
    kg.add_metric_data(file1, "complexity", 12.5)
    kg.add_metric_data(file1, "coverage", 85.0)
    kg.add_metric_data(file2, "complexity", 8.2)
    kg.add_metric_data(file2, "coverage", 92.0)

    # Add security data
    kg.add_security_vulnerability(
        file1,
        {
            "severity": "medium",
            "title": "Potential SQL injection",
            "description": "User input not properly sanitized",
            "confidence": 0.8,
        },
    )

    # Run inference
    kg.infer_relationships()

    # Query and analyze
    patterns = reasoner.find_code_patterns()
    recommendations = reasoner.recommend_improvements()

    print("Knowledge Graph Demo Results:")
    print(f"Patterns found: {len(patterns)} categories")
    print(f"Recommendations: {len(recommendations)}")
    print(f"Ontology valid: {ontology.validate_ontology()}")

    # Save graph
    kg.save_graph("demo_graph")

    return {
        "entities_added": 2,
        "relationships_inferred": True,
        "patterns_analyzed": len(patterns),
        "recommendations_generated": len(recommendations),
    }


if __name__ == "__main__":
    demo_knowledge_graph()
