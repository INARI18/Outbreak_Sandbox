import sqlite3
import os

class DBManager:
    def __init__(self, db_path: str = "data/simulation_history.db"):
        self.db_path = db_path
        self._initialize_schema()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_schema(self):
        """Creates the necessary tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Table: simulations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                virus_name TEXT NOT NULL,
                network_config TEXT NOT NULL,
                final_status TEXT
            )
        """)

        # Table: simulation_steps
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulation_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simulation_id INTEGER NOT NULL,
                step_number INTEGER NOT NULL,
                infected_count INTEGER NOT NULL,
                quarantined_count INTEGER NOT NULL,
                healthy_count INTEGER NOT NULL,
                nodes_state JSON NOT NULL,
                FOREIGN KEY (simulation_id) REFERENCES simulations (id)
            )
        """)
        
        conn.commit()
        conn.close()

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Executes an INSERT query and returns the last inserted row ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Executes a SELECT query and returns all results."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            conn.close()
