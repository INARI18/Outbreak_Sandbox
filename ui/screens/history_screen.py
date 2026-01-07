from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, 
    QGridLayout, QWidget, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit
)
from ui.screens.utils.base import NativeBase, create_icon, create_card

class SimulationHistoryProfilesScreen(NativeBase):
    def __init__(self):
        super().__init__()
        
        # Navbar (Reuse logic or keep simple)
        self._build_navbar()
        
        # Main Layout
        self.main = QScrollArea()
        self.main.setWidgetResizable(True)
        self.main.setFrameShape(QFrame.NoFrame)
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(30)
        self.main.setWidget(self.content)
        
        # Container
        self.container_layout = QVBoxLayout(self)
        self.container_layout.setContentsMargins(0,0,0,0)
        self.container_layout.addWidget(self.main)

        # Header
        h_box = QVBoxLayout()
        title = QLabel("Simulation History & Profiles")
        title.setObjectName("h2")
        sub = QLabel("Manage experiment logs, review analysis reports, and configure custom virus definitions.")
        sub.setStyleSheet("color: #64748b; font-size: 14px;")
        h_box.addWidget(title)
        h_box.addWidget(sub)
        self.content_layout.addLayout(h_box)

        # Grid Content
        grid = QGridLayout()
        grid.setSpacing(30)
        
        # --- LEFT: Simulation Logs ---
        logs_card = create_card()
        # ...
        
        # ... (rest of code uses self.layout, need to change to self.content_layout)

        lc_lay = QVBoxLayout(logs_card)
        lc_lay.setContentsMargins(0,0,0,0)
        
        # Logs Header
        lh = QHBoxLayout()
        lh.setContentsMargins(20, 20, 20, 10)
        lh_title = QLabel("Simulation Logs")
        lh_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        search = QLineEdit()
        search.setPlaceholderText("Search logs by ID, virus...")
        search.setFixedWidth(200)
        search.setStyleSheet("border-radius: 15px; padding: 5px 15px; border: 1px solid #e2e8f0; background: #f8fafc;")
        
        lh.addWidget(lh_title)
        lh.addStretch()
        lh.addWidget(search)
        lc_lay.addLayout(lh)
        
        # Filters
        lf = QHBoxLayout()
        lf.setContentsMargins(20, 0, 20, 10)
        for f in ["ALL LOGS", "DETERMINISTIC", "STOCHASTIC", "LAST 24H"]:
            btn = QPushButton(f)
            btn.setCheckable(True)
            if f == "ALL LOGS": 
                btn.setChecked(True)
                btn.setStyleSheet("background: #0d9488; color: white; border: none; border-radius: 12px; padding: 6px 12px; font-size: 10px; font-weight: bold;")
            else:
                btn.setStyleSheet("background: #f1f5f9; color: #64748b; border: none; border-radius: 12px; padding: 6px 12px; font-size: 10px; font-weight: bold;")
            lf.addWidget(btn)
        lf.addStretch()
        lc_lay.addLayout(lf)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Log ID", "Date/Time", "Topology", "Virus Used", "Mode", "Actions"])
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setFrameShape(QFrame.NoFrame)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        table.setStyleSheet("QTableWidget::item { padding: 12px; border-bottom: 1px solid #f1f5f9; color: #334155; } QHeaderView::section { background: white; border-bottom: 2px solid #e2e8f0; }")
        
        rows = [
            ("#SIM-2023-849", "Oct 24, 14:00", "Mesh Network (n=50)", "Polymorphic-Worm-A", "Stochastic"),
            ("#SIM-2023-848", "Oct 24, 09:30", "Star Topology (n=20)", "Trojan.Win32.Test", "Deterministic"),
            ("#SIM-2023-847", "Oct 23, 18:15", "Scale-Free (n=100)", "Ransomware-X", "Stochastic"),
            ("#SIM-2023-846", "Oct 22, 11:45", "Mesh Network (n=50)", "Botnet-Seed-Alpha", "Deterministic"),
            ("#SIM-2023-845", "Oct 21, 14:20", "Ring Topology (n=25)", "Worm.Gen.V4", "Stochastic"),
        ]
        
        table.setRowCount(len(rows))
        for r, row_data in enumerate(rows):
            for c, txt in enumerate(row_data):
                table.setItem(r, c, QTableWidgetItem(txt))
                if c == 4: # Mode Pill
                    item = QTableWidgetItem(txt)
                    if txt == "Stochastic":
                        item.setBackground(Qt.cyan) # simplfication, custom widget better
                    table.setItem(r, c, item)
            
            # Action buttons
            act_w = QWidget()
            al = QHBoxLayout(act_w)
            al.setContentsMargins(0,0,0,0)
            b1 = QPushButton(create_icon("visibility", 18, "#cbd5e1").text()); b1.setFlat(True); b1.setStyleSheet("font-family: 'Material Symbols Outlined';")
            b2 = QPushButton(create_icon("download", 18, "#cbd5e1").text()); b2.setFlat(True); b2.setStyleSheet("font-family: 'Material Symbols Outlined';")
            al.addWidget(b1); al.addWidget(b2)
            table.setCellWidget(r, 5, act_w)

        lc_lay.addWidget(table)
        
        # Pagination
        pag = QHBoxLayout()
        pag.setContentsMargins(20, 10, 20, 20)
        pag.addWidget(QLabel("Showing 1-5 of 48 simulations"))
        pag.addStretch()
        p1 = QPushButton("Previous"); p1.setEnabled(False)
        p2 = QPushButton("Next")
        pag.addWidget(p1); pag.addWidget(p2)
        lc_lay.addLayout(pag)
        
        grid.addWidget(logs_card, 0, 0)
        
        # --- RIGHT: Virus Library ---
        lib_col = QVBoxLayout()
        
        # Header
        lib_h = QHBoxLayout()
        lib_h.addWidget(QLabel("Virus Library"))
        lib_h.addStretch()
        add = QPushButton("+ New Profile")
        add.setStyleSheet("background: #0d9488; color: white; border-radius: 8px; font-weight: bold; padding: 6px 12px;")
        lib_h.addWidget(add)
        lib_col.addLayout(lib_h)
        
        # Cards
        viruses = [
            ("Trojan.Win32.Test.v2", "USER-DEFINED", "Modified payload specifically designed to test firewall latency.", "1.2 (High)", "200ms", "#34d399"),
            ("Worm.Aggressive.B", "STANDARD LIBRARY", "Standard aggressive worm pattern for stress-testing mesh topologies.", "2.4 (Severe)", "50ms", "#94a3b8"),
            ("Custom_Ransom_01", "USER-DEFINED", "Simulates node locking behavior after T+1000s.", "0.5 (Low)", "500ms", "#f87171"),
        ]
        
        for name, tag, desc, prop, lat, color in viruses:
            vc = create_card()
            vl = QVBoxLayout(vc)
            
            vh = QHBoxLayout()
            vt = QLabel(name)
            vt.setStyleSheet("font-weight: bold;")
            icon = create_icon("bug_report" if "Worm" in name else "security", 20, color)
            vh.addWidget(vt)
            vh.addStretch()
            vh.addWidget(icon)
            vl.addLayout(vh)
            
            tag_lbl = QLabel("● " + tag)
            tag_lbl.setStyleSheet(f"font-size: 9px; font-weight: bold; color: {color};")
            vl.addWidget(tag_lbl)
            
            vl.addSpacing(5)
            d = QLabel(desc)
            d.setWordWrap(True)
            d.setStyleSheet("color: #64748b; font-size: 11px;")
            vl.addWidget(d)
            
            vl.addSpacing(10)
            stats = QGridLayout()
            stats.addWidget(QLabel("PROPAGATION"), 0, 0)
            stats.addWidget(QLabel(prop), 1, 0)
            stats.addWidget(QLabel("LATENCY"), 0, 1)
            stats.addWidget(QLabel(lat), 1, 1)
            vl.addLayout(stats)
            
            vl.addSpacing(10)
            acts = QHBoxLayout()
            acts.addWidget(QPushButton("✎ Edit"))
            acts.addWidget(QPushButton("Delete"))
            acts.addStretch()
            acts.addWidget(QPushButton("Details →"))
            vl.addLayout(acts)
            
            lib_col.addWidget(vc)
            
        lib_col.addStretch()
        
        grid.addLayout(lib_col, 0, 1)
        grid.setColumnStretch(0, 2) # Logs wider
        grid.setColumnStretch(1, 1) # Virus narrower
        
        self.content_layout.addLayout(grid)
        self.content_layout.addStretch()

    def _build_navbar(self):
        nav = QFrame()
        nav.setStyleSheet("background: white; border-bottom: 1px solid #e2e8f0;")
        nav.setFixedHeight(70)
        l = QHBoxLayout(nav)
        l.setContentsMargins(30, 0, 30, 0)
        
        logo = create_icon("hub", 24, "#0d9488")
        title = QLabel("Outbreak Sandbox")
        title.setStyleSheet("font-family: 'Space Grotesk'; font-weight: bold;")
        
        l.addWidget(logo)
        l.addWidget(title)
        l.addStretch()
        
        back = QPushButton("Dashboard")
        back.clicked.connect(lambda: self.back_requested.emit())
        l.addWidget(back)
        
        # Insert at the top of the main container layout
        # self.container_layout is defined in __init__
        if hasattr(self, 'container_layout'):
             self.container_layout.insertWidget(0, nav)
        else:
             # Fallback if called before init finishes (unlikely)
             pass


