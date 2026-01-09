from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt
from ui.components.common.buttons import PrimaryButton

class WizardFooter(QFrame):
    back_clicked = Signal()
    next_clicked = Signal()

    def __init__(self, next_text="Next"):
        super().__init__()
        self.setStyleSheet("background: white; border-top: 1px solid #e2e8f0;")
        self.setFixedHeight(80)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(40, 0, 40, 0)
        
        # Back Button
        self.back_btn = QPushButton("← Back")
        self.back_btn.setStyleSheet("""
            QPushButton { border: none; color: #64748b; font-weight: bold; background: transparent; }
            QPushButton:hover { color: #0f172a; }
        """)
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_clicked.emit)
        
        # Next Button (Primary)
        self.next_btn = PrimaryButton(next_text, height=50)
        self.next_btn.setFixedWidth(180)
        self.next_btn.clicked.connect(self.next_clicked.emit)
        
        layout.addWidget(self.back_btn)
        layout.addStretch()
        layout.addWidget(self.next_btn)

    def set_next_text(self, text):
        self.next_btn.setText(text)
