from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Signal
from ui.screens.utils.base import NativeBase

from infra.repositories.stats_repository import StatsRepository
from infra.repositories.activity_repository import ActivityRepository

# Components
from ui.components.home.navbar import Navbar
from ui.components.home.welcome_hero import WelcomeHeader
from ui.components.home.simulation_hub_card import SimulationHubCard
from ui.components.home.system_readiness_card import SystemReadinessCard
from ui.components.home.recent_activity_card import RecentActivityCard
from ui.components.home.right_panel_widgets import SavedSimulationsWidget, VirusRepositoryWidget, DocumentationWidget

class HomeScreen(NativeBase):
    history_requested = Signal()

    def __init__(self):
        super().__init__()
        self.stats_repo = StatsRepository()
        self.repo = ActivityRepository()
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Navbar
        navbar = Navbar()
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
        header = WelcomeHeader()
        content_layout.addWidget(header)

        # Dashboard Grid
        grid = QGridLayout()
        grid.setSpacing(20)

        # Card 1: Simulation Hub
        hub_card = SimulationHubCard()
        hub_card.new_simulation_clicked.connect(lambda: self.next_requested.emit())
        grid.addWidget(hub_card, 0, 0, 1, 2)
        
        # Card 2: System Readiness
        readiness_card = SystemReadinessCard()
        readiness_card.continue_clicked.connect(lambda: self.next_requested.emit())
        grid.addWidget(readiness_card, 1, 0, 1, 2)

        # Card 3: Recent Activity
        self.recent_activity = RecentActivityCard()
        self.recent_activity.view_all_clicked.connect(lambda: self.history_requested.emit())
        grid.addWidget(self.recent_activity, 2, 0, 1, 2)

        # Card 4a: Saved Simulations
        sim_hist = SavedSimulationsWidget()
        sim_hist.clicked_signal.connect(lambda: self.history_requested.emit())
        grid.addWidget(sim_hist, 0, 2, 1, 1)

        # Card 4b: Saved Viruses
        virus_widget = VirusRepositoryWidget()
        grid.addWidget(virus_widget, 1, 2, 1, 1)

        # Card 5: Documentation
        doc_widget = DocumentationWidget()
        grid.addWidget(doc_widget, 2, 2, 1, 1)

        # Grid column stretch
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 3)
        grid.setColumnStretch(2, 2) 

        content_layout.addLayout(grid)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

        self.refresh_data()
    
    def refresh_data(self):
        activities = self.repo.load_activities()
        self.recent_activity.update_data(activities)
