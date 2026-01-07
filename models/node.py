class NodeType:
    def __init__(self, id: str, name: str, description: str, security_level: float):
        self.id = id
        self.name = name
        self.description = description
        self.security_level = security_level

    def __repr__(self):
        return f"<NodeType {self.name} (Sec: {self.security_level})>"


class Node:
    def __init__(
        self,
        id: str,
        name: str,
        node_type: str,
        security_level: float
    ):
        self.id = id
        self.name = name
        self.type = node_type
        self.security_level = security_level
        self.status = "healthy"
        self.connected_nodes: list[str] = []
        self.x: float = 0.0
        self.y: float = 0.0

    def connect(self, other_node_id: str):
        if other_node_id not in self.connected_nodes:
            self.connected_nodes.append(other_node_id)

    def infect(self):
        if self.status == "healthy":
            self.status = "infected"

    def quarantine(self):
        if self.status == "infected":
            self.status = "quarantined"

    def disinfect(self):
        self.status = "healthy"

    @property
    def is_infected(self) -> bool:
        return self.status == "infected"
