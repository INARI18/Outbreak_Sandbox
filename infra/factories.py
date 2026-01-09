import os
import keyring
from typing import Optional
from PySide6.QtCore import QSettings

from infra.providers.groq_provider import GroqProvider
from infra.providers.local_provider import LocalProvider
from infra.providers.mock_provider import MockProvider
from llm.interface import LLMInterface
from models.network import Network
from models.virus import Virus
from simulation.engine import SimulationEngine
from simulation.deterministic_policy import DeterministicPolicy
from infra.topologies import create_topology
from infra.network_factory import graph_to_network
from infra.repositories.virus_repository import VirusRepository


class SimulationFactory:
    """
    Centralizes logic of creating and configuring the simulation environment
    """

    @staticmethod
    def create_network(topology_type: str, node_count: int, seed: Optional[str] = None) -> Network:
        try:
            G = create_topology(topology_type, node_count)
        except KeyError:
            print(f"Unknown topology '{topology_type}', falling back to 'random'.")
            G = create_topology('random', node_count)
        return graph_to_network(G)

    @staticmethod
    def create_virus(virus_name: str | None = None) -> Virus:
        """Loads the selected virus or a default fallback."""
        project_root = os.getcwd()
        virus_path = os.path.join(project_root, "config/viruses.json")
        
        selected_virus = None
        try:
            repo = VirusRepository(virus_path)
            viruses = repo.load_all()
            
            if virus_name and viruses:
                for v in viruses:
                    if v.name == virus_name:
                        selected_virus = v
                        break
            
            if not selected_virus and viruses:
                selected_virus = viruses[0]

        except Exception as e:
            print(f"Error loading viruses: {e}")
        
        if not selected_virus:
            from models.virus import Virus, VirusCharacteristics
            chars = VirusCharacteristics(0.5, 0.2, 0.1, 0.1, [], "Aggressive")
            selected_virus = Virus("nop_v1", "Unknown Pathogen", "generic", chars, "none", 2024, "low", 0)

        return selected_virus

    @staticmethod
    def create_llm_interface() -> LLMInterface:
        settings = QSettings("OutbreakSandbox", "Config")
        use_local = settings.value("use_local_llm", False, type=bool)
        
        client = None

        if use_local:
            print("Factory: Configuring Local LLM Provider (Phi-3)")
            # Check if strictly required to be installed?
            # For now just instantiate, it handles its own readiness
            client = LocalProvider()
        else:
            api_key = os.getenv("GROQ_API_KEY") or os.getenv("API_KEY")
            if not api_key:
                try:
                    api_key = keyring.get_password("outbreak_sandbox", "groq_api_key")
                except Exception:
                    pass

            if api_key:
                try:
                    client = GroqProvider(api_key)
                    print("Factory: Using Real Groq Client")
                except Exception as e:
                    print(f"GroqProvider init failed: {e}. Falling back to Mock.")
                    client = MockProvider()
            else:
                print("Factory: No API Key found and Local Mode disabled. Using MockClient.")
                client = MockProvider()

        return LLMInterface(client)

    @staticmethod
    def configure_policy(mode: str, seed: str = '12345'):
        """Configures the global deterministic policy."""
        if mode == 'deterministic':
            DeterministicPolicy.get().configure(seed)
            print(f"Policy configured: DETERMINISTIC (Seed: {seed})")
        else:
            DeterministicPolicy.get().configure(None)
            print("Policy configured: STOCHASTIC")

    @classmethod
    def build_engine(cls, topology_key: str, node_count: int, virus_name: str, execution_mode: str, seed: str) -> SimulationEngine:
        """
        Orchestrates the creation of the full SimulationEngine.
        """
        # 1. Setup Policy
        cls.configure_policy(execution_mode, seed)

        # 2. Build Domain Entities
        network = cls.create_network(topology_key, node_count)
        virus = cls.create_virus(virus_name)
        llm_interface = cls.create_llm_interface()

        # 3. Setup Infection (Zero Patient)
        if network.nodes:
            first_node_id = DeterministicPolicy.get().choice(list(network.nodes.keys()))
            node = network.get_node(first_node_id)
            if node:
                node.infect()

        # 4. Construct Engine
        engine = SimulationEngine(network, virus, llm_interface=llm_interface, topology_type=topology_key)
        
        return engine
