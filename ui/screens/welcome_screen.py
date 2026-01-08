import keyring
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea,
    QDialog, QLineEdit, QMessageBox
)
from ui.screens.utils.base import NativeBase, create_icon, create_card, create_qicon
from ui.components import PrimaryButton

class ApiKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure API Key")
        self.setFixedSize(400, 250)
        self.setStyleSheet("""
            QDialog { background: white; border-radius: 12px; }
            QLabel { font-size: 14px; color: #334155; }
            QLineEdit { 
                border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px;
                color: #334155; font-size: 14px;
            }
            QLineEdit:focus { border-color: #0d9488; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30,30,30,30)

        title = QLabel("Groq API Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title)

        info = QLabel("Enter your Groq API key to enable LLM features securely.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(info)

        self.input = QLineEdit()
        self.input.setPlaceholderText("your_api_key_here...")
        self.input.setEchoMode(QLineEdit.Password)
        
        # Load existing key
        try:
            current_key = keyring.get_password("outbreak_sandbox", "groq_api_key")
            if current_key:
                self.input.setText(current_key)
        except Exception:
            pass
            
        layout.addWidget(self.input)

        btn_layout = QHBoxLayout()
        
        delete_btn = QPushButton("Delete")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: 1px solid #ef4444; color: #ef4444; 
                border-radius: 8px; padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background: #fef2f2; }
        """)
        delete_btn.clicked.connect(self.delete_key)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            background: transparent; border: none; color: #64748b; font-weight: bold;
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Key")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #0d9488; color: white; border: none; border-radius: 8px;
                padding: 8px 16px; font-weight: bold;
            }
            QPushButton:hover { background: #0f766e; }
            QPushButton:pressed { background: #115e59; }
        """)
        save_btn.clicked.connect(self.save_key)

        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def delete_key(self):
        try:
            keyring.delete_password("outbreak_sandbox", "groq_api_key")
            self.input.clear()
            QMessageBox.information(self, "Success", "API Key removed.")
            self.accept()
        except Exception:
            # keyring throws error if password not found, which is fine
            QMessageBox.information(self, "Info", "No key found to delete.")

    def save_key(self):
        key = self.input.text().strip()
        if not key:
            QMessageBox.warning(self, "Invalid Key", "Please enter an API key.")
            return

        try:
            keyring.set_password("outbreak_sandbox", "groq_api_key", key)
            QMessageBox.information(self, "Success", "API Key saved securely.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save key: {str(e)}")

class WelcomeScreen(NativeBase):
    def __init__(self):
        super().__init__()
        
        # Main vertical layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)


        # Content Area - Centered
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #f8fafc;")
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignCenter)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(40, 60, 40, 60)

        # Top Spacer for Centering
        content_layout.addStretch()

        # Badge
        badge = QFrame()
        badge.setStyleSheet("background: rgba(255,255,255,0.6); border: 1px solid #ccfbf1; border-radius: 20px;")
        badge.setFixedSize(300, 40)
        badge_layout = QHBoxLayout(badge)
        badge_layout.setContentsMargins(15, 0, 15, 0)
        dot = QLabel("●")
        dot.setStyleSheet("color: #10b981; font-size: 12px;")
        txt = QLabel("V1.0 SIMULATION ENGINE READY")
        txt.setStyleSheet("color: #0d9488; font-weight: bold; font-size: 12px; letter-spacing: 1.5px;")
        badge_layout.addWidget(dot)
        badge_layout.addSpacing(5)
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
        
        api_btn = QPushButton("  API Key")
        api_btn.setIcon(create_qicon("key", 24, "#334155"))
        api_btn.setFixedSize(200, 64)
        api_btn.setCursor(Qt.PointingHandCursor)
        api_btn.setStyleSheet("""
            QPushButton {
                background: white; border: 1px solid #cbd5e1; border-radius: 12px;
                font-size: 16px; font-weight: bold; color: #334155;
            }
            QPushButton:hover { background: #f1f5f9; border-color: #94a3b8; }
        """)
        api_btn.clicked.connect(self.open_api_dialog)
        
        btn_row.addStretch()
        btn_row.addWidget(self.start_btn)
        btn_row.addSpacing(20)
        btn_row.addWidget(api_btn)
        btn_row.addStretch()
        content_layout.addLayout(btn_row)

        content_layout.addStretch()

        # Footer
        footer = QLabel("© 2026 Outbreak Sandbox v1.0 Open source software.")
        footer.setStyleSheet("color: #94a3b8; font-size: 12px;")
        content_layout.addWidget(footer, 0, Qt.AlignCenter)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        self.check_api_key()

    def check_api_key(self):
        has_key = False
        try:
            if keyring.get_password("outbreak_sandbox", "groq_api_key"):
                has_key = True
        except Exception:
            pass
        
        self.start_btn.setEnabled(has_key)
        if not has_key:
            self.start_btn.setToolTip("Please configure your Groq API Key first")
        else:
             self.start_btn.setToolTip("") 


    def open_api_dialog(self):
        dlg = ApiKeyDialog(self)
        dlg.exec()
        self.check_api_key()
