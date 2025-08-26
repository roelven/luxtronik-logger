import sqlite3
import json
from typing import Dict, List, Tuple
from datetime import datetime
import logging

# Import validation module
try:
    from validate_data import DataValidator, quick_validation
except ImportError:
    # Fallback for when validate_data is not available
    DataValidator = None
    quick_validation = None

class DataStorage:
    def __init__(self, cache_path: str = "data/cache.db", enable_validation: bool = True):
        self.cache_path = cache_path
        self.buffer: List[Dict] = []
        self.logger = logging.getLogger(__name__)
        self.enable_validation = enable_validation
        self.validator = DataValidator() if DataValidator and enable_validation else None
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

    def add(self, timestamp: datetime, data: Dict[str, float]) -> Tuple[bool, List[str]]:
        """Add data point to in-memory buffer with validation"""
        self.logger.debug(f"Adding data point to buffer at {timestamp.isoformat()}")

        # Validate data before storing
        validation_passed = True
        validation_messages = []

        if self.enable_validation and self.validator:
            validation_passed, validation_messages = self.validator.validate_sensor_data(data, timestamp)

            if not validation_passed:
                self.logger.warning(f"Data validation failed for timestamp {timestamp.isoformat()}")
                for message in validation_messages:
                    if message.startswith("❌"):
                        self.logger.error(f"Validation error: {message}")
                    else:
                        self.logger.warning(f"Validation warning: {message}")
            else:
                self.logger.debug(f"Data validation passed for timestamp {timestamp.isoformat()}")
        elif self.enable_validation and quick_validation:
            # Use quick validation if full validator not available
            validation_passed = quick_validation(data)
            if not validation_passed:
                self.logger.warning(f"Quick validation failed for timestamp {timestamp.isoformat()}")
                validation_messages = ["Quick validation failed - insufficient data quality"]

        # Only store data if validation passed or validation is disabled
        if validation_passed or not self.enable_validation:
            self.buffer.append({"timestamp": timestamp.timestamp(), "data": data})
            self.logger.debug(f"Buffer size now {len(self.buffer)} data points")
        else:
            self.logger.error(f"❌ NOT storing invalid data point at {timestamp.isoformat()}")
            self.logger.error(f"   Sensor count: {len(data)}")
            self.logger.error(f"   Validation errors: {len([m for m in validation_messages if m.startswith('❌')])}")

        return validation_passed, validation_messages

    def flush(self) -> Tuple[int, int]:
        """Flush buffer to persistent storage, returns (success_count, total_count)"""
        if not self.buffer:
            self.logger.debug("No data to flush, buffer is empty")
            return 0, 0

        total_count = len(self.buffer)
        self.logger.info(f"Flushing {total_count} data points to storage")

        self.logger.info(f"Flushing {len(self.buffer)} data points to storage")
        success_count = 0
        try:
            with sqlite3.connect(self.cache_path) as conn:
                for point in self.buffer:
                    try:
                        conn.execute(
                            "INSERT OR REPLACE INTO sensor_data VALUES (?, ?)",
                            (point["timestamp"], json.dumps(point["data"], default=str))
                        )
                        success_count += 1
                    except Exception as point_error:
                        self.logger.error(f"Failed to store data point at {point['timestamp']}: {point_error}")

                self.buffer.clear()

                if success_count == total_count:
                    self.logger.info(f"Successfully flushed all {success_count} data points to storage")
                else:
                    self.logger.warning(f"Partially flushed {success_count}/{total_count} data points to storage")
                    self.logger.warning(f"Failed to store {total_count - success_count} data points")

        except Exception as e:
            self.logger.error(f"Failed to flush {total_count} data points to storage: {str(e)}")
            self.logger.error(f"Error type: {type(e).__name__}")
            # Keep buffer intact for retry if flush completely failed
            if success_count == 0:
                raise
            else:
                # Remove successfully stored points from buffer
                self.buffer = self.buffer[success_count:]

        return success_count, total_count

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
