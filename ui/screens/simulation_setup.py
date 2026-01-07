from PySide6.QtCore import Qt
import random
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, 
    QGridLayout, QWidget, QScrollArea, QSlider, QLineEdit, QRadioButton, QButtonGroup, QCheckBox, QSizePolicy
)
from ui.screens.utils.base import NativeBase, create_icon, create_card, create_pixmap
from ui.components import PrimaryButton, StandardHeader, WizardFooter

# -----------------------------------------------------------------------------
# Base Wizard Screen
# -----------------------------------------------------------------------------
class WizardScreen(NativeBase):
    def __init__(self, step_index):
        super().__init__()
        self.step_index = step_index # 1-based: 1=Topology, 2=Virus, 3=Config
        
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
        container = QFrame()
        # container.setStyleSheet("background: pink;")
        l = QHBoxLayout(container)
        l.setSpacing(0)
        l.setContentsMargins(100, 0, 100, 0)
        
        steps = [
            (1, "TOPOLOGY", "hub"),
            (2, "VIRUS", "coronavirus"),
            (3, "CONFIG", "tune"),
            (4, "RUN", "play_arrow")
        ]
        
        for idx, label, icon_name in steps:
            # Line connector (before item, except first)
            if idx > 1:
                line = QFrame()
                line.setFixedHeight(2)
                color = "#0d9488" if idx <= self.step_index else "#e2e8f0"
                line.setStyleSheet(f"background: {color}; margin-top: 15px;")
                l.addWidget(line, 1) # stretch 1
                
            # Step Item
            item = QVBoxLayout()
            item.setSpacing(8)
            
            # Circle
            active = idx <= self.step_index
            current = idx == self.step_index
            
            circle = QLabel(str(idx) if not active else "") 
            circle.setFixedSize(32, 32)
            circle.setAlignment(Qt.AlignCenter)
            
            if current:
                 circle.setStyleSheet("background: #0d9488; color: white; border-radius: 16px; font-weight: bold;")
                 circle.setPixmap(create_pixmap(icon_name, 18, "white"))
            elif active:
                 circle.setStyleSheet("background: #ccfbf1; color: #0d9488; border-radius: 16px; font-weight: bold;")
                 circle.setText("✓")
            else:
                 circle.setStyleSheet("background: #f1f5f9; color: #94a3b8; border-radius: 16px; font-weight: bold;")
                 circle.setText(str(idx))

            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {'#0d9488' if current else '#94a3b8'};")
            
            item.addWidget(circle, 0, Qt.AlignCenter)
            item.addWidget(lbl, 0, Qt.AlignCenter)
            
            l.addLayout(item)
            
        self.content_layout.addWidget(container)

    def _build_footer(self):
        self.footer = WizardFooter(self._get_next_text())
        self.footer.back_clicked.connect(self.back_requested.emit)
        self.footer.next_clicked.connect(self.next_requested.emit)
        self.main_layout.addWidget(self.footer)

    def _get_next_text(self):
        return "Next: Step " + str(self.step_index + 1)

# -----------------------------------------------------------------------------
# 1. Topology Selection
# -----------------------------------------------------------------------------
class TopologySelectionScreen(WizardScreen):
    def __init__(self):
        super().__init__(1)
        self._setup_ui()

    def get_selected_topology(self) -> str:
        """Return the key of the selected topology (e.g. 'random', 'mesh')."""
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
        title.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(title)
        
        subtitle = QLabel("Define the battlefield. The structural layout determines how nodes interact.")
        subtitle.setStyleSheet("color: #64748b; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(subtitle)
        
        self.content_layout.addSpacing(20)
        
        # Grid of Cards
        grid = QGridLayout()
        grid.setSpacing(20)
        for i in range(4):
            grid.setColumnStretch(i, 1)
        
        topologies = [
            ("star", "Star (Hub)", "Centralized vulnerability.\nFast spread from center.", "hub"),
            ("mesh", "Mesh", "High redundancy. Multiple\npaths make it difficult to isolate.", "share"),
            ("grid", "Grid", "Lattice structure. Infection\nspreads in a wave-like pattern.", "grid_view"),
            ("ring", "Ring", "Sequential infection.\nLinear propagation path.", "sync"),
            ("tree", "Tree", "Hierarchical spread.\nInfection travels branches.", "account_tree"),
            ("random", "Random", "Unpredictable paths.\nRepresents chaos.", "shuffle"),
        ]
        
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        
        row, col = 0, 0
        # keep mapping of topology keys so MainWindow can query selection
        self._topology_keys = [t[0] for t in topologies]
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)

        for key, name, desc, icon in topologies:
            btn = QPushButton()
            btn.setCheckable(True)
            # Make it square-ish
            btn.setMinimumHeight(240)
            btn.setMaximumWidth(280)

            # store key on the button for later retrieval
            btn.setProperty("topology_key", key)

            # Using Fixed/Preferred policy so it doesn't stretch too much horizontally
            btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            btn.setCursor(Qt.PointingHandCursor)
            # Custom stylesheet for selection
            btn.setStyleSheet("""
                QPushButton {
                    background: white; border: 2px solid #e2e8f0; border-radius: 16px;
                    text-align: left;
                }
                QPushButton:checked {
                    border: 2px solid #0d9488; background: #f0fdf4;
                }
                QPushButton:hover:!checked {
                    border-color: #cbd5e1;
                }
            """)
            
            # Inner Layout
            l = QVBoxLayout(btn)
            l.setContentsMargins(20, 20, 20, 20)
            ico = create_icon(icon, 32, "#0d9488")
            t = QLabel(name)
            t.setStyleSheet("font-weight: bold; font-size: 14px; border: none; background: transparent;")
            d = QLabel(desc)
            d.setStyleSheet("color: #64748b; font-size: 11px; border: none; background: transparent;")
            d.setWordWrap(True)
            
            l.addWidget(ico)
            l.addSpacing(10)
            l.addWidget(t)
            l.addWidget(d)
            l.addStretch()
            
            self.group.addButton(btn)
            grid.addWidget(btn, row, col)
            
            col += 1
            if col > 3:
                col = 0
                row += 1

        self.content_layout.addLayout(grid)
        self.content_layout.addSpacing(30)
        
        # Scale Slider
        scale_card = create_card()
        sc_layout = QHBoxLayout(scale_card)
        sc_layout.setContentsMargins(30,30,30,30)
        
        icon = create_icon("tune", 24, "#0d9488")
        lbl = QLabel("Network Scale")
        lbl.setStyleSheet("font-weight: bold;")
        
        slider = QSlider(Qt.Horizontal)
        slider.setRange(10, 1000)
        slider.setValue(50)
        slider.setStyleSheet("QSlider::handle:horizontal { background: #0d9488; }")
        
        val_lbl = QLabel("50 Nodes")
        val_lbl.setStyleSheet("background: #f1f5f9; padding: 5px 10px; border-radius: 6px; font-weight: bold;")
        slider.valueChanged.connect(lambda v: val_lbl.setText(f"{v} Nodes"))
        
        sc_layout.addWidget(icon)
        sc_layout.addWidget(lbl)
        sc_layout.addSpacing(20)
        sc_layout.addWidget(slider)
        sc_layout.addSpacing(20)
        sc_layout.addWidget(val_lbl)

        self.content_layout.addWidget(scale_card)
        # expose slider for other modules to read configured node count
        self.scale_slider = slider
        # Disable next until a topology is selected
        try:
            self.footer.next_btn.setEnabled(False)
        except Exception:
            pass

        # Enable next when a topology is chosen
        self.group.buttonClicked.connect(lambda _: self.footer.next_btn.setEnabled(True))
        self.content_layout.addStretch()

# -----------------------------------------------------------------------------
# 2. Virus Selection
# -----------------------------------------------------------------------------
class VirusSelectionScreen(WizardScreen):
    def __init__(self):
        super().__init__(2)
        self._setup_ui()

    def _get_next_text(self):
        return "Next: Config"

    def _setup_ui(self):
        title = QLabel("Select Simulation Strain")
        title.setObjectName("h2")
        title.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(title)
        
        # Filters (Mock)
        filters_layout = QHBoxLayout()
        filters_layout.setAlignment(Qt.AlignCenter)
        for f in ["All Types", "Ransomware", "Trojan", "Worm", "Botnet"]:
            btn = QPushButton(f)
            btn.setCheckable(True)
            if f == "All Types": btn.setChecked(True)
            btn.setFixedHeight(32)
            btn.setStyleSheet("""
                QPushButton { border-radius: 16px; padding: 0 15px; border: 1px solid #e2e8f0; background: white; color: #64748b; }
                QPushButton:checked { background: #0d9488; color: white; border: none; }
            """)
            filters_layout.addWidget(btn)
        self.content_layout.addLayout(filters_layout)
        self.content_layout.addSpacing(30)
        
        # Virus Cards
        virus_layout = QHBoxLayout()
        viruses = [
            ("WannaCry-X", "Ransomware", 85, 92, 20),
            ("Stuxnet-Sim", "Worm", 60, 45, 95),
            ("Mirai-Bot", "Botnet", 40, 75, 60)
        ]
        
        self.group = QButtonGroup(self)
        
        for name, vtype, atk, spd, stl in viruses:
            card = QPushButton()
            card.setCheckable(True)
            # Make it tall and narrow (vertical rectangle)
            card.setFixedSize(280, 420)
            # expose identity so the app can query which virus was selected
            card.setProperty("virus_name", name)
            card.setCursor(Qt.PointingHandCursor)
            card.setStyleSheet("""
                QPushButton { background: white; border: 2px solid #e2e8f0; border-radius: 16px; text-align: left; }
                QPushButton:checked { border: 2px solid #0d9488; }
            """)
            
            # Logic to construct visual inside button... technically complex in Qt with stylesheets alone
            # But we can set a layout on the button
            vl = QVBoxLayout(card)
            
            # Icon
            top = QHBoxLayout()
            icon_bg = QFrame()
            icon_bg.setFixedSize(40,40)
            if vtype == "Ransomware": icon_bg.setStyleSheet("background: #fee2e2; border-radius: 20px;")
            else: icon_bg.setStyleSheet("background: #fef3c7; border-radius: 20px;")
            
            il = QVBoxLayout(icon_bg)
            il.setContentsMargins(0,0,0,0)
            il.addWidget(create_icon("bug_report", 20, "#ef4444" if vtype=="Ransomware" else "#d97706"), 0, Qt.AlignCenter)
            
            pill = QLabel(vtype)
            pill.setStyleSheet(f"background: {'#fee2e2' if vtype=='Ransomware' else '#fef3c7'}; color: {'#991b1b' if vtype=='Ransomware' else '#92400e'}; padding: 4px 8px; border-radius: 6px; font-size: 10px; font-weight: bold;")
            
            top.addWidget(icon_bg)
            top.addStretch()
            top.addWidget(pill)
            vl.addLayout(top)
            
            # Big Icon
            vl.addStretch()
            shield = create_icon("shield" if vtype=="Worm" else "local_hospital", 64, "#cbd5e1")
            vl.addWidget(shield, 0, Qt.AlignCenter)
            vl.addStretch()

            # Name
            vn = QLabel(name)
            vn.setStyleSheet("font-weight: bold; font-size: 16px; border: none;")
            vl.addWidget(vn, 0, Qt.AlignCenter)
            
            # Stats
            sl = QGridLayout()
            sl.setSpacing(5)
            self._add_stat(sl, 0, "Attack", atk)
            self._add_stat(sl, 1, "Speed", spd)
            self._add_stat(sl, 2, "Stealth", stl)
            
            vl.addLayout(sl)
            
            self.group.addButton(card)
            virus_layout.addWidget(card)
            
        self.content_layout.addLayout(virus_layout)
        # Disable next until virus selected
        try:
            self.footer.next_btn.setEnabled(False)
        except Exception:
            pass
        self.group.buttonClicked.connect(lambda _: self.footer.next_btn.setEnabled(True))
        self.content_layout.addStretch()

    def get_selected_virus_name(self) -> str | None:
        """Return the name of the selected virus card or None."""
        btn = self.group.checkedButton()
        if not btn:
            return None
        return btn.property("virus_name")

    def _add_stat(self, layout, row, label, val):
        l = QLabel(label)
        l.setStyleSheet("color: #64748b; font-size: 10px; border: none;")
        
        bar = QFrame()
        bar.setFixedHeight(4)
        bar.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0d9488, stop:{val/100} #0d9488, stop:{val/100+0.01} #e2e8f0); border-radius: 2px;")
        
        v = QLabel(f"{val}%")
        v.setStyleSheet("font-size: 10px; font-weight: bold; border: none;")
        
        layout.addWidget(l, row, 0)
        layout.addWidget(bar, row, 1)
        layout.addWidget(v, row, 2)

# -----------------------------------------------------------------------------
# 3. Simulation Configuration
# -----------------------------------------------------------------------------
class SimulationConfigurationScreen(WizardScreen):
    def __init__(self):
        super().__init__(3)
        self._setup_ui()

    def _get_next_text(self):
        return "Initialize Environment"

    def _setup_ui(self):
        title = QLabel("Configure Outbreak Parameters")
        title.setObjectName("h2")
        title.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(title)
        
        card = create_card()
        # Ensure card has a specific background for visibility on white
        card.setStyleSheet("QFrame#card { background: white; border: 1px solid #e2e8f0; border-radius: 16px; }")
        
        cl = QVBoxLayout(card)
        cl.setContentsMargins(40,40,40,40)
        cl.setSpacing(25)
        
        # 1. Mode
        ml = QHBoxLayout()
        ico = create_icon("shuffle", 24, "#0d9488")
        circle = QLabel("1")
        circle.setStyleSheet("background: #0d9488; color: white; border-radius: 12px; font-weight: bold; min-width: 24px; min-height: 24px; qproperty-alignment: AlignCenter;")
        
        lbl = QLabel("Simulation Mode")
        lbl.setStyleSheet("font-weight: bold; font-size: 16px; background: transparent;")
        
        ml.addWidget(circle)
        ml.addSpacing(10)
        ml.addWidget(lbl)
        ml.addStretch()
        cl.addLayout(ml)
        
        mode_box = QHBoxLayout()
        # Mode buttons (must choose one to proceed)
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        for m, desc in [("Stochastic", "Randomized events based on probability."), ("Deterministic", "Fixed seed for reproducible results.")]:
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setMinimumHeight(80)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { border: 1px solid #e2e8f0; border-radius: 12px; text-align: left; padding: 15px; }
                QPushButton:checked { border: 2px solid #0d9488; background: #f0fdf4; }
            """)
            l = QVBoxLayout(btn)
            t = QLabel(m)
            t.setStyleSheet("font-weight: bold; border: none; background: transparent;")
            d = QLabel(desc)
            d.setStyleSheet("color: #64748b; font-size: 11px; border: none; background: transparent;")
            d.setWordWrap(True)
            l.addWidget(t)
            l.addWidget(d)
            mode_box.addWidget(btn)
            # mark button with a mode_key property for robust detection
            key = "deterministic" if m.lower().startswith("det") else "stochastic"
            btn.setProperty("mode_key", key)
            self.mode_group.addButton(btn)
        # Disable next until a simulation mode is selected
        try:
            self.footer.next_btn.setEnabled(False)
        except Exception:
            pass
        cl.addLayout(mode_box)
        
        # 2. Seed
        sl = QHBoxLayout()
        circle2 = QLabel("2")
        circle2.setStyleSheet("background: #ffffff; color: #0d9488; border: 1px solid #0d9488; border-radius: 12px; font-weight: bold; min-width: 24px; min-height: 24px; qproperty-alignment: AlignCenter;")
        lbl2 = QLabel("Seed Configuration")
        lbl2.setStyleSheet("font-weight: bold; font-size: 16px; background: transparent;")
        
        sl.addWidget(circle2)
        sl.addSpacing(10)
        sl.addWidget(lbl2)
        sl.addStretch()
        cl.addLayout(sl)

        self.seed_input = QLineEdit("84592")
        # Style input and clearly show disabled state via :disabled selector
        self.seed_input.setStyleSheet("QLineEdit { background: #f8fafc; border: 1px solid #e2e8f0; padding: 10px; border-radius: 8px; font-family: monospace; } QLineEdit:disabled { background: #f1f5f9; color: #94a3b8; }")
        # By default seed input is disabled until Deterministic mode is selected
        self.seed_input.setEnabled(False)

        # Add a small dice button to generate a random seed
        seed_row = QHBoxLayout()
        seed_row.addWidget(self.seed_input)
        dice_btn = QPushButton()
        dice_btn.setFixedSize(36, 36)
        # Visual style: when disabled, appear greyed out so user sees it's inactive
        dice_btn.setStyleSheet("QPushButton { background: white; border: 1px solid #e6eef2; border-radius: 8px; } QPushButton:disabled { background: #f1f5f9; color: #94a3b8; border: 1px solid #e6eef2; }")
        try:
            dice_btn.setIcon(create_pixmap("casino", 18, "#0d9488"))
        except Exception:
            # fallback to text if icon missing
            dice_btn.setText("🎲")
        dice_btn.setCursor(Qt.PointingHandCursor)
        dice_btn.setToolTip("Generate a random seed")
        dice_btn.setEnabled(False)

        def _generate_seed():
            # choose a reasonable range for seeds
            val = random.randint(1, 999999999)
            self.seed_input.setText(str(val))

        dice_btn.clicked.connect(_generate_seed)

        seed_row.addWidget(dice_btn)
        cl.addLayout(seed_row)

        # Connect mode selection to enable/disable the seed input and dice
        def _toggle_seed_on_mode(btn):
            # enable Next when any mode is chosen
            try:
                self.footer.next_btn.setEnabled(True)
            except Exception:
                pass

            try:
                mode_key = btn.property("mode_key")
            except Exception:
                mode_key = None

            is_det = (mode_key == "deterministic")
            self.seed_input.setEnabled(is_det)
            dice_btn.setEnabled(is_det)

        self.mode_group.buttonClicked.connect(_toggle_seed_on_mode)
        
        # 3. Execution
        el = QHBoxLayout()
        circle3 = QLabel("3")
        circle3.setStyleSheet("background: #ffffff; color: #0d9488; border: 1px solid #0d9488; border-radius: 12px; font-weight: bold; min-width: 24px; min-height: 24px; qproperty-alignment: AlignCenter;")
        lbl3 = QLabel("Execution Parameters")
        lbl3.setStyleSheet("font-weight: bold; font-size: 16px; background: transparent;")
        
        el.addWidget(circle3)
        el.addSpacing(10)
        el.addWidget(lbl3)
        el.addStretch()
        cl.addLayout(el)
        
        step_box = QFrame()
        step_box.setStyleSheet("background: #f8fafc; border-radius: 8px; padding: 10px;")
        sbl = QHBoxLayout(step_box)
        sbl.addWidget(create_icon("speed", 20, "#64748b"))
        tl = QVBoxLayout()
        tl.addWidget(QLabel("Step-by-step Execution"))
        st = QLabel("Manual clock control for detailed analysis")
        st.setStyleSheet("color: #64748b; font-size: 11px;")
        tl.addWidget(st)
        sbl.addLayout(tl)
        sbl.addStretch()
        
        # Toggle mimic
        self.step_toggle = QCheckBox()
        self.step_toggle.setStyleSheet("QCheckBox::indicator { width: 40px; height: 20px; border-radius: 10px; background: #cbd5e1; } QCheckBox::indicator:checked { background: #0d9488; }")
        sbl.addWidget(self.step_toggle)
        
        cl.addWidget(step_box)

        self.content_layout.addWidget(card)
        self.content_layout.addStretch()

    def get_mode(self):
        """Return 'stochastic' or 'deterministic'."""
        btn = self.mode_group.checkedButton()
        if btn:
            return btn.property("mode_key")
        return None

    def get_seed(self):
        return self.seed_input.text()

    def is_step_mode(self):
        return self.step_toggle.isChecked()


