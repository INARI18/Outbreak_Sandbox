import json
import os
from datetime import datetime

class StatsRepository:
    def __init__(self, filepath="recent_activity.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._save([])

    def _load(self):
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save(self, data):
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=4)

    def add_simulation_run(self, simulation_id, topology, node_count, virus, infection_rate):
        history = self._load()
        
        entry = {
            "simulation_id": simulation_id,
            "topology": f"{topology.capitalize()} ({node_count} nodes)",
            "virus": virus,
            "infection_rate": f"{infection_rate:.1f}%",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        # Add to beginning
        history.insert(0, entry)
        
        # Keep only last 6
        if len(history) > 6:
            history = history[:6]
            
        self._save(history)

    def get_recent_activity(self):
        return self._load()
