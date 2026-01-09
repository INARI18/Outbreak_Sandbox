from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QPainterPath
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, 
    QGridLayout, QWidget, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QButtonGroup, QStackedWidget, QGraphicsDropShadowEffect
)
from ui.utils.base import NativeBase, create_icon, create_card, create_qicon
from ui.components.common.header import StandardHeader
import math

# TODO: implement actual charting
class MockChartWidget(QFrame):
    def __init__(self, title, color="#0d9488", mode="line"):
        super().__init__()
        self.title = title
        self.base_color = QColor(color)
        self.mode = mode
        self.setStyleSheet("background: #f8fafc; border-radius: 12px; border: 1px solid #e2e8f0;")
        self.setMinimumHeight(180)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw Title
        painter.setPen(QColor("#475569"))
        font = painter.font()
        font.setFamily("Space Grotesk")
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(20, 30, self.title)
        
        # Draw Chart Area
        rect_x, rect_y, rect_w, rect_h = 20, 50, self.width() - 40, self.height() - 70
        
        # Axes
        painter.setPen(QPen(QColor("#cbd5e1"), 1))
        painter.drawLine(rect_x, rect_y + rect_h, rect_x + rect_w, rect_y + rect_h) # X axis
        painter.drawLine(rect_x, rect_y, rect_x, rect_y + rect_h) # Y axis
        
        if self.mode == "line":
            self._draw_line_chart(painter, rect_x, rect_y, rect_w, rect_h)
        else:
            self._draw_bar_chart(painter, rect_x, rect_y, rect_w, rect_h)

    def _draw_line_chart(self, painter, x, y, w, h):
        path = QPainterPath()
        path.moveTo(x, y + h)
        
        step = w / 20
        for i in range(21):
            px = x + (i * step)
            # Create a nice curve
            val = math.sin(i * 0.5) * 0.5 + 0.5 # 0 to 1
            # Add some randomness based on position to make it look like data
            val = (val + math.sin(i * 2.3) * 0.2) 
            val = max(0.1, min(0.9, val))
            
            py = y + h - (val * h)
            path.lineTo(px, py)
            
        painter.setPen(QPen(self.base_color, 2))
        painter.drawPath(path)
        
        # Fill
        path.lineTo(x + w, y + h)
        path.lineTo(x, y + h)
        c = QColor(self.base_color)
        c.setAlpha(40)
        painter.fillPath(path, c)

    def _draw_bar_chart(self, painter, x, y, w, h):
        count = 8
        bar_w = (w / count) * 0.6
        gap = (w / count) * 0.4
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.base_color)
        
        for i in range(count):
            bx = x + (i * (bar_w + gap)) + gap/2
            # varied heights
            val = (math.sin(i * 123.45) + 1) / 2 # 0-1 pseudo random
            val = 0.2 + (val * 0.7)
            bh = val * h
            by = y + h - bh
            
            painter.drawRoundedRect(bx, by, bar_w, bh, 4, 4)

class SimulationHistoryProfilesScreen(NativeBase):
    def __init__(self):
        super().__init__()
        
        # Container
        self.container_layout = QVBoxLayout(self)
        self.container_layout.setContentsMargins(0,0,0,0)
        self.container_layout.setSpacing(0)
        
        # Header
        self.header = StandardHeader(
            title="Saved Simulations",
            subtitle="Review logs, analyze metrics, and manage your simulation history.",
            show_dashboard_btn=True
        )
        self.header.dashboard_requested.connect(self.dashboard_requested.emit)
        self.container_layout.addWidget(self.header)
        
        # Main Layout
        self.main = QScrollArea()
        self.main.setWidgetResizable(True)
        self.main.setFrameShape(QFrame.NoFrame)
        self.main.setStyleSheet("background: #f8fafc;") # Global bg
        
        self.content = QWidget()
        self.content_layout = QHBoxLayout(self.content)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(30)
        self.main.setWidget(self.content)

        self.container_layout.addWidget(self.main)

        # LEFT COLUMN (Table)
        self._build_table_panel()
        
        # RIGHT COLUMN (Stats)
        self._build_stats_panel()

        # Connect signals
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

    def _build_table_panel(self):
        left_panel = QVBoxLayout()
        left_panel.setSpacing(20)
        
        # 1. Filters & Search
        top_bar = QHBoxLayout()
        
        # Exclusive Filter Buttons
        self.filter_group = QButtonGroup(self)
        self.filter_group.setExclusive(True)
        
        filters = ["All Logs", "Deterministic", "Stochastic", "Last 24h"]
        
        filter_container = QHBoxLayout()
        filter_container.setSpacing(8)
        
        for i, f in enumerate(filters):
            btn = QPushButton(f)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(36)
            # Default style
            btn.setStyleSheet("""
                QPushButton {
                    background: white; border: 1px solid #e2e8f0; border-radius: 18px; 
                    padding: 0 20px; color: #64748b; font-weight: 600; font-size: 13px;
                }
                QPushButton:hover { border-color: #cbd5e1; color: #475569; }
                QPushButton:checked {
                    background: #0f172a; border: 1px solid #0f172a; color: white;
                }
            """)
            if i == 0: btn.setChecked(True)
            self.filter_group.addButton(btn)
            filter_container.addWidget(btn)
            
        filter_container.addStretch()
        top_bar.addLayout(filter_container)
        
        # Search
        search = QLineEdit()
        search.setPlaceholderText("Search by ID or Topology...")
        search.setFixedWidth(240)
        search.setFixedHeight(36)
        search.setStyleSheet("""
            QLineEdit {
                border-radius: 18px; 
                padding: 0 16px; 
                border: 1px solid #e2e8f0; 
                background: white;
                font-size: 13px;
                color: #334155;
            }
            QLineEdit:focus {
                border: 1px solid #0d9488;
            }
        """)
        top_bar.addWidget(search)
        
        left_panel.addLayout(top_bar)
        
        # 2. Table Card
        table_card = create_card()
        # Ensure it has a white bg and shadow
        eff = QGraphicsDropShadowEffect(blurRadius=15, xOffset=0, yOffset=4, color=QColor(0,0,0,10))
        table_card.setGraphicsEffect(eff)
        
        tc_layout = QVBoxLayout(table_card)
        tc_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["SIMULATION ID", "DATE", "TOPOLOGY", "STATUS"])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.NoFrame)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Header Style
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setFixedHeight(45)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #f8fafc;
                color: #64748b;
                font-weight: bold;
                font-size: 11px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                padding-left: 16px;
                text-align: left;
            }
        """)
        
        # Table Body Style
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border-radius: 12px;
                selection-background-color: #f0fdf4;
                selection-color: #1e293b;
            }
            QTableWidget::item {
                border-bottom: 1px solid #f1f5f9;
                padding-left: 16px;
                color: #334155;
            }
        """)
        
        # Connect selection
        # Moved to __init__ to ensure stats_stack is ready
        # self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Populate Mock Data
        self._populate_mock_data()
        
        tc_layout.addWidget(self.table)
        
        # Pagination
        pag_layout = QHBoxLayout()
        pag_layout.setContentsMargins(20, 15, 20, 15)
        pag_lbl = QLabel("Showing 5 of 12 simulations")
        pag_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 500;")
        pag_layout.addWidget(pag_lbl)
        pag_layout.addStretch()
        
        for lbl in ["Previous", "Next"]:
            b = QPushButton(lbl)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet("QPushButton { border: 1px solid #e2e8f0; border-radius: 6px; padding: 4px 12px; color: #475569; background: white; } QPushButton:hover { background: #f8fafc; }")
            pag_layout.addWidget(b)
            
        tc_layout.addLayout(pag_layout)
        
        left_panel.addWidget(table_card)
        
        # Add to main
        self.content_layout.addLayout(left_panel, 2)

    def _build_stats_panel(self):
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        title = QLabel("Analytics Preview")
        title.setObjectName("h3")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #1e293b;")
        right_panel.addWidget(title)
        
        # Stacked Widget to show Placeholder OR Charts
        self.stats_stack = QStackedWidget()
        
        # Page 0: Placeholder
        page_placeholder = create_card()
        page_placeholder.setStyleSheet("background: white; border-radius: 12px; border: 1px dashed #cbd5e1;")
        pp_layout = QVBoxLayout(page_placeholder)
        pp_layout.setAlignment(Qt.AlignCenter)
        pp_layout.setSpacing(10)
        
        icon = create_icon("analytics", 48, "#cbd5e1")
        lbl = QLabel("Select a simulation")
        lbl.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 16px;")
        sub = QLabel("Click on a row in the table\nto view detailed statistics.")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        
        pp_layout.addStretch()
        pp_layout.addWidget(icon)
        pp_layout.addWidget(lbl)
        pp_layout.addWidget(sub)
        pp_layout.addStretch()
        
        self.stats_stack.addWidget(page_placeholder)
        
        # Page 1: Charts Container
        page_charts = QWidget()
        pc_layout = QVBoxLayout(page_charts)
        pc_layout.setContentsMargins(0,0,0,0)
        pc_layout.setSpacing(20)
        
        # Chart 1: Infection Curve
        self.chart1 = MockChartWidget("Infection Spread (Active Nodes)", "#0d9488", "line")
        pc_layout.addWidget(self.chart1)
        
        # Chart 2: Latency/Load
        self.chart2 = MockChartWidget("Network Load Distribution", "#6366f1", "bar")
        pc_layout.addWidget(self.chart2)
        
        pc_layout.addStretch()
        
        self.stats_stack.addWidget(page_charts)
        
        right_panel.addWidget(self.stats_stack)
        
        self.content_layout.addLayout(right_panel, 1)

    def _populate_mock_data(self):
        data = [
            ("SIM-902", "Jan 08, 14:20", "Mesh (n=50)", "Completed"),
            ("SIM-901", "Jan 08, 11:05", "Star (n=20)", "Completed"),
            ("SIM-899", "Jan 07, 16:45", "Scale-Free (n=100)", "Failed"),
            ("SIM-895", "Jan 06, 09:30", "Grid (n=64)", "Completed"),
            ("SIM-882", "Jan 05, 13:15", "Ring (n=30)", "Completed"),
        ]
        
        self.table.setRowCount(len(data))
        for r, (sid, date, topo, status) in enumerate(data):
            self.table.setItem(r, 0, QTableWidgetItem(sid))
            self.table.setItem(r, 1, QTableWidgetItem(date))
            self.table.setItem(r, 2, QTableWidgetItem(topo))
            
            # Status badge-like text
            s_item = QTableWidgetItem(status)
            if status == "Completed":
                s_item.setForeground(QColor("#059669"))
            else:
                s_item.setForeground(QColor("#ef4444"))
            s_item.setFont(QFont("Space Grotesk", 10, QFont.Bold))
            self.table.setItem(r, 3, s_item)
            
    def _on_selection_changed(self):
        # If selection exists, show stats
        indexes = self.table.selectedIndexes()
        if indexes:
            self.stats_stack.setCurrentIndex(1)
        else:
            self.stats_stack.setCurrentIndex(0)
