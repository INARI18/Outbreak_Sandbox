from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from ui.utils.base import NativeBase

class GenericStyledScreen(NativeBase):
    def __init__(self, title_text):
        super().__init__()
        l = QVBoxLayout(self)
        l.setContentsMargins(40, 40, 40, 40)
        
        header = QLabel(title_text)
        header.setObjectName("h2")
        l.addWidget(header)
        l.addStretch()
        
        # Footer
        nav = QHBoxLayout()
        b = QPushButton("Back")
        b.clicked.connect(lambda: self.back_requested.emit())
        n = QPushButton("Continue")
        n.setObjectName("primary")
        n.clicked.connect(lambda: self.next_requested.emit())
        nav.addWidget(b)
        nav.addStretch()
        nav.addWidget(n)
        l.addLayout(nav)
