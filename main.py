#!/usr/bin/env python3
import logging
from src.config import Config
from src.client import HeatPumpClient
from src.storage import DataStorage
from src.csvgen import CSVGenerator
from src.service import LuxLoggerService

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    setup_logging()
    
    # Load configuration
    config = Config()
    config.load()
    
    # Initialize components
    client = HeatPumpClient(config.host, config.port)
    storage = DataStorage(config.cache_path)
    csvgen = CSVGenerator(config.output_dirs)
    
    # Create and start service
    service = LuxLoggerService(config)
    
    try:
        service.start()
    except KeyboardInterrupt:
        service.stop()
    except Exception as e:
        logging.error(f"Service crashed: {str(e)}")
        raise

if __name__ == "__main__":
    main()