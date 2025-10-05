import json
from pathlib import Path
from typing import Any, Dict, List


class MemoryMCPServer:
    def __init__(self, memory_file: str = "memory.json"):
        self.memory_file = Path(memory_file)
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if self.memory_file.exists():
            with open(self.memory_file, "r") as f:
                return json.load(f)
        return {"entities": {}, "relations": []}

    def _save_data(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def create_entities_tool(self, entities: List[Dict[str, Any]]) -> str:
        for entity in entities:
            name = entity["name"]
            self.data["entities"][name] = {
                "entityType": entity["entityType"],
                "observations": entity["observations"],
            }
        self._save_data()
        return f"Created {len(entities)} entities"

    def create_relations_tool(self, relations: List[Dict[str, Any]]) -> str:
        for relation in relations:
            self.data["relations"].append(relation)
        self._save_data()
        return f"Created {len(relations)} relations"

    def add_observations_tool(self, observations: List[Dict[str, Any]]) -> str:
        for obs in observations:
            name = obs["entityName"]
            if name in self.data["entities"]:
                self.data["entities"][name]["observations"].extend(obs["contents"])
        self._save_data()
        return f"Added observations to {len(observations)} entities"

    def read_graph_tool(self) -> str:
        return json.dumps(self.data)

    def search_nodes_tool(self, query: str) -> str:
        matches = []
        for name, entity in self.data["entities"].items():
            if query.lower() in name.lower() or any(
                query.lower() in obs.lower() for obs in entity["observations"]
            ):
                matches.append({"name": name, **entity})
        return json.dumps({"matches": matches})

    def open_nodes_tool(self, names: List[str]) -> str:
        entities = {}
        for name in names:
            if name in self.data["entities"]:
                entities[name] = self.data["entities"][name]
        # Include relations involving these entities
        related_relations = [
            r for r in self.data["relations"] if r["from"] in names or r["to"] in names
        ]
        return json.dumps({"entities": entities, "relations": related_relations})
