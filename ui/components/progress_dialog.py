from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import  QMovie
from ui.utils.base import create_icon, create_qicon

class ModernProgressDialog(QDialog):
    def __init__(self, message="Loading...", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(320, 180)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: white; 
                border-radius: 16px; 
                border: 1px solid #e2e8f0;
            }
        """)
        
        # Shadow effect simulated (since property box-shadow is not supported)
        # In native QWidget we use QGraphicsDropShadowEffect, but here style simplified.
        
        inner_layout = QVBoxLayout(container)
        inner_layout.setContentsMargins(30,30,30,30)
        inner_layout.setAlignment(Qt.AlignCenter)
        
        # Icon / Spinner
        # We can use a simple indeterminate progress bar or just text.
        # Let's use a themed Label
        
        self.icon_lbl = QLabel()
        # Creating a simple rotating text effect or static icon
        self.icon_lbl.setPixmap(create_qicon("neurology", 48, "#0d9488").pixmap(48,48))
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        
        self.status_lbl = QLabel(message)
        self.status_lbl.setStyleSheet("font-family: 'Space Grotesk'; font-size: 14px; color: #0f172a; font-weight: bold; margin-top: 15px;")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setWordWrap(True)
        
        self.sub_lbl = QLabel("Initializing AI Environment...")
        self.sub_lbl.setStyleSheet("font-family: 'Inter'; font-size: 11px; color: #64748b; margin-top: 5px;")
        self.sub_lbl.setAlignment(Qt.AlignCenter)
        
        inner_layout.addWidget(self.icon_lbl)
        inner_layout.addWidget(self.status_lbl)
        inner_layout.addWidget(self.sub_lbl)
        
        layout.addWidget(container)

    def set_message(self, msg):
        self.status_lbl.setText(msg)
