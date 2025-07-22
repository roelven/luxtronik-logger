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
        self.output_dirs: Dict[str, str] = {"daily": "data/daily", "weekly": "data/weekly"}

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
        if "OUTPUT_DIRS_DAILY" in config and "OUTPUT_DIRS_WEEKLY" in config:
            self.output_dirs = {
                "daily": str(config["OUTPUT_DIRS_DAILY"]),
                "weekly": str(config["OUTPUT_DIRS_WEEKLY"])
            }

    def _validate(self) -> None:
        """Validate configuration values"""
        if not self.host:
            raise ValueError("HOST must be specified")
        if not 0 < self.port <= 65535:
            raise ValueError("PORT must be between 1-65535")
        if self.interval_sec < 5:
            raise ValueError("INTERVAL_SEC must be ≥5 seconds")
        # Add more validation as needed