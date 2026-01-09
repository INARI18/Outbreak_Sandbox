import keyring
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea,
    QMessageBox
)
from ui.utils.base import NativeBase, create_icon, create_card, create_qicon
from ui.components import PrimaryButton
from ui.components.common.settings_dialog import SettingsDialog

class WelcomeScreen(NativeBase):
    def __init__(self):
        super().__init__()
        
        # Main vertical layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)


        # Content Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #f8fafc;")
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignCenter)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(40, 60, 40, 60)
        content_layout.addStretch()

        # Badge
        badge = QFrame()
        badge.setStyleSheet("background: rgba(255,255,255,0.6); border: 1px solid #ccfbf1; border-radius: 20px;")

        badge.setFixedSize(320, 40) 
        badge_layout = QHBoxLayout(badge)
        badge_layout.setContentsMargins(15, 0, 15, 0)
        dot = QLabel("●")

        dot.setStyleSheet("color: #10b981; font-size: 12px; border: none; background: transparent;")
        txt = QLabel("V1.0 SIMULATION ENGINE READY")
        txt.setStyleSheet("color: #0d9488; font-weight: bold; font-size: 12px; letter-spacing: 1.5px; border: none; background: transparent;")
        badge_layout.addWidget(dot)
        badge_layout.addSpacing(8)
        badge_layout.addWidget(txt)
        badge_layout.addStretch()
        content_layout.addWidget(badge, 0, Qt.AlignCenter)

        # Hero Title
        hero_title = QLabel("Outbreak <span style='color: #0d9488'>Sandbox</span>")
        hero_title.setStyleSheet("font-size: 64px; font-weight: 800; font-family: 'Space Grotesk'; color: #0f172a; margin: 20px 0;")
        hero_title.setTextFormat(Qt.RichText)
        hero_title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(hero_title)

        # Subtitle
        subtitle = QLabel("Master the dynamics of digital outbreaks.<br>An interactive playground for students & researchers.")
        subtitle.setStyleSheet("font-size: 20px; color: #64748b; font-family: 'Inter'; font-weight: 400;")
        subtitle.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(subtitle)

        content_layout.addSpacing(40)

        # Buttons
        btn_row = QHBoxLayout()
        self.start_btn = PrimaryButton("  Start Simulation", "play_circle", height=64)
        self.start_btn.setFixedWidth(260)
        self.start_btn.setStyleSheet(self.start_btn.styleSheet() + "font-size: 18px;")
        self.start_btn.clicked.connect(lambda: self.next_requested.emit())
        
        settings_btn = QPushButton("  Settings")
        settings_btn.setIcon(create_qicon("settings", 24, "#334155"))
        settings_btn.setFixedSize(200, 64)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setStyleSheet("""
            QPushButton {
                background: white; border: 1px solid #cbd5e1; border-radius: 12px;
                font-size: 16px; font-weight: bold; color: #334155;
            }
            QPushButton:hover { background: #f1f5f9; border-color: #94a3b8; }
        """)
        settings_btn.clicked.connect(self.open_settings)
        
        btn_row.addStretch()
        btn_row.addWidget(self.start_btn)
        btn_row.addSpacing(20)
        btn_row.addWidget(settings_btn)
        btn_row.addStretch()
        content_layout.addLayout(btn_row)

        content_layout.addStretch()

        # Footer
        footer = QLabel("© 2026 Outbreak Sandbox v1.0 Open source software.")
        footer.setStyleSheet("color: #94a3b8; font-size: 12px;")
        content_layout.addWidget(footer, 0, Qt.AlignCenter)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()
