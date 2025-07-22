import sqlite3
import json
from typing import Dict, List
from datetime import datetime
import logging

class DataStorage:
    def __init__(self, cache_path: str = "data/cache.db"):
        self.cache_path = cache_path
        self.buffer: List[Dict] = []
        self.logger = logging.getLogger(__name__)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database"""
        with sqlite3.connect(self.cache_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    timestamp REAL PRIMARY KEY,
                    data_json TEXT NOT NULL
                )
            """)

    def add(self, timestamp: datetime, data: Dict[str, float]) -> None:
        """Add data point to in-memory buffer"""
        self.buffer.append({"timestamp": timestamp.timestamp(), "data": data})
        
    def flush(self) -> None:
        """Flush buffer to persistent storage"""
        if not self.buffer:
            return
            
        try:
            with sqlite3.connect(self.cache_path) as conn:
                for point in self.buffer:
                    conn.execute(
                        "INSERT OR REPLACE INTO sensor_data VALUES (?, ?)",
                        (point["timestamp"], json.dumps(point["data"]))
                    )
                self.buffer.clear()
        except Exception as e:
            self.logger.error(f"Failed to flush buffer: {str(e)}")
            raise

    def query(self, start: datetime, end: datetime) -> List[Dict]:
        """Query stored data within time range"""
        results = []
        try:
            with sqlite3.connect(self.cache_path) as conn:
                cursor = conn.execute(
                    "SELECT timestamp, data_json FROM sensor_data WHERE timestamp BETWEEN ? AND ?",
                    (start.timestamp(), end.timestamp()))
                
                for row in cursor.fetchall():
                    results.append({
                        "timestamp": datetime.fromtimestamp(row[0]),
                        "data": json.loads(row[1])
                    })
        except Exception as e:
            self.logger.error(f"Query failed: {str(e)}")
            raise
            
        return results