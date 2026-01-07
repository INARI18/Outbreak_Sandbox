from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QPen, QColor, QPainter

class NetworkVisualizer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        self.network = None
        self.node_items = {} # map id -> QGraphicsEllipseItem
        
        # Colors
        self.COLOR_HEALTHY = QColor("#10b981") # Emerald 500
        self.COLOR_INFECTED = QColor("#ef4444") # Red 500
        self.COLOR_QUARANTINED = QColor("#f59e0b") # Amber 500
        self.COLOR_EDGE = QColor("#cbd5e1") # Slate 300

    def set_network(self, network):
        self.network = network
        self.scene.clear()
        self.node_items.clear()
        
        if not network:
            return

        # Scale factor to spread nodes out (assuming spring layout returned -1 to 1)
        scale = 250.0
        
        # Pass 1: Create Edges first (so they are under nodes)
        # We generally iterate nodes, then connections. 
        # To avoid duplicates, we can store added edges or check id < target_id
        
        # To draw edges correctly we need positions first. 
        # So let's calculate positions map locally
        positions = {}
        for node in network.nodes.values():
            positions[node.id] = (node.x * scale, node.y * scale)
            
        added_edges = set()
        
        for node in network.nodes.values():
            u_pos = positions[node.id]
            
            for target_id in node.connected_nodes:
                # consistent tuple for edge key
                edge_key = tuple(sorted((node.id, target_id)))
                
                if edge_key not in added_edges and target_id in positions:
                    v_pos = positions[target_id]
                    
                    line = self.scene.addLine(u_pos[0], u_pos[1], v_pos[0], v_pos[1])
                    line.setPen(QPen(self.COLOR_EDGE, 2))
                    line.setZValue(0)
                    added_edges.add(edge_key)

        # Pass 2: Create Nodes
        radius = 8
        for node_id, pos in positions.items():
            x, y = pos
            ellipse = self.scene.addEllipse(x - radius, y - radius, radius * 2, radius * 2)
            ellipse.setPen(QPen(Qt.white, 2))
            self.update_node_color(ellipse, self.network.nodes[node_id].status)
            ellipse.setZValue(1)
            self.node_items[node_id] = ellipse
            
        # Center view
        self.scene.setSceneRect(-scale*1.5, -scale*1.5, scale*3, scale*3)

    def update_node_color(self, item, status):
        if status == "healthy":
            item.setBrush(QBrush(self.COLOR_HEALTHY))
        elif status == "infected":
            item.setBrush(QBrush(self.COLOR_INFECTED))
        elif status == "quarantined":
            item.setBrush(QBrush(self.COLOR_QUARANTINED))
        else:
            item.setBrush(QBrush(Qt.gray))

    def refresh_state(self):
        """Called periodically to update visual state based on network object changes"""
        if not self.network:
            return
            
        for node_id, node in self.network.nodes.items():
            if node_id in self.node_items:
                self.update_node_color(self.node_items[node_id], node.status)
