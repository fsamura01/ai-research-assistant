import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
from src.utils.config import Config

class AgentLogger:
    """Manages agent interaction logs in a local SQLite database."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(Config.LOGS_DIR / "agent_history.db")
        self._initialize_db()

    def _initialize_db(self):
        """Create the logs table if it doesn't exist."""
        Config.LOGS_DIR.mkdir(exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                query TEXT,
                response TEXT,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                cost FLOAT,
                latency FLOAT,
                tools_used TEXT
            )
        """)
        conn.commit()
        conn.close()

    def log_interaction(self, query: str, response: str, usage, latency: float, tools: list):
        """Record an agent interaction."""
        prompt_tokens = usage.request_tokens or 0
        completion_tokens = usage.response_tokens or 0
        total_tokens = usage.total_tokens or 0
        
        # Mock cost calculation (Llama 3.3 70B hypothetical rates)
        # $0.15 per 1M input, $0.60 per 1M output
        cost = (prompt_tokens * 0.15 / 1_000_000) + (completion_tokens * 0.60 / 1_000_000)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO interactions 
            (query, response, prompt_tokens, completion_tokens, total_tokens, cost, latency, tools_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (query, response, prompt_tokens, completion_tokens, total_tokens, cost, latency, ",".join(tools)))
        conn.commit()
        conn.close()

    def get_logs(self, limit: int = 100) -> pd.DataFrame:
        """Retrieve recent logs as a Pandas DataFrame."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(f"SELECT * FROM interactions ORDER BY timestamp DESC LIMIT {limit}", conn)
        conn.close()
        return df

    def get_stats(self):
        """Calculate aggregate statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*), SUM(total_tokens), SUM(cost), AVG(latency) FROM interactions")
        total_queries, total_tokens, total_cost, avg_latency = cursor.fetchone()
        
        conn.close()
        return {
            "total_queries": total_queries or 0,
            "total_tokens": total_tokens or 0,
            "total_cost": total_cost or 0.0,
            "avg_latency": avg_latency or 0.0
        }

    def clear_logs(self):
        """Delete all interaction records from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM interactions")
        conn.commit()
        conn.close()
