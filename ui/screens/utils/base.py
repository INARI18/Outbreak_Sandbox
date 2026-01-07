from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QLabel, QFrame, QPushButton
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont

# --- Helpers ---

def create_icon(name: str, size: int = 24, color: str = "#475569") -> QLabel:
    """Creates a text-based icon using Material Symbols Outlined font (returned as QLabel widget)."""
    lbl = QLabel(name)
    lbl.setProperty("class", "icon")
    lbl.setStyleSheet(f"font-size: {size}px; color: {color}; font-family: 'Material Symbols Outlined';")
    lbl.setAlignment(Qt.AlignCenter)
    return lbl

def create_pixmap(name: str, size: int = 24, color: str = "#475569") -> QPixmap:
    """Creates a QPixmap from a font icon."""
    # Scale for high DPI if needed, but keeping simple for now
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.TextAntialiasing)
    
    font = QFont("Material Symbols Outlined")
    font.setPixelSize(size)
    painter.setFont(font)
    painter.setPen(QColor(color))
    
    painter.drawText(pix.rect(), Qt.AlignCenter, name)
    painter.end()
    return pix

def create_qicon(name: str, size: int = 24, color: str = "#475569") -> QIcon:
    """Creates a QIcon from a font icon."""
    return QIcon(create_pixmap(name, size, color))

def create_card() -> QFrame:
    f = QFrame()
    f.setObjectName("card")
    return f

class NativeBase(QWidget):
    next_requested = Signal()
    back_requested = Signal()
    dashboard_requested = Signal()

    def __init__(self):
        super().__init__()

