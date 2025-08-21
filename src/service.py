import time
import signal
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time as dtime
from typing import Dict

class LuxLoggerService:
    def __init__(self, config):
        self.config = config
        # Configure scheduler with proper job handling
        self.scheduler = BackgroundScheduler()
        self.logger = logging.getLogger(__name__)
        self.storage = None  # Will be initialized in _poll_sensors
        self.csvgen = None  # Will be initialized in _generate_reports
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame) -> None:
        """Handle shutdown signals"""
        self.logger.info(f"Shutdown signal {signum} received")
        # Flush any buffered data before shutting down
        if self.storage and self.storage.buffer:
            self.logger.info(f"Flushing {len(self.storage.buffer)} buffered data points before shutdown")
            try:
                self.storage.flush()
                self.logger.info("Buffer flushed successfully before shutdown")
            except Exception as e:
                self.logger.error(f"Failed to flush buffer before shutdown: {str(e)}")
        self.stop()

    def start(self) -> None:
        """Start the service and scheduler"""
        try:
            # Setup polling job with proper configuration to prevent blocking
            self.scheduler.add_job(
                self._poll_sensors,
                'interval',
                seconds=self.config.interval_sec,
                max_instances=3,
                coalesce=True,
                misfire_grace_time=30,
                id='poll_sensors_job'
            )

            # Setup daily CSV generation and cleanup
            csv_time = [int(x) for x in self.config.csv_time.split(':')]
            self.scheduler.add_job(
                self._generate_reports,
                'cron',
                hour=csv_time[0],
                minute=csv_time[1],
                max_instances=1,
                coalesce=True,
                misfire_grace_time=300,
                id='generate_reports_job'
            )

            # The scheduler is already configured with default job settings
            # through the constructor configuration, so we don't need to call _configure

            self.scheduler.start()
            self.logger.info("Service started")
            self.logger.info(f"Scheduler config: {self.scheduler._job_defaults}")

            # Keep main thread alive
            while True:
                time.sleep(1)

        except Exception as e:
            self.logger.error(f"Service failed: {str(e)}")
            raise

    def stop(self) -> None:
        """Stop the service gracefully"""
        self.logger.info("Stopping service")
        self.scheduler.shutdown()

    def _poll_sensors(self) -> None:
        """Poll heat pump sensors and store data"""
        self.logger.info("Polling sensors - job started")

        from src.client import HeatPumpClient
        from src.storage import DataStorage
        from src.utils import check_disk_usage

        # Check disk space before polling
        try:
            paths_to_check = [self.config.cache_path] + list(self.config.output_dirs.values())
            exceeding_paths = check_disk_usage(paths_to_check, self.config.disk_usage_threshold, self.logger)
            if exceeding_paths:
                self.logger.warning(f"Disk usage threshold exceeded for {len(exceeding_paths)} paths before polling")
        except Exception as e:
            self.logger.error(f"Disk usage check failed before polling: {str(e)}")

        client = HeatPumpClient(self.config.host, self.config.port)
        # Store reference to storage for shutdown handling
        if self.storage is None:
            self.storage = DataStorage(self.config.cache_path)
        storage = self.storage

        try:
            sensor_data = client.get_all_sensors()
            storage.add(datetime.now(), sensor_data)
            storage.flush()
            self.logger.info(f"Stored {len(sensor_data)} sensor readings - job completed")
        except Exception as e:
            self.logger.error(f"Failed to poll sensors: {str(e)}")
            # Don't raise the exception to prevent job from crashing the scheduler
            # The retry logic is handled in the client
            self.logger.info("Polling job completed with errors")

    def _generate_reports(self) -> None:
        """Generate daily and weekly reports"""
        self.logger.info("Generating reports")

        from src.storage import DataStorage
        from src.csvgen import CSVGenerator
        from src.utils import check_disk_usage

        # Check disk space before generating reports
        try:
            paths_to_check = [self.config.cache_path] + list(self.config.output_dirs.values())
            exceeding_paths = check_disk_usage(paths_to_check, self.config.disk_usage_threshold, self.logger)
            if exceeding_paths:
                self.logger.warning(f"Disk usage threshold exceeded for {len(exceeding_paths)} paths")
        except Exception as e:
            self.logger.error(f"Disk usage check failed: {str(e)}")

        # Initialize csvgen if not already done
        if self.csvgen is None:
            self.csvgen = CSVGenerator(self.config.output_dirs)

        # Run cleanup first
        try:
            self.csvgen.cleanup_old_csvs(self.config.csv_retention_days)
        except Exception as e:
            self.logger.error(f"CSV cleanup failed: {str(e)}")

        # Implementation will use storage and csvgen components for report generation
