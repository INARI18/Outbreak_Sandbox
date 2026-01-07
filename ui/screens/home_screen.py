from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, 
    QGridLayout, QWidget, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView
)
from ui.screens.utils.base import NativeBase, create_icon, create_card, create_qicon, create_pixmap
from ui.components import PrimaryButton

from infra.repositories.stats_repository import StatsRepository
from infra.repositories.activity_repository import ActivityRepository

class HomeScreen(NativeBase):
    def __init__(self):
        super().__init__()
        self.stats_repo = StatsRepository()
        self.repo = ActivityRepository()
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Navbar / Top Bar
        navbar = QFrame()
        navbar.setStyleSheet("background: white; border-bottom: 1px solid #e2e8f0;")
        navbar.setFixedHeight(70)
        nav_layout = QHBoxLayout(navbar)
        nav_layout.setContentsMargins(30, 0, 30, 0)
        
        # Logo Area
        brand_layout = QHBoxLayout()
        logo = create_icon("bug_report", 28, "#0d9488")
        brand_text = QLabel("Outbreak Sandbox")
        brand_text.setStyleSheet("font-family: 'Space Grotesk'; font-weight: bold; font-size: 16px;")
        brand_layout.addWidget(logo)
        brand_layout.addWidget(brand_text)
        
        # Right Side (User Profile)
        user_layout = QHBoxLayout()
        status_pill = QLabel("● Server Online")
        status_pill.setStyleSheet("color: #10b981; font-size: 11px; background: #f0fdf4; padding: 6px 12px; border-radius: 12px; border: 1px solid #bbf7d0;")
        
        settings_btn = QPushButton()
        settings_btn.setIcon(create_qicon("settings", 20, "#64748b"))
        settings_btn.setFixedSize(40, 40)
        settings_btn.setStyleSheet("border: none; background: transparent;")
        
        user_info = QLabel("Dr. A. Turing<br><span style='color:#94a3b8; font-size:11px'>Level 4 Researcher</span>")
        user_info.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        avatar = create_icon("account_circle", 36, "#cbd5e1")
        
        user_layout.addWidget(status_pill)
        user_layout.addSpacing(15)
        user_layout.addWidget(settings_btn)
        user_layout.addSpacing(15)
        user_layout.addWidget(user_info)
        user_layout.addWidget(avatar)

        nav_layout.addLayout(brand_layout)
        nav_layout.addStretch()
        nav_layout.addLayout(user_layout)
        
        layout.addWidget(navbar)

        # 2. Content Area (Scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #f8fafc;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)

        # Header Section
        header_text = QLabel("Welcome to Outbreak Sandbox")
        header_text.setObjectName("h2")
        sub_text = QLabel("Configure, simulate, and analyze malware propagation in safe, controlled network environments.")
        sub_text.setStyleSheet("color: #64748b; font-size: 14px;")
        
        content_layout.addWidget(header_text)
        content_layout.addWidget(sub_text)

        # Dashboard Grid
        grid = QGridLayout()
        grid.setSpacing(20)

        # --- LEFT COLUMN ---
        
        # Card 1: Simulation Hub (Main Action)
        hub_card = create_card()
        hub_layout = QVBoxLayout(hub_card)
        hub_layout.setContentsMargins(30, 30, 30, 30)
        
        hub_title = QLabel("Simulation Hub")
        hub_title.setObjectName("h3")
        
        # Banner inside card
        banner_layout = QHBoxLayout()
        start_btn = PrimaryButton("New Simulation", "add_circle", 50)
        start_btn.setFixedWidth(220)
        start_btn.clicked.connect(lambda: self.next_requested.emit())
        
        recom_pill = QLabel("RECOMMENDED ACTION")
        recom_pill.setStyleSheet("background: #e0f2fe; color: #0369a1; font-weight: bold; font-size: 10px; padding: 6px 10px; border-radius: 6px;")
        
        banner_layout.addWidget(start_btn)
        banner_layout.addStretch()
        banner_layout.addWidget(recom_pill)
        
        hub_layout.addWidget(hub_title)
        hub_layout.addSpacing(10)
        hub_layout.addLayout(banner_layout)
        
        grid.addWidget(hub_card, 0, 0, 1, 2) # Span 2 cols
        
        # Card 2: Configuration Progress (Workflow viz)
        workflow_card = create_card()
        wf_layout = QVBoxLayout(workflow_card)
        wf_title = QHBoxLayout()
        wf_title.addWidget(QLabel("Configuration Workflow"))
        info_icon = create_icon("info", 16, "#94a3b8")
        wf_title.addStretch()
        wf_title.addWidget(info_icon)
        
        # Steps
        steps_layout = QHBoxLayout()
        steps = [
            ("Network Topology", "Define node structures", "hub"),
            ("Virus Selection", "Choose payload types", "bug_report"),
            ("Global Config", "Set time dilation", "tune")
        ]
        
        for title, desc, icon_name in steps:
            step_frame = QFrame()
            step_frame.setStyleSheet("background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;")
            sf_layout = QVBoxLayout(step_frame)
            
            icon = create_icon(icon_name, 24, "#0d9488")
            t = QLabel(title)
            t.setStyleSheet("font-weight: bold; color: #0f172a;")
            d = QLabel(desc)
            d.setStyleSheet("font-size: 11px; color: #64748b;")
            d.setWordWrap(True)
            
            sf_layout.addWidget(icon)
            sf_layout.addWidget(t)
            sf_layout.addWidget(d)
            steps_layout.addWidget(step_frame)
            
        wf_layout.addLayout(wf_title)
        wf_layout.addSpacing(15)
        wf_layout.addLayout(steps_layout)
        
        grid.addWidget(workflow_card, 1, 0, 1, 2)

        # Card 3: Recent Activity Table
        recent_card = create_card()
        self.rc_layout = QVBoxLayout(recent_card)
        self.rc_layout.setSpacing(0)
        
        rc_header = QHBoxLayout()
        rc_header.addWidget(QLabel("Recent Activity"))
        view_all = QPushButton("View All History →")
        view_all.setStyleSheet("border: none; color: #0d9488; font-weight: bold; text-align: right;")
        view_all.setCursor(Qt.PointingHandCursor)
        rc_header.addStretch()
        rc_header.addWidget(view_all)
        # rc_header.setContentsMargins(0,0,0,10)
        
        self.rc_layout.addLayout(rc_header)
        # self.rc_layout.addSpacing(10)
        
        self.table_container = QWidget()
        self.table_layout = QVBoxLayout(self.table_container)
        self.table_layout.setContentsMargins(0,0,0,0)
        self.rc_layout.addWidget(self.table_container)
        
        # We will build the table or placeholder in update_recent_activity
        recent_card.setMinimumHeight(250)
        
        grid.addWidget(recent_card, 2, 0, 1, 2)

        self.update_recent_activity()
        
        # --- RIGHT COLUMN ---
        
        # Card 4: Data Management
        data_card = create_card()
        data_layout = QVBoxLayout(data_card)
        data_layout.addWidget(QLabel("Data Management"))
        data_layout.addSpacing(10)
        
        opts = [
            ("Simulation History", "Review 12 past logs", "history"),
            ("Saved States", "3 snapshots available", "save"),
            ("User Virus Profiles", "Manage custom payloads", "science")
        ]
        
        for title, subtitle, icon_name in opts:
            btn = QPushButton()
            btn.setStyleSheet("""
                QPushButton { text-align: left; padding: 15px; background: #f8fafc; border: none; border-radius: 8px; }
                QPushButton:hover { background: #f1f5f9; }
            """)
            slug = QHBoxLayout(btn)
            ico = create_icon(icon_name, 20, "#10b981")
            
            v = QVBoxLayout()
            t = QLabel(title)
            t.setStyleSheet("font-weight: bold;")
            s = QLabel(subtitle)
            s.setStyleSheet("color: #64748b; font-size: 11px;")
            v.addWidget(t)
            v.addWidget(s)
            
            slug.addWidget(ico)
            slug.addLayout(v)
            slug.addStretch()
            slug.addWidget(QLabel("›"))
            
            data_layout.addWidget(btn)
            data_layout.addSpacing(5)
            
        grid.addWidget(data_card, 0, 2, 2, 1) # Right side, span 2 rows vertically
        
        # Card 5: Documentation (Dark)
        doc_card = QFrame()
        doc_card.setStyleSheet("background: #1e293b; border-radius: 16px; color: white;")
        doc_layout = QVBoxLayout(doc_card)
        doc_layout.setContentsMargins(25, 25, 25, 25)
        
        doc_title = QLabel("Documentation")
        doc_title.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        doc_desc = QLabel("Access the full technical manual, API references, and community guides on GitHub.")
        doc_desc.setWordWrap(True)
        doc_desc.setStyleSheet("color: #94a3b8; margin-top: 10px; margin-bottom: 20px;")
        
        gh_btn = QPushButton("  View on GitHub")
        gh_btn.setIcon(create_qicon("code", 16, "#0f172a"))
        gh_btn.setStyleSheet("background: white; color: #0f172a; border: none;")
        
        doc_layout.addWidget(doc_title)
        doc_layout.addWidget(doc_desc)
        doc_layout.addWidget(gh_btn)
        
        grid.addWidget(doc_card, 2, 2, 1, 1) # Bottom right
        
        # Grid column stretch
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 3)
        grid.setColumnStretch(2, 2) # Right col smaller

        content_layout.addLayout(grid)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def update_recent_activity(self):
        # Clear existing content
        while self.table_layout.count():
            child = self.table_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        activities = self.repo.load_activities()

        if not activities:
            # Placeholder State
            placeholder = QFrame()
            placeholder.setStyleSheet("background: #f8fafc; border-radius: 8px; border: 1px dashed #cbd5e1;")
            pl = QVBoxLayout(placeholder)
            pl.setAlignment(Qt.AlignCenter)
            pl.setSpacing(10)
            
            icon = QLabel()
            icon.setPixmap(create_pixmap("history", 32, "#94a3b8"))
            icon.setAlignment(Qt.AlignCenter)
            
            txt = QLabel("No recent activity recorded")
            txt.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 14px;")
            txt.setAlignment(Qt.AlignCenter)
            
            sub = QLabel("Run your first simulation to see logs here.")
            sub.setStyleSheet("color: #cbd5e1; font-size: 12px;")
            sub.setAlignment(Qt.AlignCenter)
            
            pl.addStretch()
            pl.addWidget(icon)
            pl.addWidget(txt)
            pl.addWidget(sub)
            pl.addStretch()
            
            self.table_layout.addWidget(placeholder)
        else:
            # Table State
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["SIMULATION ID", "TOPOLOGY", "VIRUS", "INFECTION RATE"])
            table.verticalHeader().setVisible(False)
            table.setShowGrid(False)
            table.setFrameShape(QFrame.NoFrame)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: white;
                    color: #94a3b8;
                    font-weight: bold;
                    border: none;
                    border-bottom: 2px solid #f1f5f9;
                    padding: 8px;
                    text-align: left;
                }
            """)
            table.setStyleSheet("""
                QTableWidget { border: none; background: white; }
                QTableWidget::item { padding: 12px 5px; border-bottom: 1px solid #f8fafc; color: #334155; }
                QTableWidget::item:selected { background: #f0fdf4; color: #0d9488; }
            """)
            table.setFocusPolicy(Qt.NoFocus)
            table.setSelectionMode(QTableWidget.NoSelection) # Or SingleSelection
            
            table.setRowCount(len(activities))
            for row, item in enumerate(activities):
                # ID with Date tooltip
                id_item = QTableWidgetItem(item.get("id", "Unknown"))
                id_item.setToolTip(f"Run Date: {item.get('date')}")
                # Optional: Make ID look like a link or code
                id_item.setForeground(Qt.black)
                f = QFont()
                f.setBold(True)
                id_item.setFont(f) 
                
                topo_item = QTableWidgetItem(item.get("topology", "—"))
                virus_item = QTableWidgetItem(item.get("virus", "—"))
                
                rate_str = item.get("infection_rate", "0%")
                rate_item = QTableWidgetItem(rate_str)
                # Colorize high infection rates?
                try:
                    val = float(rate_str.replace("%", ""))
                    if val > 70:
                        rate_item.setForeground(Qt.red)
                    elif val > 30:
                        rate_item.setForeground(Qt.darkYellow)
                    else:
                        rate_item.setForeground(Qt.darkGreen)
                except:
                    pass

                table.setItem(row, 0, id_item)
                table.setItem(row, 1, topo_item)
                table.setItem(row, 2, virus_item)
                table.setItem(row, 3, rate_item)
            
            self.table_layout.addWidget(table)


