from ui.utils.loader_thread import EngineLoaderThread
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from ui.screens.welcome_screen import WelcomeScreen
from ui.components.progress_dialog import ModernProgressDialog
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
            if key == 'home':
                 # Special handling for Home Screen multi-path navigation
                 widget.new_simulation_requested.connect(self.on_new_simulation)
                 widget.continue_simulation_requested.connect(self.on_continue_simulation)
                 widget.history_requested.connect(lambda: self.show_screen('history'))
            else:
                widget.next_requested.connect(lambda k=key: self.on_next(k))
                widget.back_requested.connect(lambda k=key: self.on_back(k))
                
            if hasattr(widget, 'dashboard_requested'):
                widget.dashboard_requested.connect(lambda: self.show_screen('home'))
            if hasattr(widget, 'history_requested') and key != 'home':
                widget.history_requested.connect(lambda: self.show_screen('history'))

        self.show_screen('welcome')

    def show_screen(self, key: str):
        if key == 'home':
            self.update_home_workflow_status()
            
        widget = self.screens.get(key)
        if widget:
            self.stack.setCurrentWidget(widget)

    def reset_configuration_screens(self):
        """Reset all configuration wizard screens to default state."""
        self.screens['topology'].reset()
        self.screens['virus'].reset()
        self.screens['config'].reset()

    def update_home_workflow_status(self):
        """Query wizard screens and update the home screen card."""
        topo_done = self.screens['topology'].is_complete()
        virus_done = self.screens['virus'].is_complete()
        config_done = self.screens['config'].is_complete()
        self.screens['home'].update_workflow_status(topo_done, virus_done, config_done)

    def on_next(self, current_key: str):
        # Case specific: New Simulation from Home should clear state logic?
        # SimulationHubCard emits "new_simulation_clicked" which connects to HomeScreen.next_requested
        # HomeScreen.next_requested just emits... wait.
        
        # We need to distinguish "New Simulation" from "Continue"
        
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

    def on_new_simulation(self):
        """Reset screens and start fresh."""
        self.reset_configuration_screens()
        self.show_screen('topology')

    def on_continue_simulation(self):
        """Resume where left off."""
        # Check Topology
        if not self.screens['topology'].is_complete():
            self.show_screen('topology')
            return
            
        # Check Virus
        if not self.screens['virus'].is_complete():
            self.show_screen('virus')
            return
            
        # Check Config (defaults to ready, but go there if all else ready)
        self.show_screen('config')

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

        # Show Loading
        self.progress_dlg = ModernProgressDialog("Configuring Simulation...", self)
        self.progress_dlg.setWindowModality(Qt.WindowModal)
        self.progress_dlg.show()

        # Run loading in thread to avoid UI freeze
        self.loader = EngineLoaderThread(topology_key, node_count, selected_virus_name, mode, seed_val)
        self.loader.finished_loading.connect(self.on_engine_loaded)
        self.loader.error_occurred.connect(self.on_engine_error)
        self.loader.start()

    def on_engine_loaded(self, engine):
        self.progress_dlg.close()
        self.screens['execute'].set_engine(engine)
        # SimulationExecution Dashboard is already next in stack logic if calling from on_next,
        # but if we are just calling initialize, we are good.
        # Wait, show_screen usually called after initialize by on_next logic. 
        # But since we made this async, we might be already on the screen but with empty data if we don't hold off.
        # Actually in on_next, we call initialize_simulation THEN show_screen.
        # Since initialize is now async, show_screen will happen immediately showing empty dashboard, then update.
        # That's acceptable, or we could handle it better. Given the current structure, let's let it load.

    def on_engine_error(self, err_msg):
        self.progress_dlg.close()
        print(f"Engine Init Error: {err_msg}")
        # Ideally show error message box here

