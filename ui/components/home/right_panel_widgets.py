from PySide6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, Signal
from ui.utils.base import create_icon
from PySide6.QtGui import QIcon

class SavedSimulationsWidget(QPushButton):
    clicked_signal = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(120) 
        self.setStyleSheet("""
            QPushButton {
                background-color: #0d9488;
                border: 1px solid #0f766e;
                border-radius: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #14b8a6;
                border: 1px solid #115e59;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        
        icon = create_icon("folder", 32, "white")
        icon.setStyleSheet("background: rgba(255,255,255,0.2); border-radius: 10px; padding: 10px; color: white; font-size: 32px; font-family: 'Material Symbols Outlined';")
        
        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(4)
        text_col.setAlignment(Qt.AlignVCenter)
        
        title = QLabel("Saved Simulations")
        title.setStyleSheet("color: white; font-weight: 800; font-size: 15px; border: none; background: transparent;")
        desc = QLabel("Access your saved simulation states and replays")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #ccfbf1; font-size: 11px; border: none; background: transparent;")
        
        text_col.addWidget(title)
        text_col.addWidget(desc)
        
        layout.addWidget(icon)
        layout.addSpacing(15)
        layout.addLayout(text_col)
        layout.addStretch()
        
        self.clicked.connect(self.clicked_signal.emit)

class VirusRepositoryWidget(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(160)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #334155;
                border: 1px solid #475569;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        
        icon = create_icon("science", 32, "white")
        icon.setStyleSheet("background: rgba(255,255,255,0.1); border-radius: 10px; padding: 10px; color: white; font-size: 32px; font-family: 'Material Symbols Outlined';")
        
        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(4)
        text_col.setAlignment(Qt.AlignVCenter)
        
        title = QLabel("Virus Repository")
        title.setStyleSheet("color: white; font-weight: 800; font-size: 15px; border: none; background: transparent;")
        desc = QLabel("Create and manage custom virus profiles")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #94a3b8; font-size: 11px; border: none; background: transparent;")
        
        text_col.addWidget(title)
        text_col.addWidget(desc)
        
        layout.addWidget(icon)
        layout.addSpacing(15)
        layout.addLayout(text_col)
        layout.addStretch()

class DocumentationWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #1e293b; border-radius: 16px; color: white;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Documentation")
        title.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        desc = QLabel("Find setup instructions, usage examples, and technical details in our GitHub repository.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #94a3b8; margin-top: 10px; margin-bottom: 20px;")

        gh_btn = QPushButton("  View on GitHub")
        gh_btn.setIcon(QIcon("ui/assets/icons/github-mark.svg"))
        gh_btn.setStyleSheet("background: white; color: #0f172a; border: none;")
        gh_btn.clicked.connect(lambda: __import__('webbrowser').open('https://github.com/INARI18/Outbreak_Sandbox'))
        gh_btn.setCursor(Qt.PointingHandCursor)

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(gh_btn)
