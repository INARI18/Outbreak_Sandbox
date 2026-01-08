from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from ui.screens.utils.base import create_pixmap

class WizardHeader(QFrame):
    def __init__(self, step_index, parent=None):
        super().__init__(parent)
        self.step_index = step_index
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(100, 0, 100, 0)
        
        steps = [
            (1, "TOPOLOGY", "hub"),
            (2, "VIRUS", "coronavirus"),
            (3, "CONFIG", "tune"),
            (4, "RUN", "play_arrow")
        ]
        
        for idx, label, icon_name in steps:
            # Line connector
            if idx > 1:
                line = QFrame()
                line.setFixedHeight(2)
                color = "#0d9488" if idx <= self.step_index else "#e2e8f0"
                line.setStyleSheet(f"background: {color}; margin-top: 15px;")
                layout.addWidget(line, 1) # stretch 1
                
            # Step Item
            item = QVBoxLayout()
            item.setSpacing(8)
            
            # Circle
            active = idx <= self.step_index
            current = idx == self.step_index
            
            circle = QLabel(str(idx) if not active else "") 
            circle.setFixedSize(32, 32)
            circle.setAlignment(Qt.AlignCenter)
            
            if current:
                 circle.setStyleSheet("background: #0d9488; color: white; border-radius: 16px; font-weight: bold;")
                 circle.setPixmap(create_pixmap(icon_name, 18, "white"))
            elif active:
                 circle.setStyleSheet("background: #ccfbf1; color: #0d9488; border-radius: 16px; font-weight: bold;")
                 circle.setText("✓")
            else:
                 circle.setStyleSheet("background: #f1f5f9; color: #94a3b8; border-radius: 16px; font-weight: bold;")
                 circle.setText(str(idx))

            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {'#0d9488' if current else '#94a3b8'};")
            
            item.addWidget(circle, 0, Qt.AlignCenter)
            item.addWidget(lbl, 0, Qt.AlignCenter)
            
            layout.addLayout(item)
