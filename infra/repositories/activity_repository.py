import json
import os
from datetime import datetime

class ActivityRepository:
    """
    Manages Recent Activity logs for simulations.
    Persists data to 'recent_activity.json' in the project root.
    Keeps only the last 6 entries.
    """
    FILE_NAME = "recent_activity.json"

    def __init__(self, root_dir=None):
        self.root = root_dir if root_dir else os.getcwd()
        self.file_path = os.path.join(self.root, self.FILE_NAME)

    def load_activities(self):
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                # Sort by timestamp descending (newest first)
                data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                return data
        except Exception:
            return []

    def log_activity(self, sim_id, topology, node_count, virus, infection_rate):
        """
        Record a new simulation run.
        """
        entry = {
            "id": sim_id,
            "topology": f"{topology.capitalize()} ({node_count} nodes)",
            "virus": virus,
            "infection_rate": f"{infection_rate:.1f}%",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "timestamp": datetime.now().isoformat()
        }

        activities = self.load_activities()
        activities.insert(0, entry) # Insert at top
        
        # Keep only last 6
        activities = activities[:6]
        
        try:
            with open(self.file_path, "w") as f:
                json.dump(activities, f, indent=4)
        except Exception as e:
            print(f"Failed to save activity: {e}")
