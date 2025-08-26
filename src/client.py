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
        self.connection_timeout = 60  # seconds
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def connect(self) -> bool:
        """Establish connection to heat pump with retry logic"""
        self.logger.info(f"Attempting to connect to heat pump at {self.host}:{self.port} with {self.connection_timeout}s timeout")
        start_time = time.time()
        for attempt in range(self.max_retries):
            attempt_start = time.time()
            try:
                self.logger.debug(f"Connecting to heat pump at {self.host}:{self.port} (attempt {attempt + 1}/{self.max_retries})")
                # TODO: Pass timeout to Luxtronik connection when supported
                self.connection = Luxtronik(self.host, self.port)
                elapsed = time.time() - attempt_start
                self.logger.info(f"Successfully connected to heat pump at {self.host}:{self.port} (attempt {attempt + 1}, took {elapsed:.2f}s)")
                return True
            except Exception as e:
                elapsed = time.time() - attempt_start
                self.logger.warning(f"Connection attempt {attempt + 1} failed after {elapsed:.2f}s: {str(e)}")
                if attempt < self.max_retries - 1:
                    backoff_time = self.retry_delay * (2 ** attempt)
                    self.logger.info(f"Retrying in {backoff_time} seconds (exponential backoff)")
                    time.sleep(backoff_time)
                else:
                    total_elapsed = time.time() - start_time
                    self.logger.error(f"Failed to connect to heat pump after {self.max_retries} attempts over {total_elapsed:.2f}s. Final error: {str(e)}")
                    self.logger.error(f"Connection parameters: host={self.host}, port={self.port}, timeout={self.connection_timeout}s")
                    return False

    def get_all_sensors(self) -> Dict[str, float]:
        """Retrieve all sensor readings with error handling"""
        self.logger.debug("Starting get_all_sensors method")
        if not self.connection:
            if not self.connect():
                raise ConnectionError("Failed to establish connection to heat pump")

        try:
            self.logger.debug("Retrieving sensor readings from heat pump")
            start_time = time.time()

            # Get data using proper luxtronik API methods with numeric indices
            try:
                # Get all available data using numeric indices
                calculations_dict = {}
                parameters_dict = {}
                visibilities_dict = {}

                # Get calculations data (typically 275 items)
                for i in range(275):
                    try:
                        entry = self.connection.calculations.get(i)
                        if hasattr(entry, 'value'):
                            key_name = entry.name if hasattr(entry, 'name') and not entry.name.startswith('Unknown') else f"calculations.{i}"
                            calculations_dict[f"calculations.{key_name}"] = entry.value
                    except Exception as e:
                        self.logger.debug(f"Failed to get calculations.{i}: {e}")

                # Get parameters data (typically 1187 items)
                for i in range(1187):
                    try:
                        entry = self.connection.parameters.get(i)
                        if hasattr(entry, 'value'):
                            key_name = entry.name if hasattr(entry, 'name') and not entry.name.startswith('Unknown') else f"parameters.{i}"
                            parameters_dict[f"parameters.{key_name}"] = entry.value
                    except Exception as e:
                        self.logger.debug(f"Failed to get parameters.{i}: {e}")

                # Get visibilities data (typically 398 items)
                for i in range(398):
                    try:
                        entry = self.connection.visibilities.get(i)
                        if hasattr(entry, 'value'):
                            key_name = entry.name if hasattr(entry, 'name') and not entry.name.startswith('Unknown') else f"visibilities.{i}"
                            visibilities_dict[f"visibilities.{key_name}"] = entry.value
                    except Exception as e:
                        self.logger.debug(f"Failed to get visibilities.{i}: {e}")

            except Exception as api_error:
                self.logger.warning(f"API methods failed, falling back to __dict__: {api_error}")
                # Fallback to __dict__ approach if API methods fail
                calculations_dict = {f"calculations.{k}": v for k, v in self.connection.calculations.__dict__.items() if not k.startswith('_')}
                parameters_dict = {f"parameters.{k}": v for k, v in self.connection.parameters.__dict__.items() if not k.startswith('_')}
                visibilities_dict = {f"visibilities.{k}": v for k, v in self.connection.visibilities.__dict__.items() if not k.startswith('_')}

            readings = {}
            readings.update(calculations_dict)
            readings.update(parameters_dict)
            readings.update(visibilities_dict)

            self.logger.debug(f"Retrieved {len(readings)} sensor readings")
            self.logger.debug(f"Sample data: {dict(list(readings.items())[:3])}")  # Log first 3 items

            # Log data source information for debugging
            api_success = 'calculations_dict' in locals() and len(calculations_dict) > 0
            self.logger.debug(f"Data source: {'API methods' if api_success else '__dict__ fallback'}")

            elapsed = time.time() - start_time
            self.logger.debug(f"Retrieved {len(readings)} sensor readings in {elapsed:.2f}s")
            return readings

        except Exception as e:
            self.logger.error(f"Failed to read sensors after attempting connection: {str(e)}")
            self.logger.error(f"Error type: {type(e).__name__}")
            # Reset connection for next attempt
            self.connection = None
            self.logger.error(f"Error in get_all_sensors: {str(e)}")
            raise
