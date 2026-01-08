from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from ui.screens.utils.base import create_icon, create_qicon

class Navbar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: white; border-bottom: 1px solid #e2e8f0;")
        self.setFixedHeight(70)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 0, 30, 0)
        
        # Logo Area
        brand_layout = QHBoxLayout()
        logo = create_icon("bug_report", 28, "#0d9488")
        brand_text = QLabel("Outbreak Sandbox")
        brand_text.setStyleSheet("font-family: 'Space Grotesk'; font-weight: bold; font-size: 16px;")
        brand_layout.addWidget(logo)
        brand_layout.addWidget(brand_text)
        
        # Right Side (App Version)
        user_layout = QHBoxLayout()
        version_lbl = QLabel("v1.0.2-alpha")
        version_lbl.setStyleSheet("color: #cbd5e1; font-family: 'Space Grotesk'; font-size: 13px; font-weight: 500;")
        user_layout.addWidget(version_lbl)

        layout.addLayout(brand_layout)
        layout.addStretch()
        layout.addLayout(user_layout)
