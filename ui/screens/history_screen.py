from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, 
    QGridLayout, QWidget, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit
)
from ui.screens.utils.base import NativeBase, create_icon, create_card, create_qicon

class SimulationHistoryProfilesScreen(NativeBase):
    def __init__(self):
        super().__init__()
        
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
        self.container_layout.setSpacing(0)
        
        # Build Navbar first and add to container
        self._build_navbar()

        self.container_layout.addWidget(self.main)

        # Header
        h_box = QVBoxLayout()
        title = QLabel("Simulation History & Profiles")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #1e293b; letter-spacing: -0.5px;")
        
        sub = QLabel("Manage experiment logs, review analysis reports, and configure custom virus definitions.")
        sub.setStyleSheet("color: #64748b; font-size: 14px; margin-top: 4px;")
        
        h_box.addWidget(title)
        h_box.addWidget(sub)
        self.content_layout.addLayout(h_box)

        # Grid Content
        grid = QGridLayout()
        grid.setSpacing(30)
        
        # --- LEFT: Simulation Logs ---
        logs_card = create_card()
        logs_card.setStyleSheet("background: white; border-radius: 16px; border: 1px solid #e2e8f0;")
        
        lc_lay = QVBoxLayout(logs_card)
        lc_lay.setContentsMargins(0,0,0,0)
        
        # Logs Header
        lh = QHBoxLayout()
        lh.setContentsMargins(24, 24, 24, 16)
        
        lh_icon = QFrame()
        lh_icon.setFixedSize(36, 36)
        lh_icon.setStyleSheet("background: #f1f5f9; border-radius: 10px;")
        lil = QVBoxLayout(lh_icon); lil.setContentsMargins(0,0,0,0); lil.setAlignment(Qt.AlignCenter)
        lil.addWidget(create_icon("table_chart", 20, "#475569"))
        
        lh_title = QLabel("Simulation Logs")
        lh_title.setStyleSheet("font-weight: 800; font-size: 16px; color: #1e293b;")
        
        search = QLineEdit()
        search.setPlaceholderText("Search logs...")
        search.setFixedWidth(240)
        search.setStyleSheet("""
            QLineEdit {
                border-radius: 18px; 
                padding: 6px 16px; 
                border: 1px solid #e2e8f0; 
                background: #f8fafc;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #0d9488;
                background: white;
            }
        """)
        
        lh.addWidget(lh_icon)
        lh.addSpacing(12)
        lh.addWidget(lh_title)
        lh.addStretch()
        lh.addWidget(search)
        lc_lay.addLayout(lh)
        
        # Filters
        lf = QHBoxLayout()
        lf.setContentsMargins(24, 0, 24, 16)
        for f in ["ALL LOGS", "DETERMINISTIC", "STOCHASTIC", "LAST 24H"]:
            btn = QPushButton(f)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            if f == "ALL LOGS": 
                btn.setChecked(True)
                btn.setStyleSheet("""
                    QPushButton { background: #0f172a; color: white; border: none; border-radius: 8px; padding: 6px 12px; font-size: 11px; font-weight: bold; }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton { background: white; color: #64748b; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 12px; font-size: 11px; font-weight: bold; }
                    QPushButton:hover { background: #f8fafc; color: #334155; }
                    QPushButton:checked { background: #e2e8f0; color: #1e293b; }
                """)
            lf.addWidget(btn)
        lf.addStretch()
        lc_lay.addLayout(lf)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["ID", "DATE / TIME", "TOPOLOGY", "VIRUS", "MODE", "ACTION"])
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setFrameShape(QFrame.NoFrame)
        table.setFocusPolicy(Qt.NoFocus)
        table.setSelectionMode(QTableWidget.NoSelection)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 12px 24px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-weight: bold;
                font-size: 11px;
                color: #64748b;
                text-align: left;
            }
        """)
        
        table.setStyleSheet("""
            QTableWidget {
                background: white; border: none;
            }
            QTableWidget::item { 
                padding: 12px 24px; 
                border-bottom: 1px solid #f1f5f9; 
                color: #334155; 
                font-size: 13px;
            } 
        """)
        
        rows = [
            ("#SIM-849", "Oct 24, 14:00", "Mesh Network (n=50)", "Polymorphic-Worm-A", "Stochastic"),
            ("#SIM-848", "Oct 24, 09:30", "Star Topology (n=20)", "Trojan.Win32.Test", "Deterministic"),
            ("#SIM-847", "Oct 23, 18:15", "Scale-Free (n=100)", "Ransomware-X", "Stochastic"),
            ("#SIM-846", "Oct 22, 11:45", "Mesh Network (n=50)", "Botnet-Seed-Alpha", "Deterministic"),
            ("#SIM-845", "Oct 21, 14:20", "Ring Topology (n=25)", "Worm.Gen.V4", "Stochastic"),
        ]
        
        table.setRowCount(len(rows))
        for r, row_data in enumerate(rows):
            for c, txt in enumerate(row_data):
                if c == 0: # ID
                    lbl = QLabel(txt)
                    lbl.setStyleSheet("font-family: 'Monaco', monospace; font-weight: bold; color: #0d9488;")
                    table.setCellWidget(r, c, lbl)
                elif c == 4:
                    w = QWidget()
                    wl = QHBoxLayout(w); wl.setContentsMargins(0,0,0,0); wl.setAlignment(Qt.AlignLeft)
                    lbl = QLabel(txt)
                    if txt == "Stochastic":
                        lbl.setStyleSheet("background: #f0f9ff; color: #0369a1; font-size: 11px; padding: 4px 8px; border-radius: 6px; font-weight: bold;")
                    else:
                        lbl.setStyleSheet("background: #fdf2f8; color: #be185d; font-size: 11px; padding: 4px 8px; border-radius: 6px; font-weight: bold;")
                    wl.addWidget(lbl)
                    table.setCellWidget(r, c, w)
                else:
                    table.setItem(r, c, QTableWidgetItem(txt))
            
            # Action buttons
            act_w = QWidget()
            al = QHBoxLayout(act_w)
            al.setContentsMargins(0,0,0,0)
            al.setSpacing(4)
            
            b1 = QPushButton()
            b1.setIcon(create_qicon("visibility", 18, "#64748b"))
            b1.setFlat(True)
            b1.setCursor(Qt.PointingHandCursor)
            
            b2 = QPushButton()
            b2.setIcon(create_qicon("download", 18, "#64748b"))
            b2.setFlat(True)
            b2.setCursor(Qt.PointingHandCursor)
            
            al.addWidget(b1); al.addWidget(b2)
            table.setCellWidget(r, 5, act_w)

        lc_lay.addWidget(table)
        
        # Pagination
        pag = QHBoxLayout()
        pag.setContentsMargins(24, 16, 24, 24)
        pag.addWidget(QLabel("Showing 1-5 of 48 simulations"))
        pag.addStretch()
        
        p1 = QPushButton("Previous")
        p1.setEnabled(False)
        p1.setStyleSheet("background: white; border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px 12px; color: #94a3b8;")
        
        p2 = QPushButton("Next")
        p2.setStyleSheet("background: white; border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px 12px; color: #1e293b;")
        
        pag.addWidget(p1); pag.addWidget(p2)
        lc_lay.addLayout(pag)
        
        grid.addWidget(logs_card, 0, 0)
        
        # --- RIGHT: Virus Library ---
        lib_col = QVBoxLayout()
        
        # Header
        lib_h = QHBoxLayout()
        t = QLabel("Virus Library")
        t.setStyleSheet("font-size: 18px; font-weight: 800; color: #1e293b;")
        lib_h.addWidget(t)
        lib_h.addStretch()
        
        add = QPushButton(" + New ")
        add.setCursor(Qt.PointingHandCursor)
        add.setStyleSheet("""
            QPushButton {
                background: #0f172a; color: white; border-radius: 8px; font-weight: bold; padding: 6px 12px; font-size: 12px;
            }
            QPushButton:hover {
                background: #1e293b;
            }
        """)
        lib_h.addWidget(add)
        lib_col.addLayout(lib_h)
        lib_col.addSpacing(16)
        
        # Cards
        viruses = [
            ("Trojan.Win32.Test.v2", "USER-DEFINED", "Modified payload specifically designed to test firewall latency.", "1.2 (High)", "200ms", "#10b981"),
            ("Worm.Aggressive.B", "STANDARD LIBRARY", "Standard aggressive worm pattern for stress-testing mesh topologies.", "2.4 (Severe)", "50ms", "#6366f1"),
            ("Custom_Ransom_01", "USER-DEFINED", "Simulates node locking behavior after T+1000s.", "0.5 (Low)", "500ms", "#f43f5e"),
        ]
        
        for name, tag, desc, prop, lat, color in viruses:
            vc = create_card()
            vc.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #e2e8f0;")
            
            vl = QVBoxLayout(vc)
            vl.setContentsMargins(20, 20, 20, 20)
            
            vh = QHBoxLayout()
            
            # Colored Indicator
            ind = QFrame()
            ind.setFixedSize(12, 12)
            ind.setStyleSheet(f"background: {color}; border-radius: 6px;")
            
            vt = QLabel(name)
            vt.setStyleSheet("font-weight: 800; font-size: 14px; color: #1e293b;")
            
            vh.addWidget(ind)
            vh.addSpacing(8)
            vh.addWidget(vt)
            vh.addStretch()
            
            # Small pill tag
            tag_pill = QLabel(tag.replace("-", " "))
            tag_pill.setStyleSheet("font-size: 9px; font-weight: bold; color: #64748b; background: #f1f5f9; padding: 4px 6px; border-radius: 4px;")
            vh.addWidget(tag_pill)
            
            vl.addLayout(vh)
            
            vl.addSpacing(12)
            d = QLabel(desc)
            d.setWordWrap(True)
            d.setStyleSheet("color: #64748b; font-size: 12px; line-height: 1.4;")
            vl.addWidget(d)
            
            vl.addSpacing(16)
            
            # Stats row
            stats = QHBoxLayout()
            
            def make_stat(lbl, val):
                c = QVBoxLayout()
                c.setSpacing(2)
                l = QLabel(lbl)
                l.setStyleSheet("font-size: 10px; font-weight: bold; color: #94a3b8; text-transform: uppercase;")
                v = QLabel(val)
                v.setStyleSheet("font-size: 12px; font-weight: bold; color: #334155;")
                c.addWidget(l); c.addWidget(v)
                return c
                
            stats.addLayout(make_stat("R0 / Spread", prop))
            stats.addSpacing(20)
            stats.addLayout(make_stat("Latency", lat))
            stats.addStretch()
            
            vl.addLayout(stats)
            lib_col.addWidget(vc)
            lib_col.addSpacing(12)
            
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
        
        logo = create_icon("hub", 26, "#0d9488")
        title = QLabel("Outbreak Sandbox")
        title.setStyleSheet("font-family: 'Space Grotesk'; font-weight: bold; font-size: 16px;")
        
        l.addWidget(logo)
        l.addWidget(title)
        l.addStretch()
        
        back = QPushButton(" Dashboard")
        back.setIcon(create_qicon("arrow_back", 18, "#334155"))
        back.setCursor(Qt.PointingHandCursor)
        back.setStyleSheet("""
            QPushButton {
                background: transparent; color: #334155; font-weight: bold; font-size: 13px; border: 1px solid #cbd5e1; border-radius: 8px; padding: 6px 12px;
            }
            QPushButton:hover {
                background: #f1f5f9; border-color: #94a3b8;
            }
        """)
        back.clicked.connect(lambda: self.back_requested.emit())
        l.addWidget(back)
        
        if hasattr(self, 'container_layout'):
            self.container_layout.insertWidget(0, nav)


