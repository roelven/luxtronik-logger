import logging
from typing import Dict
from luxtronik import Luxtronik

class HeatPumpClient:
    def __init__(self, host: str, port: int = 8888):
        self.host = host
        self.port = port
        self.connection = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """Establish connection to heat pump with retry logic"""
        try:
            self.connection = Luxtronik(self.host, self.port)
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            return False
            
    def get_all_sensors(self) -> Dict[str, float]:
        """Retrieve all sensor readings with error handling"""
        if not self.connection:
            if not self.connect():
                raise ConnectionError("Failed to establish connection")
                
        try:
            readings = {}
            # Get raw data from connection
            calculations = {f"calculations.{k}": v for k, v in self.connection.calculations.__dict__.items() if not k.startswith('_')}
            parameters = {f"parameters.{k}": v for k, v in self.connection.parameters.__dict__.items() if not k.startswith('_')}
            visibilities = {f"visibilities.{k}": v for k, v in self.connection.visibilities.__dict__.items() if not k.startswith('_')}
            
            readings.update(calculations)
            readings.update(parameters)
            readings.update(visibilities)
            return readings
            
        except Exception as e:
            self.logger.error(f"Failed to read sensors: {str(e)}")
            raise