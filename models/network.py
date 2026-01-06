from models.node import Node

class Network:
    def __init__(
        self,
        id: str,
        topology: str,
        size: int,
        security_level: float = 0.0 # Mantido apenas para compatibilidade de assinatura, mas ignorado
    ):
        self.id = id
        self.topology = topology
        self.size = size
        # self.security_level removido daqui, agora é calculado dinamicamente
        self.nodes: dict[str, Node] = {}

    @property
    def security_level(self) -> float:
        """
        Calcula o nível de segurança atual da rede dinamicamente.
        Nós infectados contribuem com 0.0 de segurança.
        Nós saudáveis contribuem com seu nível de defesa atual (que pode subir com patches).
        """
        if not self.nodes:
            return 0.0
            
        total_defense = 0.0
        for node in self.nodes.values():
            if node.is_infected:
                total_defense += 0.0
            else:
                total_defense += node.security_level
                
        return round(total_defense / len(self.nodes), 4)

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def get_node(self, node_id: str) -> Node | None:
        return self.nodes.get(node_id)

    def infected_nodes(self) -> list[Node]:
        return [node for node in self.nodes.values() if node.is_infected]

    def healthy_nodes(self) -> list[Node]:
        return [n for n in self.nodes.values() if not n.is_infected]