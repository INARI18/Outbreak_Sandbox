from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal
from ui.components import PrimaryButton

class SimulationHubCard(QFrame):
    new_simulation_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setObjectName("card")
        self.setStyleSheet("""
            #card {
                background: white; 
                border-radius: 12px; 
                border: 1px solid #e2e8f0;
            }
        """)
        # Shadow effect
        eff = QGraphicsDropShadowEffect(blurRadius=15, xOffset=0, yOffset=4, color=QColor(0,0,0,15))
        self.setGraphicsEffect(eff)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Top Row
        top_row = QHBoxLayout()
        
        # Left Text
        text_col = QVBoxLayout()
        text_col.setSpacing(6)
        
        hub_title = QLabel("Simulation Hub")
        hub_title.setStyleSheet("font-weight: 800; font-size: 18px; color: #1e293b; border: none;")
        
        desc_lbl = QLabel("Start a new outbreak scenario using our advanced deterministic or stochastic engines.")
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #64748b; font-size: 14px; border: none;")
        
        text_col.addWidget(hub_title)
        text_col.addWidget(desc_lbl)
        
        top_row.addLayout(text_col, 1) 
        top_row.addSpacing(20)
        
        # Right Button
        start_btn = PrimaryButton("New Simulation", None, 42)
        start_btn.setFixedWidth(180)
        start_btn.setCursor(Qt.PointingHandCursor)
        start_btn.clicked.connect(self.new_simulation_clicked.emit)
        
        top_row.addWidget(start_btn)
        
        layout.addLayout(top_row)
