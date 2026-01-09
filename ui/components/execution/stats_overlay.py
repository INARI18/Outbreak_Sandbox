from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton
from ui.theme import Theme

class StatsOverlay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        
        self.lbl_infection_val = QLabel("0%")
        self.lbl_infection_val.setStyleSheet(f"font-size: 18px; font-weight: 800; font-family: 'Space Grotesk'; color: {Theme.PRIMARY};")

        self.lbl_step_val = QLabel("0")
        self.lbl_step_val.setStyleSheet(f"font-size: 18px; font-weight: 800; font-family: 'Space Grotesk'; color: {Theme.TEXT_PRIMARY};")
        
        self.lbl_nodes_val = QLabel("0")
        self.lbl_nodes_val.setStyleSheet(f"font-size: 18px; font-weight: 800; font-family: 'Space Grotesk'; color: {Theme.TEXT_PRIMARY};")
        
        self.layout.addWidget(self._glass_stat("Infection", self.lbl_infection_val))
        self.layout.addWidget(self._glass_stat("Step", self.lbl_step_val))
        self.layout.addWidget(self._glass_stat("Nodes", self.lbl_nodes_val))
        self.layout.addStretch()
        
        # Zoom placeholder could go here
    
    def _glass_stat(self, label, val_widget):
        f = QFrame()
        f.setStyleSheet(f"background: rgba(255,255,255,0.9); border-radius: 12px; border: 1px solid {Theme.BORDER};")
        v = QVBoxLayout(f)
        v.setContentsMargins(12, 8, 12, 8)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: 10px; font-weight: bold; text-transform: uppercase; color: {Theme.TEXT_SECONDARY}; background: transparent; border: none;")
        val_box = QHBoxLayout()
        val_widget.setStyleSheet(val_widget.styleSheet() + "background: transparent; border: none;")
        val_box.addWidget(val_widget)
        v.addWidget(lbl)
        v.addLayout(val_box)
        return f

    def update_stats(self, infection_rate, step, total_nodes):
        self.lbl_infection_val.setText(f"{infection_rate:.1f}%")
        self.lbl_step_val.setText(str(step))
        self.lbl_nodes_val.setText(str(total_nodes))
