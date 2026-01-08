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
import keyring

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
        print("Initializing Simulation...")
        topo_screen = self.screens.get('topology')
        topology_key = getattr(topo_screen, 'get_selected_topology', lambda: 'random')()
        node_count = getattr(topo_screen, 'get_node_count', lambda: 30)()
        try:
            G = create_topology(topology_key, int(node_count))
        except KeyError:
            print(f"Unknown topology '{topology_key}', falling back to 'random'.")
            G = create_topology('random', int(node_count))

        network = graph_to_network(G)
        
        project_root = os.getcwd() 
        virus_path = os.path.join(project_root, "viruses.json")
        
        try:
            repo = VirusRepository(virus_path)
            viruses = repo.load_all()
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
            from models.virus import Virus
            virus = Virus("Unknown Pathogen", 0.5, 0.2, 0.1, 0.1, "Aggressive")

        # 3. LLM Configuration
        # Priority:
        # 1. Environment Variable (.env)
        # 2. System Keyring (saved via UI)
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("API_KEY")
        
        if not api_key:
            try:
                api_key = keyring.get_password("outbreak_sandbox", "groq_api_key")
            except Exception:
                pass

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
        
        if network.nodes:
            first_node_id = DeterministicPolicy.get().choice(list(network.nodes.keys()))
            node = network.get_node(first_node_id)
            if node:
                node.infect()
        
        self.screens['execute'].set_engine(engine)
