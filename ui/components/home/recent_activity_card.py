from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
    QTableWidget, QHeaderView, QTableWidgetItem, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt, Signal
from ui.screens.utils.base import create_pixmap

class RecentActivityCard(QFrame):
    view_all_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet("""
            #card {
                background: white; 
                border-radius: 12px; 
                border: 1px solid #e2e8f0;
            }
        """)
        
        # Shadow
        eff = QGraphicsDropShadowEffect(blurRadius=15, xOffset=0, yOffset=4, color=QColor(0,0,0,15))
        self.setGraphicsEffect(eff)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(0)
        
        # Header Row
        h_row = QHBoxLayout()
        rc_title = QLabel("Recent Activity")
        rc_title.setStyleSheet("font-weight: 800; font-size: 18px; color: #1e293b; border: none;")
        
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

    def _render_table(self, activities):
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
                text-align: center;
            }
        """)
        table.setStyleSheet("""
            QTableWidget { border: none; background: white; gridline-color: transparent; }
            QTableWidget::item { padding: 12px 5px; border-bottom: 1px solid #f1f5f9; color: #475569; }
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
        id_item.setTextAlignment(Qt.AlignCenter)
        f = QFont()
        f.setBold(True)
        id_item.setFont(f) 
        
        topo_item = QTableWidgetItem(item.get("topology", "—"))
        topo_item.setTextAlignment(Qt.AlignCenter)
        virus_item = QTableWidgetItem(item.get("virus", "—"))
        virus_item.setTextAlignment(Qt.AlignCenter)
        
        rate_str = item.get("infection_rate", "0%")
        rate_item = QTableWidgetItem(rate_str)
        rate_item.setTextAlignment(Qt.AlignCenter)
        
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
        table.setItem(row, 2, virus_item)
        table.setItem(row, 3, rate_item)
