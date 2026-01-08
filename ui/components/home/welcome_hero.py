from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QDate

class WelcomeHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(6)

        # Date Line
        current_date_str = QDate.currentDate().toString("dddd, MMMM d, yyyy").upper()
        date_lbl = QLabel(current_date_str)
        date_lbl.setStyleSheet("color: #64748b; font-weight: 700; font-size: 12px; letter-spacing: 1px; font-family: 'Inter';")

        # Title
        header_text = QLabel("Welcome to <span style='color: #0d9488;'>Outbreak Sandbox</span>")
        header_text.setTextFormat(Qt.RichText)
        header_text.setStyleSheet("font-family: 'Space Grotesk'; font-size: 34px; font-weight: 800; color: #0f172a;")
        
        # Subtitle
        sub_text = QLabel("Configure, simulate, and analyze malware propagation in safe, controlled network environments.")
        sub_text.setStyleSheet("color: #64748b; font-size: 16px; margin-top: 4px;")
        
        layout.addWidget(date_lbl)
        layout.addWidget(header_text)
        layout.addWidget(sub_text)
