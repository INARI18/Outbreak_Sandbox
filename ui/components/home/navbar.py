from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from ui.utils.base import create_icon, create_qicon
from ui.components.common.settings_dialog import SettingsDialog

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
        
        # Right Side
        layout.addLayout(brand_layout)
        layout.addStretch()

        # Settings
        settings_btn = QPushButton()
        settings_btn.setIcon(create_qicon("settings", 28, "#64748b"))
        settings_btn.setFixedSize(48, 48)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setStyleSheet("background: transparent; border: none; border-radius: 20px;")
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)
        
        # App Version
        version_lbl = QLabel("v1.0")
        version_lbl.setStyleSheet("color: #cbd5e1; font-family: 'Space Grotesk'; font-size: 13px; font-weight: 500; margin-left: 10px;")
        layout.addWidget(version_lbl)

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()
