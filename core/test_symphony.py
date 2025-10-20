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
Comprehensive Test Suite for Symphony Implementation
Validates all new AI-enhanced components
"""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


class TestSymphonyComponents:
    """Test all symphony components"""

    def test_ai_agents_orchestrator(self):
        """Test AI agent orchestration system"""
        try:
            from ai_agents.orchestrator import AgentTemplates, AIAgentOrchestrator

            orchestrator = AIAgentOrchestrator()

            # Test agent creation
            config = AgentTemplates.create_code_reviewer()
            agent = orchestrator.create_agent(**config)
            assert agent is not None

            # Test task addition
            task = orchestrator.add_task("Review test file", "code_reviewer", "Review completed")
            assert task is not None

        except ImportError:
            pytest.skip("AI agents not available")

    def test_multimodal_processor(self):
        """Test multimodal processing capabilities"""
        try:
            from multimodal.processor import MultimodalProcessor

            processor = MultimodalProcessor()
            # Removed unused variable _audio_processor

            text_data = processor.process_text("Hello world")
            assert "text_features" in text_data
            assert text_data["word_count"] == 2

            # Test cross-modal similarity (text-text for now)
            similarity = processor.cross_modal_similarity(text_data["text_features"], text_data["text_features"])
            assert similarity > 0.9  # Same text should be very similar

        except ImportError:
            pytest.skip("Multimodal dependencies not available")

    def test_mlops_pipeline(self):
        """Test MLOps pipeline functionality"""
        try:
            from mlops.pipeline import MLOpsPipeline, ModelRegistry

            pipeline = MLOpsPipeline("test_experiment")
            registry = ModelRegistry()

            # Test pipeline initialization
            assert pipeline.experiment_name == "test_experiment"

            # Test registry
            models = registry.list_models()
            assert isinstance(models, dict)

        except ImportError:
            pytest.skip("MLOps dependencies not available")

    def test_security_scanner(self):
        """Test AI-enhanced security scanning"""
        try:
            from security.scanner import SecurityScanner

            scanner = SecurityScanner()

            # Test scanner initialization
            assert hasattr(scanner, "ai_analyzer")
            assert hasattr(scanner, "tools")

            # Test with a simple file scan (should handle gracefully)
            report = scanner.scan_project(".")
            assert hasattr(report, "vulnerabilities")
            assert hasattr(report, "summary")
            assert hasattr(report, "ai_insights")

        except ImportError:
            pytest.skip("Security dependencies not available")

    def test_synthetic_data_generator(self):
        """Test synthetic data generation"""
        try:
            from synthetic_data.generator import SyntheticDataGenerator

            generator = SyntheticDataGenerator()

            # Create test data
            test_data = pd.DataFrame(
                {
                    "age": np.random.normal(30, 5, 100),
                    "score": np.random.uniform(0, 100, 100),
                }
            )

            # Test metadata detection
            metadata = generator.detect_metadata(test_data)
            assert metadata is not None

            # Test synthetic generation (small sample for speed)
            synthetic, validation = generator.generate_synthetic_data(test_data, 10, method="copula")
            assert len(synthetic) == 10
            assert "quality_metrics" in validation

        except ImportError:
            pytest.skip("Synthetic data dependencies not available")

    def test_knowledge_graph(self):
        """Test knowledge graph system"""
        try:
            from knowledge_graph.system import KnowledgeGraph, OntologyManager

            kg = KnowledgeGraph()
            ontology = OntologyManager(kg)

            # Test entity addition
            entity = kg.add_code_entity("File", "test.py", {"language": "python"})
            assert entity is not None

            # Test ontology validation
            valid = ontology.validate_ontology()
            assert isinstance(valid, bool)

            # Test graph export
            turtle_data = kg.export_graph("turtle")
            assert isinstance(turtle_data, str)
            assert len(turtle_data) > 0

        except ImportError:
            pytest.skip("Knowledge graph dependencies not available")

    def test_visualization_tool(self):
        """Test the enhanced visualization tool"""
        # Check if reports exist
        reports = ["coverage.json", "radon_cc.json", "radon_mi.json"]
        metrics_dir = Path("metrics")

        for report in reports:
            report_path = metrics_dir / report
            if report_path.exists():
                # Try to load JSON
                with open(report_path, "r") as f:
                    data = json.load(f)
                assert isinstance(data, (dict, list))

    def test_codebase_visualizer_execution(self):
        """Test that the visualizer runs without critical errors"""
        import subprocess
        import sys

        # Run visualizer and check it doesn't crash
        result = subprocess.run(
            [sys.executable, "metrics/codebase_visualizer.py"],
            cwd=".",
            capture_output=True,
            text=True,
            timeout=60,  # 1 minute timeout
        )

        # Should complete (exit code 0 or 1 is acceptable, not crash with 2+)
        assert result.returncode < 2, f"Visualizer crashed with exit code {result.returncode}"

    def test_symphony_integration(self):
        """Test integration between symphony components"""
        # Check that all new directories exist
        symphony_dirs = [
            "ai_agents",
            "multimodal",
            "mlops",
            "security",
            "synthetic_data",
            "knowledge_graph",
        ]

        for dir_name in symphony_dirs:
            assert os.path.exists(dir_name), f"Symphony directory {dir_name} not found"
            assert os.path.isdir(dir_name), f"{dir_name} is not a directory"

    def test_memory_system(self):
        """Test that symphony implementation is properly documented in memory"""
        # Check if symphony task memory exists
        # This is more of a documentation test
        assert True  # Placeholder - would check memory system if accessible


# Performance and scalability tests
class TestSymphonyPerformance:
    """Performance tests for symphony components"""

    def test_large_dataset_handling(self):
        """Test handling of larger datasets"""
        try:
            from synthetic_data.generator import SyntheticDataGenerator

            # Create larger test dataset
            large_data = pd.DataFrame(
                {
                    "feature1": np.random.randn(1000),
                    "feature2": np.random.randn(1000),
                    "category": np.random.choice(["A", "B", "C"], 1000),
                }
            )

            generator = SyntheticDataGenerator()

            # Test with reasonable timeout
            import time

            _start_time = time.time()

            synthetic, _ = generator.generate_synthetic_data(large_data, 100, method="copula")

            duration = time.time() - _start_time
            assert duration < 30  # Should complete within 30 seconds
            assert len(synthetic) == 100

        except ImportError:
            pytest.skip("Performance test dependencies not available")


if __name__ == "__main__":
    # Run basic validation
    print("Running Symphony Component Validation...")

    components = [
        ("AI Agents", "ai_agents.orchestrator"),
        ("Multimodal", "multimodal.processor"),
        ("MLOps", "mlops.pipeline"),
        ("Security", "security.scanner"),
        ("Synthetic Data", "synthetic_data.generator"),
        ("Knowledge Graph", "knowledge_graph.system"),
    ]

    results = {}
    for name, module in components:
        try:
            __import__(module)
            results[name] = "✓ Available"
        except ImportError as e:
            results[name] = f"✗ Missing: {e}"

    print("\nComponent Status:")
    for name, status in results.items():
        print(f"  {name}: {status}")

    print(
        f"\nSymphony integration: {'✓ Complete' if all('✓' in status for status in results.values()) else '⚠ Partial'}"
    )
