from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from ui.screens.welcome_screen import WelcomeScreen
from ui.screens.home_screen import HomeScreen
from ui.screens.simulation_setup import (
    TopologySelectionScreen,
    SimulationConfigurationScreen,
    VirusSelectionScreen
)
from ui.screens.simulation_execution import SimulationExecutionDashboardScreen
from ui.screens.history_screen import SimulationHistoryProfilesScreen

# Simulation Logic
from infra.factories import SimulationFactory

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Outbreak Sandbox")
        self.resize(1100, 720)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.screens = {}
        self.screens['welcome'] = WelcomeScreen()
        self.screens['home'] = HomeScreen()
        self.screens['topology'] = TopologySelectionScreen()
        self.screens['config'] = SimulationConfigurationScreen()
        self.screens['virus'] = VirusSelectionScreen()
        self.screens['execute'] = SimulationExecutionDashboardScreen()
        self.screens['history'] = SimulationHistoryProfilesScreen()

        for key, widget in self.screens.items():
            self.stack.addWidget(widget)
            widget.next_requested.connect(lambda k=key: self.on_next(k))
            widget.back_requested.connect(lambda k=key: self.on_back(k))
            if hasattr(widget, 'dashboard_requested'):
                widget.dashboard_requested.connect(lambda: self.show_screen('home'))
            if hasattr(widget, 'history_requested'):
                widget.history_requested.connect(lambda: self.show_screen('history'))

        self.show_screen('welcome')

    def show_screen(self, key: str):
        widget = self.screens.get(key)
        if widget:
            self.stack.setCurrentWidget(widget)

    def on_next(self, current_key: str):
        order = ['welcome', 'home', 'topology', 'virus', 'config', 'execute', 'history']
        try:
            idx = order.index(current_key)
            next_key = order[min(idx + 1, len(order) - 1)]
            
            if next_key == 'execute':
                self.initialize_simulation()
            
            self.show_screen(next_key)
        except ValueError:
            self.show_screen('home')

    def on_back(self, current_key: str):
        order = ['welcome', 'home', 'topology', 'virus', 'config', 'execute', 'history']
        try:
            idx = order.index(current_key)
            prev_key = order[max(idx - 1, 0)]
            self.show_screen(prev_key)
        except ValueError:
            self.show_screen('welcome')

    def initialize_simulation(self):
        print("Initializing Simulation via Factory...")
        
        # 1. Gather Parameters from UI
        topo_screen = self.screens.get('topology')
        virus_screen = self.screens.get('virus')
        config_screen = self.screens.get('config')

        topology_key = getattr(topo_screen, 'get_selected_topology', lambda: 'random')()
        node_count = int(getattr(topo_screen, 'get_node_count', lambda: 30)())
        
        selected_virus_name = None
        if virus_screen and hasattr(virus_screen, 'get_selected_virus_name'):
            selected_virus_name = virus_screen.get_selected_virus_name()

        mode = getattr(config_screen, 'get_mode', lambda: 'stochastic')()
        seed_val = getattr(config_screen, 'get_seed', lambda: '12345')()

        # 2. Build Engine using Factory
        # encapsulates complexity of network creation, virus loading, and LLM setup
        engine = SimulationFactory.build_engine(
            topology_key=topology_key,
            node_count=node_count,
            virus_name=selected_virus_name,
            execution_mode=mode,
            seed=seed_val
        )
        
        self.screens['execute'].set_engine(engine)
