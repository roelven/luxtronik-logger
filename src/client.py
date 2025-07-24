import logging
import time
from typing import Dict
from luxtronik import Luxtronik

class HeatPumpClient:
    def __init__(self, host: str, port: int = 8888):
        self.host = host
        self.port = port
        self.connection = None
        self.logger = logging.getLogger(__name__)
        self.connection_timeout = 10  # seconds
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
    def connect(self) -> bool:
        """Establish connection to heat pump with retry logic"""
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Connecting to heat pump at {self.host}:{self.port} (attempt {attempt + 1}/{self.max_retries})")
                self.connection = Luxtronik(self.host, self.port)
                self.logger.info(f"Successfully connected to heat pump at {self.host}:{self.port}")
                return True
            except Exception as e:
                self.logger.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    self.logger.error(f"Failed to connect to heat pump after {self.max_retries} attempts: {str(e)}")
                    return False
                    
    def get_all_sensors(self) -> Dict[str, float]:
        """Retrieve all sensor readings with error handling"""
        if not self.connection:
            if not self.connect():
                raise ConnectionError("Failed to establish connection to heat pump")
                
        try:
            readings = {}
            # Get raw data from connection
            calculations = {f"calculations.{k}": v for k, v in self.connection.calculations.__dict__.items() if not k.startswith('_')}
            parameters = {f"parameters.{k}": v for k, v in self.connection.parameters.__dict__.items() if not k.startswith('_')}
            visibilities = {f"visibilities.{k}": v for k, v in self.connection.visibilities.__dict__.items() if not k.startswith('_')}
            
            readings.update(calculations)
            readings.update(parameters)
            readings.update(visibilities)
            self.logger.debug(f"Retrieved {len(readings)} sensor readings")
            return readings
            
        except Exception as e:
            self.logger.error(f"Failed to read sensors: {str(e)}")
            # Reset connection for next attempt
            self.connection = None
            raise