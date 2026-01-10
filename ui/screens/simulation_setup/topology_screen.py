from PySide6.QtWidgets import (
    QLabel, QGridLayout, QVBoxLayout, QFrame, QHBoxLayout, QSlider, QSizePolicy, QButtonGroup
)
from PySide6.QtCore import Qt
from ui.utils.base import create_icon, create_card
from ui.components import PrimaryButton
from .base_wizard import WizardScreen

class TopologySelectionScreen(WizardScreen):
    def __init__(self):
        super().__init__(1)
        self._setup_ui()

    def get_selected_topology(self) -> str:
        btn = self.group.checkedButton()
        if not btn:
            return getattr(self, "default_topology", "random")
        val = btn.property("topology_key")
        return val if val else getattr(self, "default_topology", "random")

    def get_node_count(self) -> int:
        if hasattr(self, 'scale_slider'):
            return int(self.scale_slider.value())
        return 50

    def _get_next_text(self):
        return "Next: Virus"

    def _setup_ui(self):
        # Title
        title = QLabel("Choose Network Topology")
        title.setObjectName("h2")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #1e293b; margin-bottom: 8px;")
        title.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(title)
        
        subtitle = QLabel("The network structure determines how nodes interact and how threats propagate.")
        subtitle.setStyleSheet("color: #64748b; font-size: 14px; margin-bottom: 24px;")
        subtitle.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(subtitle)
        
        # Grid of Cards
        grid = QGridLayout()
        grid.setSpacing(24)
        for i in range(4):
            grid.setColumnStretch(i, 1)
        
        topologies = [
            ("star", "Star (Hub)", "Centralized vulnerability. Fast spread from center.", "hub"),
            ("mesh", "Mesh", "High redundancy. Multiple paths make it difficult to isolate.", "share"),
            ("grid", "Grid", "Lattice structure. Infection spreads in a wave-like pattern.", "grid_view"),
            ("ring", "Ring", "Sequential infection. Linear propagation path.", "sync"),
            ("tree", "Tree", "Hierarchical spread. Infection travels branches.", "account_tree"),
            ("random", "Random", "Unpredictable paths. Represents chaos.", "shuffle"),
        ]
        
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        
        row, col = 0, 0
        self._topology_keys = [t[0] for t in topologies]
        
        grid.setColumnStretch(0, 1); grid.setColumnStretch(1, 1); grid.setColumnStretch(2, 1) 

        for key, name, desc, icon in topologies:
            btn = PrimaryButton("")
            btn.setCheckable(True)
            btn.setMinimumHeight(180)
            btn.setProperty("topology_key", key)
            btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: white; 
                    border: 1px solid #e2e8f0; 
                    border-radius: 20px;
                    text-align: left;
                    padding: 0;
                }
                QPushButton:checked {
                    background: #f0fdf4; 
                    border: 2px solid #0d9488;
                }
                QPushButton:hover:!checked {
                    background: #f8fafc;
                    border: 1px solid #cbd5e1;
                }
            """)
            # Inner Layout
            l = QVBoxLayout(btn)
            l.setContentsMargins(24, 24, 24, 24)
            l.setSpacing(12)
            # Icon Container
            ico_frame = QFrame()
            ico_frame.setFixedSize(48, 48)
            ico_frame.setStyleSheet("background: #f1f5f9; border-radius: 20px;")
            ifl = QVBoxLayout(ico_frame)
            ifl.setContentsMargins(0,0,0,0)
            ifl.setAlignment(Qt.AlignCenter)
            ifl.addWidget(create_icon(icon, 24, "#0d9488"))
            t = QLabel(name)
            t.setStyleSheet("font-weight: 800; font-size: 15px; color: #0f172a; border: none; background: transparent;")
            d = QLabel(desc)
            d.setStyleSheet("color: #64748b; font-size: 12px; line-height: 1.4; border: none; background: transparent;")
            d.setWordWrap(True)
            l.addWidget(ico_frame)
            l.addWidget(t)
            l.addWidget(d)
            l.addStretch()
            self.group.addButton(btn)
            grid.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        self.content_layout.addLayout(grid)
        self.content_layout.addSpacing(40)
        
        # Scale Slider
        scale_card = create_card()
        scale_card.setStyleSheet("background: white; border-radius: 20px; border: 1px solid #e2e8f0;")
        sc_layout = QHBoxLayout(scale_card)
        sc_layout.setContentsMargins(30,30,30,30)
        
        # Icon Box
        ib = QFrame()
        ib.setFixedSize(48, 48)
        ib.setStyleSheet("background: #f0fdf4; border-radius: 20px;")
        ibl = QVBoxLayout(ib); ibl.setContentsMargins(0,0,0,0); ibl.setAlignment(Qt.AlignCenter)
        ibl.addWidget(create_icon("hub", 24, "#16a34a"))
        
        info_col = QVBoxLayout()
        info_col.setSpacing(4)
        lbl = QLabel("Network Scale")
        lbl.setStyleSheet("font-weight: 800; font-size: 14px; color: #0f172a; border: none;")
        sub = QLabel("Adjust the number of nodes in the simulation graph.")
        sub.setStyleSheet("color: #64748b; font-size: 12px; border: none;")
        info_col.addWidget(lbl)
        info_col.addWidget(sub)
        
        slider = QSlider(Qt.Horizontal)
        slider.setRange(10, 250)
        slider.setValue(50)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #e2e8f0;
                height: 8px;
                background: #f1f5f9;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0f172a;
                border: 2px solid white; 
                width: 20px;
                height: 20px;
                line-height: 20px;
                margin: -7px 0;
                border-radius: 11px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            QSlider::sub-page:horizontal {
                background: #0f172a;
                border-radius: 4px;
            }
        """)
        
        val_lbl = QLabel(" 50 Nodes ")
        val_lbl.setFixedWidth(110)
        val_lbl.setAlignment(Qt.AlignCenter)
        val_lbl.setStyleSheet("background: #0f172a; color: white; padding: 6px 10px; border-radius: 8px; font-weight: bold; font-family: 'Space Grotesk';")
        slider.valueChanged.connect(lambda v: val_lbl.setText(f" {v} Nodes "))
        
        sc_layout.addLayout(info_col)
        sc_layout.addSpacing(20)
        sc_layout.addWidget(slider, 1)
        sc_layout.addSpacing(20)
        sc_layout.addWidget(val_lbl)

        self.content_layout.addWidget(scale_card)
        self.scale_slider = slider
        # Disable next until a topology is selected
        try:
            self.footer.next_btn.setEnabled(False)
        except Exception:
            pass
        # Enable next when a topology is chosen
        self.group.buttonClicked.connect(lambda _: self.footer.next_btn.setEnabled(True))
        self.content_layout.addStretch()

    def reset(self):
        """Reset the screen to its initial state."""
        # Uncheck all buttons
        if self.group.checkedButton():
            self.group.setExclusive(False)
            self.group.checkedButton().setChecked(False)
            self.group.setExclusive(True)
        
        # Reset scale slider
        if hasattr(self, 'scale_slider'):
            self.scale_slider.setValue(50)
            
        # Disable next button if possible (handled by signal usually but good to enforce)
        if hasattr(self, 'footer'):
             self.footer.next_btn.setEnabled(False)

    def is_complete(self) -> bool:
        """Check if a topology is selected."""
        return self.group.checkedButton() is not None
