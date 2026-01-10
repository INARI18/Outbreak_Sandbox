from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QWidget, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal
from ui.utils.base import create_icon
from ui.components import PrimaryButton

class ConfigurationWorkflowCard(QFrame):
    continue_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet("""
            #card {
                background: white; 
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
            QPushButton {
                border-radius: 20px;
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
        
        self.sys_title = QLabel("Configuration Workflow")
        self.sys_title.setStyleSheet("font-weight: 800; font-size: 18px; color: #1e293b; border: none; background: transparent;")
        
        self.sys_sub = QLabel("0 of 3 Modules Configured")
        self.sys_sub.setStyleSheet("color: #64748b; font-size: 14px; font-weight: 500; border: none; background: transparent;")
        
        text_col.addWidget(self.sys_title)
        text_col.addWidget(self.sys_sub)
        
        top_row.addLayout(text_col)
        top_row.addStretch()
        
        self.perc_lbl = QLabel("0%")
        self.perc_lbl.setStyleSheet("font-family: 'Space Grotesk'; font-weight: 800; font-size: 24px; color: #1e293b; border: none; background: transparent;") 
        top_row.addWidget(self.perc_lbl)
        
        layout.addLayout(top_row)
        
        # Progress Bar
        self.pbar = QProgressBar()
        self.pbar.setFixedHeight(6)
        self.pbar.setTextVisible(False)
        self.pbar.setRange(0, 100)
        self.pbar.setValue(0)
        self.pbar.setStyleSheet("""
            QProgressBar {
                background-color: #f1f5f9;
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #0f172a; /* Dark Slate theme */
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.pbar)
        
        self.status_container = QWidget()
        self.status_layout = QHBoxLayout(self.status_container)
        self.status_layout.setContentsMargins(0,0,0,0)
        self.status_layout.setSpacing(15)
        layout.addWidget(self.status_container)
        
        # Bottom Button
        btn_row = QHBoxLayout()
        from PySide6.QtWidgets import QPushButton
        self.continue_btn = QPushButton("Resume")
        self.continue_btn.setFixedSize(100, 32)
        self.continue_btn.setCursor(Qt.PointingHandCursor)
        self.continue_btn.setStyleSheet("""
            QPushButton {
                background: #0f172a;
                color: white;
                border: 1px solid #0f172a;
                border-radius: 16px;
                font-size: 12px;
                font-family: 'Space Grotesk';
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1e293b;
                border: 1px solid #334155;
            }
            QPushButton:disabled {
                background: #cbd5e1;
                color: white;
                border: none;
            }
        """)
        self.continue_btn.clicked.connect(self.continue_clicked.emit)
        self.continue_btn.clicked.connect(self.continue_clicked.emit)
        btn_row.addWidget(self.continue_btn)
        btn_row.addStretch()
        layout.addSpacing(10)
        layout.addLayout(btn_row)
        
        # Initial Render
        self.update_progress(False, False, False)

    def update_progress(self, topology_ready: bool, virus_ready: bool, config_ready: bool):
        # Calculate completion
        steps = [topology_ready, virus_ready, config_ready]
        
        # Determine current step index for label
        completed_count = sum(1 for s in steps if s)
        
        self.sys_sub.setText(f"{completed_count} of 3 Modules Configured")
        
        percent = int( (completed_count / 3) * 100 )
        self.perc_lbl.setText(f"{percent}%")
        self.pbar.setValue(percent)
        
        # Clear status layout
        while self.status_layout.count():
            child = self.status_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Rebuild Status Items
        # Topology
        if topology_ready:
            self.status_layout.addWidget(self._create_status_item("Topology", "Ready", "#10b981", "check_circle", "#10b981"))
        else:
             self.status_layout.addWidget(self._create_status_item("Topology", "Pending", "#ef4444", "error", "#ef4444"))

        # Virus
        if virus_ready:
            self.status_layout.addWidget(self._create_status_item("Virus", "Ready", "#10b981", "check_circle", "#10b981"))
        else:
             self.status_layout.addWidget(self._create_status_item("Virus", "Pending", "#f59e0b", "schedule", "#f59e0b"))

        # Mode
        if config_ready:
            self.status_layout.addWidget(self._create_status_item("Mode", "Ready", "#10b981", "check_circle", "#10b981"))
        else:
             self.status_layout.addWidget(self._create_status_item("Mode", "Pending", "#f59e0b", "schedule", "#f59e0b"))

        self.status_layout.addStretch()
        
        # Button State
        if completed_count == 0:
            self.continue_btn.setEnabled(False)
            self.continue_btn.setStyleSheet("""
                QPushButton {
                    background: #cbd5e1;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-size: 12px;
                    font-family: 'Space Grotesk';
                    font-weight: bold;
                }
            """)
        else:
            self.continue_btn.setEnabled(True)
            self.continue_btn.setStyleSheet("""
                QPushButton {
                    background: #0f172a;
                    color: white;
                    border: 1px solid #0f172a;
                    border-radius: 20px;
                    font-size: 12px;
                    font-family: 'Space Grotesk';
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #1e293b;
                    border: 1px solid #334155;
                }
            """)



    def _create_status_item(self, label, status_text, status_color, icon_name, icon_color):
        item_w = QWidget()
        item_w.setAttribute(Qt.WA_TranslucentBackground)
        item_w.setStyleSheet("background: transparent;")
        l = QHBoxLayout(item_w)
        l.setContentsMargins(0,0,0,0)
        l.setSpacing(6)
        
        sep = QLabel("|")
        sep.setStyleSheet("color: #cbd5e1; font-weight: bold; border: none; background: transparent;")
        l.addWidget(sep)
        
        ico = create_icon(icon_name, 16, icon_color)
        ico.setStyleSheet(ico.styleSheet() + "border: none; background: transparent;")
        l.addWidget(ico)
        
        txt = QLabel(f"{label}: <span style='color:{status_color}'>{status_text}</span>")
        txt.setTextFormat(Qt.RichText)
        txt.setStyleSheet("font-size: 12px; color: #64748b; font-weight: 600; border: none; background: transparent;")
        l.addWidget(txt)
        
        return item_w
