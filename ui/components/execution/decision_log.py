from PySide6.QtWidgets import QListWidget, QListWidgetItem, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from ui.utils.base import create_icon, create_card
from ui.components.common.badge import Badge
from ui.theme import Theme
from PySide6.QtCore import Qt

class DecisionLog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)
        
        self.card = create_card()
        col1_layout = QVBoxLayout(self.card)
        col1_layout.setContentsMargins(10, 15, 10, 15)
        
        # Header
        c1_head = QHBoxLayout()
        c1_head.addWidget(create_icon("neurology", 20, Theme.PRIMARY))
        c1_title = QLabel("DECISION ENGINE")
        c1_title.setStyleSheet(f"font-weight: bold; font-size: 12px; letter-spacing: 0.5px; color: {Theme.TEXT_PRIMARY}")
        c1_head.addWidget(c1_title)

        c1_head.addStretch()
        self.live_badge = Badge("READY", theme="gray")
        c1_head.addWidget(self.live_badge)
        col1_layout.addLayout(c1_head)
        
        col1_layout.addWidget(QLabel(f"<hr style='color:{Theme.BORDER}'>"))

        # List of decisions
        self.decision_list = QListWidget()
        self.decision_list.setFrameShape(QFrame.NoFrame)
        self.decision_list.setStyleSheet(f"""
             QListWidget {{
                 background: transparent;
                 outline: none;
             }}
             QListWidget::item {{
                 border-bottom: 1px solid {Theme.BORDER};
                 padding: 8px 0;
                 color: {Theme.TEXT_PRIMARY};
             }}
             QListWidget::item:selected {{
                 background: transparent;
                 color: inherit;
             }}
        """)
        self.decision_list.setWordWrap(True)
        self.decision_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        col1_layout.addWidget(self.decision_list)
        
        # AI Mode Indication
        bottom_row = QHBoxLayout()
        self.ai_mode_badge = Badge("CLOUD AI", theme="blue") # Default text
        bottom_row.addStretch()
        bottom_row.addWidget(self.ai_mode_badge)
        bottom_row.addStretch()
        
        col1_layout.addLayout(bottom_row)
        
        # Layout widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.card)

    def add_decision(self, step, text):
        it = QListWidgetItem(f"STEP {step}: {text}")
        self.decision_list.addItem(it)
        self.decision_list.scrollToBottom()

    def set_engine_state(self, state):
        self.live_badge.setText(state)
        # Simple color mapping for state
        if state == "THINKING":
            self.live_badge.set_theme("blue")
        elif state == "INFECTING":
            self.live_badge.set_theme("red")
        else:
            self.live_badge.set_theme("gray")

    def set_ai_mode(self, mode_text, theme="blue"):
        self.ai_mode_badge.setText(mode_text)
        self.ai_mode_badge.set_theme(theme)
