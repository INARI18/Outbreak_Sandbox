import os
import json
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QTableWidget, QHeaderView, QTableWidgetItem, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt, Signal
from ui.utils.base import create_pixmap
from ui.components.common.badge import Badge

class RecentActivityCard(QFrame):
    view_all_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet("""
            #card {
                background: white; 
                border-radius: 20px; 
                border: 1px solid #e2e8f0;
            }
        """)
        
        self.virus_type_map = self._load_virus_data()
        self.type_colors = {
            "ransomware": ("#ef4444", "#fef2f2"),
            "worm":       ("#f59e0b", "#fffbeb"),
            "botnet":     ("#6366f1", "#e0e7ff"),
            "trojan":     ("#8b5cf6", "#f3e8ff"),
            "spyware":    ("#ec4899", "#fce7f3"),
            "adware":     ("#10b981", "#d1fae5"),
        }

        
        # Shadow
        eff = QGraphicsDropShadowEffect(blurRadius=15, xOffset=0, yOffset=4, color=QColor(0,0,0,15))
        self.setGraphicsEffect(eff)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(0)
        
        # Header Row
        h_row = QHBoxLayout()
        rc_title = QLabel("Recent Activity")
        rc_title.setStyleSheet("font-weight: 800; font-size: 18px; color: #1e293b; border: none; background: transparent;")
        
        h_row.addWidget(rc_title)
        h_row.addStretch()
        self.layout.addLayout(h_row)
        self.layout.addSpacing(20)

        # Table Container
        self.table_container = QWidget()
        self.table_layout = QVBoxLayout(self.table_container)
        self.table_layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.table_container)
        
        self.setMinimumHeight(250)

    def _load_virus_data(self):
        """Loads virus map name->type"""
        mapping = {}
        try:
            path = os.path.join(os.getcwd(), 'config/viruses.json')
            if not os.path.exists(path):
                path = os.path.join(os.getcwd(), '..', 'config/viruses.json')
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for v in data.get('viruses', []):
                    mapping[v['name']] = v['type']
        except Exception:
            pass
        return mapping

    def update_data(self, activities):
        # Clear existing
        while self.table_layout.count():
            child = self.table_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not activities:
            self._render_placeholder()
        else:
            self._render_table(activities)

    def _render_placeholder(self):
        placeholder = QFrame()
        placeholder.setStyleSheet("background: #f8fafc; border-radius: 20px; border: 1px dashed #cbd5e1;")
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

    def _render_table(self, activities):
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["SIMULATION ID", "TOPOLOGY", "VIRUS", "INFECTION RATE"])
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.setShowGrid(False)
        table.setFrameShape(QFrame.NoFrame)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: white;
                color: #94a3b8;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #f1f5f9;
                padding: 12px;
                text-align: left;
            }
        """)
        table.setStyleSheet("""
            QTableWidget { border: none; background: white; gridline-color: transparent; }
            QTableWidget::item { padding: 12px 12px; border-bottom: 1px solid #f1f5f9; color: #475569; }
            QTableWidget::item:selected { background: transparent; color: inherit; }
        """)
        table.setFocusPolicy(Qt.NoFocus)

        table.setSelectionMode(QTableWidget.NoSelection)
        table.setAlternatingRowColors(True)
        table.setStyleSheet(table.styleSheet() + "QTableWidget { alternate-background-color: #f8fafc; }")
        
        table.setRowCount(len(activities))
        for row, item in enumerate(activities):
            self._add_table_row(table, row, item)
        
        self.table_layout.addWidget(table)

    def _add_table_row(self, table, row, item):
        id_item = QTableWidgetItem(item.get("id", "Unknown"))
        id_item.setToolTip(f"Run Date: {item.get('date')}")
        id_item.setForeground(Qt.black)
        id_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        f = QFont()
        f.setBold(True)
        id_item.setFont(f) 
        
        topo_item = QTableWidgetItem(item.get("topology", "—"))
        topo_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Virus Badge
        virus_name = item.get("virus", "—")
        virus_type = self.virus_type_map.get(virus_name, "unknown")
        color, bg = self.type_colors.get(virus_type, ("#64748b", "#f1f5f9"))
        
        badge_widget = QWidget()
        badge_widget.setStyleSheet("background: transparent;")
        bw_layout = QHBoxLayout(badge_widget)
        bw_layout.setContentsMargins(12, 0, 0, 0)
        bw_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        badge = Badge(text=virus_name, color=color, bg_color=bg)
        bw_layout.addWidget(badge)
        bw_layout.addStretch()
        
        rate_str = item.get("infection_rate", "0%")
        rate_item = QTableWidgetItem(rate_str)
        rate_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        try:
            val = float(rate_str.replace("%", ""))
            if val > 70:
                rate_item.setForeground(Qt.red)
            elif val > 30:
                rate_item.setForeground(Qt.darkYellow)
            else:
                rate_item.setForeground(Qt.darkGreen)
            
            font = QFont()
            font.setBold(True)
            rate_item.setFont(font)
        except:
            pass

        table.setItem(row, 0, id_item)
        table.setItem(row, 1, topo_item)
        table.setCellWidget(row, 2, badge_widget)
        table.setItem(row, 3, rate_item)
