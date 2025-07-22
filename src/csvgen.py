import csv
import os
from datetime import datetime, timedelta
from typing import List, Dict
import logging

class CSVGenerator:
    def __init__(self, output_dirs: Dict[str, str]):
        self.output_dirs = output_dirs
        self.logger = logging.getLogger(__name__)
        self._ensure_dirs()
    
    def _ensure_dirs(self) -> None:
        """Create output directories if they don't exist"""
        for dir_path in self.output_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
    
    def generate_daily_csv(self, data: List[Dict], date: datetime) -> str:
        """Generate daily CSV file for given date"""
        filename = f"{date.strftime('%Y-%m-%d')}_daily.csv"
        filepath = os.path.join(self.output_dirs["daily"], filename)
        
        self._write_csv(filepath, data)
        return filepath
    
    def generate_weekly_csv(self, data: List[Dict], date: datetime) -> str:
        """Generate weekly CSV file for week containing given date"""
        filename = f"{date.strftime('%Y-%m-%d')}_weekly.csv"
        filepath = os.path.join(self.output_dirs["weekly"], filename)
        
        self._write_csv(filepath, data)
        return filepath
    
    def _write_csv(self, filepath: str, data: List[Dict]) -> None:
        """Write data to CSV file with headers"""
        if not data:
            self.logger.warning(f"No data to write to {filepath}")
            return
            
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0]["data"].keys())
                writer.writeheader()
                for point in data:
                    writer.writerow(point["data"])
        except Exception as e:
            self.logger.error(f"Failed to write CSV: {str(e)}")
            raise