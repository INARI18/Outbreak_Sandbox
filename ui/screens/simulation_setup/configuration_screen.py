import random
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QButtonGroup, 
    QLineEdit, QCheckBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from ui.screens.utils.base import create_card, create_icon, create_pixmap
from .base_wizard import WizardScreen

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
        dice_btn.setIcon(create_pixmap("casino", 18, "#0d9488"))
        dice_btn.setCursor(Qt.PointingHandCursor)
        dice_btn.setToolTip("Generate a random seed")
        dice_btn.setEnabled(False)

        def _generate_seed():
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
