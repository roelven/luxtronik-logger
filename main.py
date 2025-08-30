#!/usr/bin/env python3
import argparse
import logging
import sys
import threading
import os
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
    parser = argparse.ArgumentParser(description='Luxtronik Logger Service')
    parser.add_argument(
        '--mode',
        choices=['service', 'generate-reports', 'web'],
        default='service',
        help='Run mode: "service" for continuous logging (default), "generate-reports" for on-demand report generation, "web" for web interface only'
    )

    args = parser.parse_args()

    setup_logging()

    if args.mode == 'web':
        # Run web interface only - no config needed
        try:
            from src.web import start_web_interface
            start_web_interface(host="0.0.0.0", port=8000)
        except KeyboardInterrupt:
            print("Web interface stopped.")
            sys.exit(0)
        except Exception as e:
            logging.error(f"Web interface failed: {str(e)}")
            sys.exit(1)
    else:
        # For service and generate-reports modes, we need full config
        # Load configuration
        config = Config()
        config.load()

        if args.mode == 'generate-reports':
            # Generate reports on demand
            service = LuxLoggerService(config)
            try:
                service.generate_reports_on_demand()
                print("On-demand report generation completed successfully.")
                sys.exit(0)
            except Exception as e:
                logging.error(f"On-demand report generation failed: {str(e)}")
                sys.exit(1)
        else:
            # Run as service (default behavior)
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
