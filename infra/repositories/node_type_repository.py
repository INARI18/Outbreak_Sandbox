import json
from models.node import NodeType

class NodeTypeRepository:
    def __init__(self, json_path: str):
        self.json_path = json_path
        self._cache = None

    def load_all(self) -> list[NodeType]:
        if self._cache:
            return self._cache

        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        node_types = []
        for item in data.get("node_types", []):
            node_types.append(NodeType(
                id=item["id"],
                name=item["name"],
                description=item["description"],
                security_level=item["security_level"]
            ))
        
        self._cache = node_types
        return node_types

    def get_by_id(self, type_id: str) -> NodeType:
        all_types = self.load_all()
        for nt in all_types:
            if nt.id == type_id:
                return nt
        return None
