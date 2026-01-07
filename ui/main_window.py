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
from models.network import Network
from infra.topologies import create_topology
from infra.network_factory import graph_to_network
from simulation.engine import SimulationEngine
from simulation.deterministic_policy import DeterministicPolicy
from infra.repositories.virus_repository import VirusRepository
from infra.llm.groq_client import GroqClient
from infra.llm.mock_client import MockClient
from llm.interface import LLMInterface
import os

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

        # create screens
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
            # connect navigation
            widget.next_requested.connect(lambda k=key: self.on_next(k))
            widget.back_requested.connect(lambda k=key: self.on_back(k))
            if hasattr(widget, 'dashboard_requested'):
                widget.dashboard_requested.connect(lambda: self.show_screen('home'))

        # start on welcome
        self.show_screen('welcome')

    def show_screen(self, key: str):
        widget = self.screens.get(key)
        if widget:
            self.stack.setCurrentWidget(widget)

    def on_next(self, current_key: str):
        # Correct Order: Topology -> Virus -> Config -> Execute
        order = ['welcome', 'home', 'topology', 'virus', 'config', 'execute', 'history']
        try:
            idx = order.index(current_key)
            next_key = order[min(idx + 1, len(order) - 1)]
            
            # Hook: If entering execution, initialize engine
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
        print("Initializing Simulation...")
        # 1. Topology (read selection from Topology screen)
        topo_screen = self.screens.get('topology')
        topology_key = getattr(topo_screen, 'get_selected_topology', lambda: 'random')()
        node_count = getattr(topo_screen, 'get_node_count', lambda: 30)()
        # Using the user selected settings
        try:
            G = create_topology(topology_key, int(node_count))
        except KeyError:
            print(f"Unknown topology '{topology_key}', falling back to 'random'.")
            G = create_topology('random', int(node_count))

        network = graph_to_network(G)
        
        # 2. Virus
        # Ensure we are looking in the project root
        project_root = os.getcwd() # Assumption: running from root
        virus_path = os.path.join(project_root, "viruses.json")
        
        try:
            repo = VirusRepository(virus_path)
            viruses = repo.load_all()
            # Check user selection
            v_screen = self.screens.get('virus')
            selected_name = None
            if v_screen and hasattr(v_screen, 'get_selected_virus_name'):
                selected_name = v_screen.get_selected_virus_name()

            virus = None
            if selected_name and viruses:
                for v in viruses:
                    if v.name == selected_name:
                        virus = v
                        break
            if not virus:
                virus = viruses[0] if viruses else None
        except Exception as e:
            print(f"Error loading viruses: {e}")
            virus = None
        
        if not virus:
            # Fallback mockup virus if file missing
            from models.virus import Virus
            virus = Virus("Unknown Pathogen", 0.5, 0.2, 0.1, 0.1, "Aggressive")

        # 3. LLM: prefer real client but fallback to mock if not configured or on error
        # support both GROQ_API_KEY (explicit) and API_KEY (common .env variable used by GroqClient)
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("API_KEY")
        client = None
        if api_key:
            try:
                client = GroqClient(api_key)
                print("Using Real Groq Client")
            except Exception as e:
                print("GroqClient init failed, falling back to MockClient:", e)
                client = MockClient()
        else:
            print("GROQ_API_KEY not set; using MockClient")
            client = MockClient()

        llm_interface = LLMInterface(client)
        
        # 4. Engine
        # Configure Deterministic Policy based on UI
        config_screen = self.screens.get('config')
        if config_screen:
            mode = getattr(config_screen, 'get_mode', lambda: 'stochastic')()
            if mode == 'deterministic':
                seed_val = getattr(config_screen, 'get_seed', lambda: '12345')()
                DeterministicPolicy.get().configure(seed_val)
                print(f"Policy configured: DETERMINISTIC (Seed: {seed_val})")
            else:
                DeterministicPolicy.get().configure(None)
                print("Policy configured: STOCHASTIC")

        engine = SimulationEngine(network, virus)
        engine.attach_llm(llm_interface)
        # Infect an initial patient-zero so the simulation can start spreading
        
        if network.nodes:
            first_node_id = DeterministicPolicy.get().choice(list(network.nodes.keys()))
            node = network.get_node(first_node_id)
            if node:
                node.infect()
        
        # 5. Pass to screen
        self.screens['execute'].set_engine(engine)
