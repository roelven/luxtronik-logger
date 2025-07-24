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
        self._setup_signal_handlers()
        
    def _setup_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame) -> None:
        """Handle shutdown signals"""
        self.logger.info("Shutdown signal received")
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
            
            # Setup daily CSV generation
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
            
            # Configure default job settings
            self.scheduler._configure(
                job_defaults={
                    'coalesce': True,
                    'max_instances': 3,
                    'misfire_grace_time': 30
                }
            )
            
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
        
        client = HeatPumpClient(self.config.host, self.config.port)
        storage = DataStorage(self.config.cache_path)
        
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
        # Implementation will use storage and csvgen components