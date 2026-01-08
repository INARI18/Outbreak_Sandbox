# Outbreak Sandbox

> Experimental malware propagation and cyber defense simulator assisted by Artificial Intelligence.

**Outbreak Sandbox** is an interactive graphical platform that allows you to simulate, visualize, and interact with complex network topologies where digital viruses spread guided by LLMs.

**Note:** This system was not designed for advanced security analysis, real audits, or rigorous academic research. The goal is purely experimental: to provide a visual environment to observe how a language model interacts with graph theory concepts and infection strategies in a controlled scenario.

## 📁 Project Architecture

### Folder Structure

```
├── main.py                                 # Application entry point
├── infra/                                  # Infrastructure Layer
│   ├── factories.py                        # Centralized object creation (Factory Pattern)
│   ├── databases/                          # Persistence management
│   ├── repositories/                       # Data access (JSON/DB)
│   │   ├── activity_repository.py          # Recent history
│   │   └── virus_repository.py             # Malware catalog
│   └── llm/                                # API Clients (Groq/Mock)
├── llm/                                    # AI Business Logic
│   ├── parsers/                            # Response interpreters (JSON)
│   ├── prompts/                            # Prompt engineering (txt)
│   └── interface.py                        # Facade for the simulation engine
├── models/                                 # Domain Models
│   ├── enums.py                            # Domain enumerators
│   ├── network.py                          # Network graph and nodes
│   ├── node.py                             # Connected entities
│   └── virus.py                            # Pathogen definition
├── simulation/                             # Simulation Core
│   ├── engine.py                           # Main Loop (Simulation Loop)
│   ├── propagation.py                      # Infection mathematics
│   ├── mutation.py                         # Virus evolution logic
│   └── stop_conditions.py                  # Termination rules
└── ui/                                     # Graphical Interface (PySide6)
    ├── app.py                              # Qt application configuration
    ├── main_window.py                      # Navigation manager
    ├── components/                         # Reusable widgets
    │   ├── home/                           # Home screen specific widgets
    │   │   ├── navbar.py                   # Side navigation
    │   │   ├── welcome_hero.py             # Hero section
    │   │   └── ...                         # Dashboard cards
    │   ├── buttons.py                      # Custom buttons
    │   ├── header.py                       # Standard app header
    │   └── network_visualizer.py           # Graph rendering
    └── screens/                            # Application screens
        ├── simulation_execution.py         # Real-time dashboard
        └── simulation_setup/               # Scenario configuration (Wizard package)
            ├── topology_screen.py          # Network topology selection
            ├── virus_screen.py             # Malware selection
            ├──  configuration_screen.py    # Simulation parameters
            └── ...
```

## 🧠 AI Integration (Groq)

This project uses the **Groq** API to provide the virus "brain", allowing it to take decisions based on the current network state.

### API Key Configuration

To use the real AI, you need a Groq account (the free plan works) to get an access key.

1.  Create an account at [Groq Cloud](https://console.groq.com/).
2.  Generate an API Key in the console.
3.  **In the App:** When starting Outbreak Sandbox, click the **"API Key"** button on the home screen and paste your key.
4.  **Alternatively (.env):** You can create a `.env` file in the project root with the content `GROQ_API_KEY=your_api_key`.

If no key is configured, the system will automatically use a **Mock Client**. In this mode, the virus decisions will be random, with no AI reasoning, but ensuring the application works for interface testing.

## 🏗️ Simulation Core

### Simulation Engine

The `SimulationEngine` orchestrates time (steps) and checks stop conditions.

#### Execution Flow

1.  **Stop Check:** Checks if everyone is infected or time has run out.
2.  **AI Query:** Sends the current network state to the LLM interface.
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

1.  **Exploit (Default):** Balanced between Attack and Defense. Medium detection chance.
2.  **Brute Force:** +50% attack, but ignores stealth. High detection chance.
3.  **Phishing (Social Engineering):** Focuses on stealth. Very effective against human nodes (PCs), less effective against servers.

## 🚀 Step-by-Step: Running a Simulation

1.  **Start:** Upon opening the app, navigate to the configuration screen.
2.  **Topology:** Choose the network shape (e.g., Mesh, Star, Grid) and the total number of nodes.
3.  **Virus:** Select a virus from the predefined list. Each malware has its own characteristics of aggressiveness and stealth.
4.  **Configuration:** Choose the simulation mode:
    - **Stochastic:** Probabilistic results (role-playing).
    - **Deterministic:** Fixed results based on a "Seed". Useful for replicating exact scenarios.
5.  **Execution:**
    - The main panel will display the network graph.
    - The simulation will automatically choose the first infected node.
    - Follow the AI decision log in the side panel while the infection visually spreads through the network.

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
