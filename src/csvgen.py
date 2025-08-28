import csv
import os
import glob
from datetime import datetime, timedelta
from typing import List, Dict
import logging

class CSVGenerator:
    # Mapping of raw sensor IDs to human-readable names
    SENSOR_NAME_MAPPINGS = {
        "calculations.ID_WEB_Temperatur_TVL": "Flow Temperature",
        "calculations.ID_WEB_Temperatur_TRL": "Return Temperature",
        "calculations.ID_WEB_Temperatur_TA": "Ambient Temperature",
        "calculations.ID_WEB_Temperatur_TBW": "Hot Water Temperature",
        # Add more mappings as needed
    }

    def __init__(self, output_dirs: Dict[str, str]):
        self.output_dirs = output_dirs
        self.logger = logging.getLogger(__name__)
        self._ensure_dirs()
        # Read readable headers setting from environment
        self.readable_headers = os.getenv("READABLE_HEADERS", "false").lower() == "true"

    def _ensure_dirs(self) -> None:
        """Create output directories if they don't exist"""
        for dir_path in self.output_dirs.values():
            os.makedirs(dir_path, exist_ok=True)

    def cleanup_old_csvs(self, retention_days: int) -> None:
        """Delete CSV files older than retention_days"""
        self.logger.debug(f"Starting CSV cleanup with {retention_days} day retention")

        if retention_days < 1:
            self.logger.warning("CSV retention days must be >= 1, skipping cleanup")
            return

        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0
        total_freed_bytes = 0

        for dir_type, dir_path in self.output_dirs.items():
            self.logger.debug(f"Processing {dir_type} directory: {dir_path}")

            if not os.path.exists(dir_path):
                self.logger.warning(f"Directory does not exist, skipping: {dir_path}")
                continue

            # Find all CSV files in the directory
            csv_pattern = os.path.join(dir_path, "*.csv")
            csv_files = glob.glob(csv_pattern)
            self.logger.debug(f"Found {len(csv_files)} CSV files in {dir_path}")

            for file_path in csv_files:
                try:
                    # Get file modification time
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

                    # Delete if older than cutoff date
                    if file_mtime < cutoff_date:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_count += 1
                        total_freed_bytes += file_size
                        self.logger.info(f"Deleted old {dir_type} CSV: {os.path.basename(file_path)} "
                                       f"(modified: {file_mtime.strftime('%Y-%m-%d %H:%M:%S')}, "
                                       f"size: {file_size} bytes)")
                except Exception as e:
                    self.logger.warning(f"Failed to process {file_path} for cleanup: {str(e)}")
                    self.logger.warning(f"Error type: {type(e).__name__}")

        if deleted_count > 0:
            # Convert bytes to MB for readable logging
            freed_mb = total_freed_bytes / (1024 * 1024)
            self.logger.info(f"CSV cleanup completed: {deleted_count} files deleted, {freed_mb:.2f} MB freed")
        else:
            self.logger.info("CSV cleanup completed: No old files found")

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

    def _convert_to_readable_name(self, raw_id: str) -> str:
        """Convert raw sensor ID to human-readable name if mapping exists"""
        return self.SENSOR_NAME_MAPPINGS.get(raw_id, raw_id)

    def _get_readable_fieldnames(self, fieldnames: List[str]) -> List[str]:
        """Convert fieldnames to readable names if readable_headers is enabled"""
        if not self.readable_headers:
            return fieldnames

        return [self._convert_to_readable_name(field) for field in fieldnames]

    def _write_csv(self, filepath: str, data: List[Dict]) -> None:
        """Write data to CSV file with headers"""
        self.logger.debug(f"Writing CSV file: {filepath} with {len(data)} data points")

        if not data:
            self.logger.warning(f"No data to write to {filepath}")
            return

        try:
            # Get original fieldnames
            original_fieldnames = list(data[0]["data"].keys())

            # Convert to readable fieldnames if enabled
            fieldnames = self._get_readable_fieldnames(original_fieldnames)

            # Create a mapping from original to readable fieldnames
            fieldname_mapping = {
                original: readable
                for original, readable in zip(original_fieldnames, fieldnames)
            }

            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                row_count = 0
                for point in data:
                    # Convert data keys to readable names if needed
                    if self.readable_headers:
                        readable_data = {
                            fieldname_mapping[key]: value
                            for key, value in point["data"].items()
                        }
                        writer.writerow(readable_data)
                    else:
                        writer.writerow(point["data"])
                    row_count += 1
            self.logger.info(f"Successfully wrote CSV file: {filepath} with {row_count} rows")
        except Exception as e:
            self.logger.error(f"Failed to write CSV file {filepath}: {str(e)}")
            self.logger.error(f"Error type: {type(e).__name__}")
            raise
