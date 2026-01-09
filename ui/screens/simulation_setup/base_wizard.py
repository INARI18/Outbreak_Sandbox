from PySide6.QtWidgets import (
    QVBoxLayout, QWidget, QScrollArea, QFrame
)
from ui.utils.base import NativeBase
from ui.components import StandardHeader
from .wizard_header import WizardHeader
from .wizard_footer import WizardFooter

class WizardScreen(NativeBase):
    def __init__(self, step_index):
        super().__init__()
        self.step_index = step_index
        
        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Navbar (Simple)
        self._build_navbar()
        
        # Scroll Area for Content
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: #f8fafc;")
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(30)
        
        # Wizard Progress Header
        self._build_wizard_header()
        
        self.scroll.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll)
        
        # Footer
        self._build_footer()

    def _build_navbar(self):
        self.header = StandardHeader()
        self.header.dashboard_requested.connect(self.dashboard_requested.emit)
        self.main_layout.addWidget(self.header)

    def _build_wizard_header(self):
        header = WizardHeader(self.step_index)
        self.content_layout.addWidget(header)

    def _build_footer(self):
        self.footer = WizardFooter(self._get_next_text())
        self.footer.back_clicked.connect(self.back_requested.emit)
        self.footer.next_clicked.connect(self.next_requested.emit)
        self.main_layout.addWidget(self.footer)

    def _get_next_text(self):
        return "Next: Step " + str(self.step_index + 1)
