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
        self.logger.debug(f"Initializing database at {self.cache_path}")
        try:
            with sqlite3.connect(self.cache_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sensor_data (
                        timestamp REAL PRIMARY KEY,
                        data_json TEXT NOT NULL
                    )
                """)
            self.logger.debug(f"Database initialized successfully at {self.cache_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize database at {self.cache_path}: {str(e)}")
            raise

    def add(self, timestamp: datetime, data: Dict[str, float]) -> None:
        """Add data point to in-memory buffer"""
        self.logger.debug(f"Adding data point to buffer at {timestamp.isoformat()}")
        self.buffer.append({"timestamp": timestamp.timestamp(), "data": data})
        self.logger.debug(f"Buffer size now {len(self.buffer)} data points")

    def flush(self) -> None:
        """Flush buffer to persistent storage"""
        if not self.buffer:
            self.logger.debug("No data to flush, buffer is empty")
            return

        self.logger.info(f"Flushing {len(self.buffer)} data points to storage")
        try:
            with sqlite3.connect(self.cache_path) as conn:
                flushed_count = 0
                for point in self.buffer:
                    conn.execute(
                        "INSERT OR REPLACE INTO sensor_data VALUES (?, ?)",
                        (point["timestamp"], json.dumps(point["data"]))
                    )
                    flushed_count += 1
                self.buffer.clear()
                self.logger.info(f"Successfully flushed {flushed_count} data points to storage")
        except Exception as e:
            self.logger.error(f"Failed to flush {len(self.buffer)} data points to storage: {str(e)}")
            self.logger.error(f"Error type: {type(e).__name__}")
            raise

    def query(self, start: datetime, end: datetime) -> List[Dict]:
        """Query stored data within time range"""
        self.logger.debug(f"Querying data between {start.isoformat()} and {end.isoformat()}")
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
            self.logger.debug(f"Query returned {len(results)} data points")
        except Exception as e:
            self.logger.error(f"Query failed between {start.isoformat()} and {end.isoformat()}: {str(e)}")
            self.logger.error(f"Error type: {type(e).__name__}")
            raise

        return results
