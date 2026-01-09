# Outbreak Sandbox

> Experimental malware propagation and cyber defense simulator assisted by Artificial Intelligence.

**Outbreak Sandbox** is an interactive graphical platform that allows you to simulate, visualize, and interact with complex network topologies where digital viruses spread guided by LLMs.

**Note:** This system was not designed for advanced security analysis, real audits, or rigorous academic research. The goal is purely experimental: to provide a visual environment to observe how a language model interacts with graph theory concepts and infection strategies in a controlled scenario.

## 📁 Project Architecture

### Folder Structure

```
├── main.py                                     # Application entry point
├── config/                                     # Static configuration files
│   ├── node_types.json                         # Network device definitions and stats
│   └── viruses.json                            # Predefined virus catalog
├── data/                                       # Runtime data storage
│   └── recent_activity.json                    # Recent simulation history log
├── infra/                                      # Infrastructure Layer
│   ├── factories.py                            # Centralized object creation (Factory Pattern)
│   ├── database/                               # Persistence management
│   │   └── db_manager.py                       # SQLite database handler
│   ├── repositories/                           # Data access (JSON/DB)
│   │   ├── node_type_repository.py             # Node configuration access
│   │   ├── simulation_repository.py            # Simulation state persistence
│   │   ├── activity_repository.py              # Recent history
│   │   └── virus_repository.py                 # Malware catalog
│   ├── providers/                              # AI Service Providers
│   │   ├── groq_provider.py                    # Cloud AI integration (Groq)
│   │   └── local_provider.py                   # Local Ai integretation ()
├── llm/                                        # AI Business Logic
│   ├── parsers/                                # Response interpreters (JSON)
│   ├── prompts/                                # Prompt engineering (txt)
│   └── interface.py                            # Facade for the simulation engine
├── models/                                     # Domain Models
│   ├── enums.py                                # Domain enumerators
│   ├── network.py                              # Network graph and nodes
│   ├── node.py                                 # Connected entities
│   └── virus.py                                # Pathogen definition
├── simulation/                                 # Simulation Core
│   ├── engine.py                               # Main Loop (Simulation Loop)
│   ├── propagation.py                          # Infection mathematics
│   ├── mutation.py                             # Virus evolution logic
│   └── stop_conditions.py                      # Termination rules
└── ui/                                         # Graphical Interface (PySide6)
    ├── app.py                                  # Qt application configuration
    ├── main_window.py                          # Navigation manager
    ├── components/                             # Reusable widgets
    │   ├── common/                             # Shared components (Buttons, Headers, Dialogs)
    │   ├── home/                               # Home screen specific widgets
    │   ├── execution/                          # Execution dashboard components
    │   └── visualizers/                        # Complex visualizers (Network Graph)
    ├── utils/                                  # Shared UI utilities (Icons, Base Classes)
    │   ├── base.py                             # Common widget bases
    │   └── generic_screen.py                   # Template for consistent screens
    └── screens/                                # Application screens
        ├── home_screen.py                      # Dashboard
        ├── welcome_screen.py                   # Initial onboarding & API Key
        ├── simulation_execution.py             # Real-time dashboard
        ├── history_screen.py                   # Past simulations
        └── simulation_setup/                   # Scenario configuration (Wizard package)
            ...
```

## 🧠 AI Integration

### 1. Cloud AI (Groq API) - _Recommended_

Connects to the ultra-fast Llama 3 models hosted by Groq. Requires an internet connection.

1.  **Get a Key:** Create a free account at [Groq Cloud](https://console.groq.com/) and generate an API Key.
2.  **Configuration:**
    - Open **Settings** (Gear icon in the header) or click **"API Key"**.
    - Toggle "Use Local LLM" to **OFF**.
    - Enter your API Key in the "Groq Cloud API Key" field.
    - Click **Save**.
3.  **Security Note:** Your API key is stored using your system's keyring service via the `keyring` Python library.

### 2. Local AI (Microsoft Phi-3)

Runs entirely on your machine uses **Microsoft Phi-3-mini-4k-instruct** via Hugging Face `transformers`. Useful for offline usage.

1.  **Configuration:**
    - Open **Settings**.
    - Toggle "Use Local LLM" to **ON**.
    - If not manually downloaded via Settings, the system will download the model (approx 2GB) automatically on the first run.
2.  **Dependencies:** Ensure you have `torch` and `transformers` installed.

---

## 🏗️ Simulation Core

### Simulation Engine

The `SimulationEngine` orchestrates time (steps) and checks stop conditions.

#### Execution Flow

1.  **Stop Check:** Checks if everyone is infected or time has run out.
2.  **AI Query:** Sends the current network state to the selected Provider (Groq or Local).
3.  **Decision:** Receives instruction on which node to infect and which strategy to use.
4.  **Propagation:** Calculates success based on virus attributes vs. node security.
5.  **Visualization:** The UI is updated in real-time.

### Data Structure

#### Virus (`models/virus.py`)

Possesses attributes that determine its success:

```python
class VirusCharacteristics:
    attack_power: float    # Brute force (0.0 to 10.0)
    stealth: float         # Ability to hide
    spread_rate: float     # Propagation speed
    mutation_rate: float   # Chance to alter its stats
    behavior: str          # Profile (e.g., "Aggressive", "Stealthy")
```

#### Network Node (`models/node.py`)

Represents devices (PC, Server, IoT):

```python
class Node:
    id: str
    type: str              # 'server', 'pc', 'iot', etc.
    security_level: float  # Defense against attacks
    status: str            # 'healthy', 'infected', 'quarantined'
```

## 📊 Propagation Mechanics

Propagation uses different attack strategies:

1.  **Exploit (Default):** Balanced between Attack and Defense. Medium detection chance. Uses the virus's base `attack_power` against the node's `security_level`.
2.  **Brute Force:** Increases attack power by **50%**, but drastically reduces stealth, increasing detection probability.
3.  **Phishing (Social Engineering):** Ignores technical defenses of **PC/User** nodes, relying on the virus's `stealth` and randomness. Less effective against Servers or IoT devices.

## 🚀 Step-by-Step: Running a Simulation

1.  **Start:** Upon opening the app, navigate to the **Simulation Setup** wizard.
2.  **Topology:** Choose the network shape (e.g., Mesh, Star, Grid) and the total number of nodes.
3.  **Virus:** Select a virus from the predefined list (e.g., **WannaCry**, **Emotet**). Each malware has its own characteristics.
4.  **Configuration:** Choose the simulation mode:
    - **Stochastic:** Probabilistic results.
    - **Deterministic:** Fixed results based on a "Seed".
5.  **Execution:**
    - The main panel will display the network graph.
    - The system will pause to load the necessary AI engine (Cloud or Local).
    - The simulation will automatically choose the first infected node.
    - Follow the AI decision log across the logic steps: **Target Selection** -> **Attack Validation** -> **Mutation Check**.

## 💻 Installation and Execution

### Prerequisites

- Python 3.10+
- Virtual environment (venv) recommended

### Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure variables (Optional, to use Real AI)
# Create the .env file with: GROQ_API_KEY=your_key_here

# 3. Run
python main.py
```

## 🔮 Future Roadmap

- **Timeline Navigation:** Implementation of a simulation playback system to retrace steps (forward/backward) for detailed analysis.
- **Persistence Layer:** Integration with local SQL databases to save simulation outcomes and history.
- **Custom Virus Builder:** A dedicated interface for designing personalized pathogen profiles with custom attribute distribution.
- **Advanced Analytics:** Interactive charts and graphs to visualize infection trends, node compromise rates, and comparative statistics between disparate runs.
