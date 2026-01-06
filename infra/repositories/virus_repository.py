import json
from models.virus import VirusFactory

class VirusRepository:

    def __init__(self, json_path: str):
        self.json_path = json_path

    def load_all(self) -> list:
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [
            VirusFactory.from_dict(v)
            for v in data["viruses"]
        ]
