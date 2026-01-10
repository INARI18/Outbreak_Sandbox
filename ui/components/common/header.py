from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt
from ui.utils.base import create_icon, create_qicon
from ui.components.common.settings_dialog import SettingsDialog
from ui.theme import Theme

class StandardHeader(QFrame):
    dashboard_requested = Signal()

    def __init__(self, title="Outbreak Sandbox", subtitle=None, show_dashboard_btn=True, show_settings_btn=True):
        super().__init__()
        self.setObjectName("header_frame")
        self.setStyleSheet(f"#header_frame {{ background: white; border-bottom: 1px solid {Theme.BORDER}; }}")
        self.setFixedHeight(70)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 0, 30, 0)
        
        # Icon
        logo = create_icon("bug_report", 28, Theme.PRIMARY)
        
        # Text Column (Title + Optional Subtitle)
        text_col = QVBoxLayout()
        text_col.setSpacing(0)
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setAlignment(Qt.AlignVCenter)
        
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.setContentsMargins(0, 0, 0, 0)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-family: 'Space Grotesk'; font-weight: bold; font-size: 16px; color: {Theme.TEXT_PRIMARY};")
        title_row.addWidget(title_lbl)
        
        version_lbl = QLabel("v1.0")
        version_lbl.setStyleSheet(f"background: {Theme.BACKGROUND_APP}; color: {Theme.TEXT_SECONDARY}; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px;")
        title_row.addWidget(version_lbl)
        title_row.addStretch()
        
        text_col.addLayout(title_row)
        
        self.subtitle_lbl = QLabel(subtitle) if subtitle else QLabel()
        self.subtitle_lbl.setStyleSheet(f"font-size: 11px; color: {Theme.TEXT_SECONDARY};")
        if not subtitle:
            self.subtitle_lbl.hide()
            
        text_col.addWidget(self.subtitle_lbl)
        
        layout.addWidget(logo)
        layout.addLayout(text_col)
        layout.addStretch()

        if show_settings_btn:
             settings_btn = QPushButton()
             settings_btn.setIcon(create_qicon("settings", 28, "#64748b"))
             settings_btn.setFixedSize(48, 48)
             settings_btn.setCursor(Qt.PointingHandCursor)
             settings_btn.setStyleSheet("""
                QPushButton { border: 1px solid #e2e8f0; background: white; border-radius: 20px; }
                QPushButton:hover { background: #f8fafc; border-color: #cbd5e1; }
            """)
             settings_btn.clicked.connect(self.open_settings)
             layout.addWidget(settings_btn)

        if show_dashboard_btn:
            dash_btn = QPushButton()
            dash_btn.setIcon(create_qicon("home", 28, "#64748b"))
            dash_btn.setFixedSize(48, 48)
            dash_btn.setCursor(Qt.PointingHandCursor)
            dash_btn.setToolTip("Go to Dashboard")
            dash_btn.setStyleSheet("""
                QPushButton { border: 1px solid #e2e8f0; background: white; border-radius: 20px; }
                QPushButton:hover { background: #f8fafc; border-color: #cbd5e1; }
            """)
            dash_btn.clicked.connect(self.dashboard_requested.emit)
            layout.addWidget(dash_btn)

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def set_subtitle(self, text):
        self.subtitle_lbl.setText(text)
        self.subtitle_lbl.show()
