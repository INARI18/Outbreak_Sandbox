from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QWidget, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal
from ui.screens.utils.base import create_icon

class SystemReadinessCard(QFrame):
    continue_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet("""
            #card {
                background: white; 
                border-radius: 12px; 
                border: 1px solid #e2e8f0;
            }
        """)
        
        # Shadow
        eff = QGraphicsDropShadowEffect(blurRadius=15, xOffset=0, yOffset=4, color=QColor(0,0,0,15))
        self.setGraphicsEffect(eff)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        # Top Row
        top_row = QHBoxLayout()
        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        
        sys_title = QLabel("System Readiness")
        sys_title.setStyleSheet("font-weight: 800; font-size: 18px; color: #1e293b; border: none;")
        
        sys_sub = QLabel("2 of 3 Modules Configured")
        sys_sub.setStyleSheet("color: #64748b; font-size: 14px; font-weight: 500; border: none;")
        
        text_col.addWidget(sys_title)
        text_col.addWidget(sys_sub)
        
        top_row.addLayout(text_col)
        top_row.addStretch()
        
        perc_lbl = QLabel("66%")
        perc_lbl.setStyleSheet("font-family: 'Space Grotesk'; font-weight: 800; font-size: 24px; color: #1e293b; border: none;") 
        top_row.addWidget(perc_lbl)
        
        layout.addLayout(top_row)
        
        # Progress Bar
        pbar = QProgressBar()
        pbar.setFixedHeight(6)
        pbar.setTextVisible(False)
        pbar.setRange(0, 100)
        pbar.setValue(66)
        pbar.setStyleSheet("""
            QProgressBar {
                background-color: #f1f5f9;
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #0d9488; /* Teal theme */
                border-radius: 3px;
            }
        """)
        layout.addWidget(pbar)
        
        # Status Indicators
        status_row = QHBoxLayout()
        status_row.setSpacing(15)
        
        status_row.addWidget(self._create_status_item("Topology", "Ready", "#10b981", "check_circle", "#10b981"))
        status_row.addWidget(self._create_status_item("Virus", "Ready", "#10b981", "check_circle", "#10b981"))
        status_row.addWidget(self._create_status_item("Mode", "Action Required", "#ef4444", "error", "#ef4444"))
        
        status_row.addStretch()
        layout.addLayout(status_row)
        
        # Bottom Button
        btn_row = QHBoxLayout()
        continue_btn = QPushButton("Continue")
        continue_btn.setFixedSize(100, 32)
        continue_btn.setCursor(Qt.PointingHandCursor)
        continue_btn.setStyleSheet("""
            QPushButton {
                background: #0d9488;
                color: white;
                border: 1px solid #0f766e;
                border-radius: 6px;
                font-size: 12px;
                font-family: 'Space Grotesk';
                font-weight: bold;
            }
            QPushButton:hover {
                background: #14b8a6;
                border: 1px solid #115e59;
            }
        """)
        continue_btn.clicked.connect(self.continue_clicked.emit)
        btn_row.addWidget(continue_btn)
        btn_row.addStretch()
        
        layout.addSpacing(10)
        layout.addLayout(btn_row)

    def _create_status_item(self, label, status_text, status_color, icon_name, icon_color):
        item_w = QWidget()
        l = QHBoxLayout(item_w)
        l.setContentsMargins(0,0,0,0)
        l.setSpacing(6)
        
        sep = QLabel("|")
        sep.setStyleSheet("color: #cbd5e1; font-weight: bold; border: none;")
        l.addWidget(sep)
        
        ico = create_icon(icon_name, 16, icon_color)
        ico.setStyleSheet(ico.styleSheet() + "border: none;")
        l.addWidget(ico)
        
        txt = QLabel(f"{label}: <span style='color:{status_color}'>{status_text}</span>")
        txt.setTextFormat(Qt.RichText)
        txt.setStyleSheet("font-size: 12px; color: #64748b; font-weight: 600; border: none;")
        l.addWidget(txt)
        
        return item_w
