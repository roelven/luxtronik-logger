import os
import yaml
from typing import Dict, Any

class Config:
    def __init__(self):
        self.host: str = ""
        self.port: int = 8888
        self.interval_sec: int = 30
        self.csv_time: str = "07:00"
        self.cache_path: str = "data/cache.db"
        self.output_dirs: Dict[str, str] = {"daily": "data/reports/daily", "weekly": "data/reports/weekly"}
        self.csv_retention_days: int = 30
        self.disk_usage_threshold: int = 90

    def load(self, config_path: str = None) -> None:
        """Load configuration from YAML file and environment variables"""
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                yaml_config = yaml.safe_load(f) or {}
                self._update_from_dict(yaml_config)

        self._update_from_dict(os.environ)
        self._validate()

    def _update_from_dict(self, config: Dict[str, Any]) -> None:
        """Update config from dictionary (YAML or ENV vars)"""
        if "HOST" in config: self.host = str(config["HOST"])
        if "PORT" in config: self.port = int(config["PORT"])
        if "INTERVAL_SEC" in config: self.interval_sec = int(config["INTERVAL_SEC"])
        if "CSV_TIME" in config: self.csv_time = str(config["CSV_TIME"])
        if "CACHE_PATH" in config: self.cache_path = str(config["CACHE_PATH"])
        if "CSV_RETENTION_DAYS" in config: self.csv_retention_days = int(config["CSV_RETENTION_DAYS"])
        if "DISK_USAGE_THRESHOLD" in config: self.disk_usage_threshold = int(config["DISK_USAGE_THRESHOLD"])
        if "OUTPUT_DIRS_DAILY" in config and "OUTPUT_DIRS_WEEKLY" in config:
            self.output_dirs = {
                "daily": str(config["OUTPUT_DIRS_DAILY"]),
                "weekly": str(config["OUTPUT_DIRS_WEEKLY"])
            }
        # Also support the old OUTPUT_DIRS format for backward compatibility
        elif "OUTPUT_DIRS" in config:
            import json
            try:
                dirs = json.loads(config["OUTPUT_DIRS"])
                if "daily" in dirs and "weekly" in dirs:
                    self.output_dirs = {
                        "daily": str(dirs["daily"]),
                        "weekly": str(dirs["weekly"])
                    }
            except:
                pass  # Ignore invalid JSON

    def _validate(self) -> None:
        """Validate configuration values"""
        if not self.host:
            raise ValueError("HOST must be specified")
        if not 0 < self.port <= 65535:
            raise ValueError("PORT must be between 1-65535")
        if self.interval_sec < 5:
            raise ValueError("INTERVAL_SEC must be ≥5 seconds")
        if self.csv_retention_days < 1:
            raise ValueError("CSV_RETENTION_DAYS must be ≥1 day")
        if not 0 < self.disk_usage_threshold < 100:
            raise ValueError("DISK_USAGE_THRESHOLD must be between 1-99")
        # Add more validation as needed
