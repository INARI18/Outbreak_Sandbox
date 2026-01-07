from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt
from ui.screens.utils.base import create_icon

class StandardHeader(QFrame):
    dashboard_requested = Signal()

    def __init__(self, title="Outbreak Sandbox", subtitle=None, show_dashboard_btn=True):
        super().__init__()
        self.setObjectName("header_frame")
        self.setStyleSheet("#header_frame { background: white; border-bottom: 1px solid #e2e8f0; }")
        self.setFixedHeight(70)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 0, 30, 0)
        
        # Brand
        logo = create_icon("bug_report", 28, "#0d9488")
        
        # Text Column (Title + Optional Subtitle)
        text_col = QVBoxLayout()
        text_col.setSpacing(0)
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setAlignment(Qt.AlignVCenter)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-family: 'Space Grotesk'; font-weight: bold; font-size: 16px; color: #0f172a;")
        text_col.addWidget(title_lbl)
        
        self.subtitle_lbl = QLabel(subtitle) if subtitle else QLabel()
        self.subtitle_lbl.setStyleSheet("font-size: 11px; color: #64748b;")
        if not subtitle:
            self.subtitle_lbl.hide()
            
        text_col.addWidget(self.subtitle_lbl)
        
        layout.addWidget(logo)
        layout.addLayout(text_col)
        layout.addStretch()
        
        if show_dashboard_btn:
            dash_btn = QPushButton("Dashboard")
            dash_btn.setStyleSheet("""
                QPushButton { border: none; color: #64748b; font-weight: bold; }
                QPushButton:hover { color: #0d9488; }
            """)
            dash_btn.clicked.connect(self.dashboard_requested.emit)
            layout.addWidget(dash_btn)

    def set_subtitle(self, text):
        self.subtitle_lbl.setText(text)
        self.subtitle_lbl.show()
