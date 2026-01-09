from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

class Badge(QLabel):
    def __init__(self, text="BADGE", color="#64748b", bg_color="#f1f5f9", theme=None, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        
        if theme:
            self.set_theme(theme)
        else:
            self.bg_color = bg_color
            self.text_color = color
            self._update_style()
        
    def _update_style(self):
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {self.bg_color};
                color: {self.text_color};
                font-size: 11px;
                font-weight: 700;
                border-radius: 6px;
                padding: 4px 12px;
                border: 1px solid {self.text_color};
            }}
        """)
        self.adjustSize()

    def set_theme(self, theme="gray"):
        themes = {
            "gray": ("#64748b", "#f1f5f9"),
            "green": ("#059669", "#ecfdf5"),
            "blue": ("#3b82f6", "#eff6ff"),
            "yellow": ("#eab308", "#fefce8"),
            "red": ("#be123c", "#fff1f2"),
            "purple": ("#9333ea", "#f3e8ff")
        }
        color, bg = themes.get(theme, themes["gray"])
        self.bg_color = bg
        self.text_color = color
        self._update_style()
