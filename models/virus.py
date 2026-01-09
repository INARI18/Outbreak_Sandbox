class VirusCharacteristics:
    def __init__(
        self,
        attack_power: float,
        spread_rate: float,
        stealth: float,
        mutation_rate: float,
        target_hosts: list[str],
        behavior: str
    ):  
        self.attack_power = attack_power
        self.spread_rate = spread_rate
        self.stealth = stealth
        self.mutation_rate = mutation_rate
        self.target_hosts = target_hosts
        self.behavior = behavior

    def clone(self):
        return VirusCharacteristics(
            attack_power=self.attack_power,
            spread_rate=self.spread_rate,
            stealth=self.stealth,
            mutation_rate=self.mutation_rate,
            target_hosts=self.target_hosts.copy(),
            behavior=self.behavior
        )
    

class Virus:
    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        characteristics: VirusCharacteristics,
        exploit: str,
        year: int,
        impact: str,
        vulnerability_window: int
    ):
        self.id = id
        self.name = name
        self.type = type
        self.characteristics = characteristics
        self.exploit = exploit
        self.year = year
        self.impact = impact
        self.vulnerability_window = vulnerability_window

    def mutate(self, new_characteristics: VirusCharacteristics):
        self.characteristics = new_characteristics

    def can_infect(self, node_type: str) -> bool:
        return node_type in self.characteristics.target_hosts
    

class VirusFactory:
    @staticmethod
    def _map_targets(priority: str) -> list[str]:
        mapping = {
            # Aggressive / Spread Fast (e.g. WannaCry) - targets almost everything
            "spread_fast": ["home_pc", "corp_workstation", "legacy_system", "cloud_server", "iot_device", "mainframe"],
            
            # Focused / Critical Infra (e.g. Stuxnet)
            "critical_infrastructure": ["mainframe", "cloud_server", "legacy_system"],
            
            # IoT / Botnet (e.g. Mirai)
            "weak_credentials": ["iot_device", "legacy_system"],
            
            # Standard / Balanced (e.g. Emotet)
            "balanced_spread": ["home_pc", "corp_workstation", "cloud_server"],
            "corporate_networks": ["corp_workstation", "cloud_server", "mainframe"],
            
            # Special / High Security Targets (e.g. APTs)
            "air_gapped_systems": ["legacy_system", "mainframe"] 
        }
        return mapping.get(priority, [])

    @staticmethod
    def from_dict(data: dict) -> Virus:
        c = data["characteristics"]

        characteristics = VirusCharacteristics(
            attack_power=c["attack_power"],
            spread_rate=c["speed"],          # JSON → engine
            stealth=c["stealth"],
            mutation_rate=c["mutation_rate"],
            target_hosts=VirusFactory._map_targets(
                c["target_priority"]
            ),
            behavior=c["behavior"]
        )

        return Virus(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            characteristics=characteristics,
            exploit=data["exploit"],
            year=data["year"],
            impact=data["impact"],
            vulnerability_window=data["vulnerability_window"]
        )



