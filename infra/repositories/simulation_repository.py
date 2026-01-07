import json
from infra.database.db_manager import DBManager

class SimulationRepository:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    def create_simulation(self, virus_name: str, network_config: dict) -> int:
        """Creates a new simulation entry and returns its ID."""
        query = """
            INSERT INTO simulations (virus_name, network_config, final_status)
            VALUES (?, ?, ?)
        """
        config_json = json.dumps(network_config)
        return self.db.execute_insert(query, (virus_name, config_json, "running"))

    def save_step(self, simulation_id: int, step_number: int, stats: dict, nodes_snapshot: list):
        """
        Saves a single step of the simulation.
        stats: dict like {'infected': 10, 'healthy': 40, 'quarantined': 0}
        nodes_snapshot: list of dicts with node states
        """
        query = """
            INSERT INTO simulation_steps 
            (simulation_id, step_number, infected_count, quarantined_count, healthy_count, nodes_state)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        nodes_json = json.dumps(nodes_snapshot)
        self.db.execute_insert(query, (
            simulation_id,
            step_number,
            stats.get('infected', 0),
            stats.get('quarantined', 0),
            stats.get('healthy', 0),
            nodes_json
        ))

    def mark_finished(self, simulation_id: int):
        conn = self.db._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE simulations SET final_status = ? WHERE id = ?", ("finished", simulation_id))
        conn.commit()
        conn.close()

    def get_all_simulations(self):
        query = "SELECT id, created_at, virus_name, final_status FROM simulations ORDER BY created_at DESC"
        return self.db.execute_query(query)

    def delete_simulation(self, simulation_id: int):
        """Removes a simulation and its history from the database."""
        conn = self.db._get_connection()
        cursor = conn.cursor()
        try:
            # Delete steps first (foreign key)
            cursor.execute("DELETE FROM simulation_steps WHERE simulation_id = ?", (simulation_id,))
            # Delete simulation record
            cursor.execute("DELETE FROM simulations WHERE id = ?", (simulation_id,))
            conn.commit()
        finally:
            conn.close()

    def save_simulation_history(self, virus: str, network: dict, history: list, final_status: str = "finished") -> int:
        """
        Bulk saves the entire simulation history after execution.
        """
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Create Simulation Record
            cursor.execute("""
                INSERT INTO simulations (virus_name, network_config, final_status)
                VALUES (?, ?, ?)
            """, (virus, json.dumps(network), final_status))
            
            sim_id = cursor.lastrowid
            
            # 2. Bulk Insert Steps
            step_records = []
            for step_data in history:
                step_records.append((
                    sim_id,
                    step_data["step"],
                    step_data["stats"]["infected"],
                    step_data["stats"]["quarantined"],
                    step_data["stats"]["healthy"],
                    json.dumps(step_data["nodes_snapshot"])
                ))
            
            cursor.executemany("""
                INSERT INTO simulation_steps 
                (simulation_id, step_number, infected_count, quarantined_count, healthy_count, nodes_state)
                VALUES (?, ?, ?, ?, ?, ?)
            """, step_records)
            
            conn.commit()
            return sim_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_simulation_details(self, simulation_id: int):
        """Retrieves header and all steps for a specific simulation."""
        # 1. Get Header
        query_header = "SELECT * FROM simulations WHERE id = ?"
        header = self.db.execute_query(query_header, (simulation_id,))
        
        if not header:
            return None
            
        # 2. Get Steps
        query_steps = """
            SELECT step_number, infected_count, quarantined_count, healthy_count, nodes_state 
            FROM simulation_steps 
            WHERE simulation_id = ? 
            ORDER BY step_number ASC
        """
        steps_raw = self.db.execute_query(query_steps, (simulation_id,))
        
        steps = []
        for s in steps_raw:
            steps.append({
                "step": s[0],
                "stats": {
                    "infected": s[1],
                    "quarantined": s[2],
                    "healthy": s[3]
                },
                "nodes_snapshot": json.loads(s[4])
            })
            
        return {
            "info": header[0],
            "steps": steps
        }
