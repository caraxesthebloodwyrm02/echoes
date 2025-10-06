#!/usr/bin/env python3
"""
Semantic Codebase Organizer and Reorganizer

This script analyzes the codebase structure and design, performs organizing actions,
and learns from them to improve future reorganizations.
"""

import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Any
import sys
sys.path.append(str(Path(__file__).parent.parent))
from modules.knowledge_graph_memory import MemoryMCPServer

class SemanticOrganizer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.memory = MemoryMCPServer("organizing_memory.json")
        self.load_knowledge()

    def load_knowledge(self):
        # Load existing knowledge or initialize
        pass

    def scan_codebase(self):
        """Scan the codebase and build semantic knowledge."""
        for file_path in self.root_path.rglob("*.py"):
            if file_path.is_file():
                self.analyze_file(file_path)

    def analyze_file(self, file_path: Path):
        """Analyze a single file for semantic content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            imports = self.extract_imports(tree)
            classes = self.extract_classes(tree)
            functions = self.extract_functions(tree)
            # Create entity for file
            entity = {
                "name": str(file_path.relative_to(self.root_path)),
                "entityType": "file",
                "observations": [
                    f"Contains {len(classes)} classes: {', '.join(classes)}",
                    f"Contains {len(functions)} functions: {', '.join(functions)}",
                    f"Imports: {', '.join(imports)}"
                ]
            }
            self.memory.create_entities_tool([entity])
            # Create relations for imports
            for imp in imports:
                relation = {
                    "from": str(file_path.relative_to(self.root_path)),
                    "to": imp,
                    "relationType": "imports"
                }
                self.memory.create_relations_tool([relation])
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def extract_imports(self, tree: ast.AST) -> List[str]:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports

    def extract_classes(self, tree: ast.AST) -> List[str]:
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    def extract_functions(self, tree: ast.AST) -> List[str]:
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    def analyze_structure(self):
        """Analyze folder structure."""
        for dir_path in self.root_path.rglob("*"):
            if dir_path.is_dir():
                entity = {
                    "name": str(dir_path.relative_to(self.root_path)),
                    "entityType": "folder",
                    "observations": [f"Contains {len(list(dir_path.iterdir()))} items"]
                }
                self.memory.create_entities_tool([entity])

    def decide_actions(self) -> List[Dict[str, Any]]:
        """Decide on organizing actions based on knowledge."""
        actions = []
        # Simple rule: move files based on content
        graph = json.loads(self.memory.read_graph_tool())
        for name, entity in graph["entities"].items():
            if entity["entityType"] == "file":
                if "test" in name.lower() or "test" in " ".join(entity["observations"]).lower():
                    actions.append({"action": "move", "file": name, "to": "tests/"})
                elif "deploy" in name.lower() or "docker" in name.lower():
                    actions.append({"action": "move", "file": name, "to": "deployment/"})
                # Add more rules
        return actions

    def perform_action(self, action: Dict[str, Any]):
        """Perform an organizing action."""
        if action["action"] == "move":
            src = self.root_path / action["file"]
            dst_dir = self.root_path / action["to"]
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst = dst_dir / src.name
            src.rename(dst)
            # Learn from action
            observation = f"Moved to {action['to']} based on semantic analysis"
            self.memory.add_observations_tool([{"entityName": action["file"], "contents": [observation]}])

    def run(self):
        """Main run method."""
        self.scan_codebase()
        self.analyze_structure()
        actions = self.decide_actions()
        for action in actions:
            self.perform_action(action)
        # Evolve: perhaps update rules based on actions
        self.update_knowledge()

    def update_knowledge(self):
        """Update semantic knowledge."""
        # For now, just save
        pass

if __name__ == "__main__":
    organizer = SemanticOrganizer()
    organizer.run()
