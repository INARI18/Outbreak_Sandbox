from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from ui.utils.base import create_qicon
from ui.theme import Theme

class PrimaryButton(QPushButton):
    def __init__(self, text="", icon_name=None, height=54):
        super().__init__(text)
        self.setFixedHeight(height)
        self.setCursor(Qt.PointingHandCursor)
        
        # Force styling directly here to guarantee solid color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: white;
                border: 1px solid #0f766e;
                border-radius: 20px;
                font-family: 'Space Grotesk';
                font-weight: bold;
                font-size: 16px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: #14b8a6;
                border: 1px solid #115e59;
            }}
            QPushButton:pressed {{
                background-color: #0f766e;
            }}
            QPushButton:disabled {{
                background-color: #e6eef2;
                color: #94a3b8;
                border: 1px solid #cbd5e1;
            }}
        """)
        
        if icon_name:
            self.setIcon(create_qicon(icon_name, 20, "white"))
