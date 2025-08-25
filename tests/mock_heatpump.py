#!/usr/bin/env python3
"""
Mock heat pump server for testing the Luxtronik logger.

This script simulates a heat pump server that responds to Luxtronik protocol requests.
It's used for testing the logger without requiring actual hardware.
"""

import socket
import struct
import time
import threading
import random
from datetime import datetime

class MockHeatPumpServer:
    def __init__(self, host='localhost', port=8889):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        self.connections = 0

        # Sample sensor data that mimics a real heat pump
        self.calculations = {
            'ID_WEB_Temperatur_TVL': 35.0 + random.uniform(-2, 2),  # Flow temperature
            'ID_WEB_Temperatur_TRL': 32.0 + random.uniform(-2, 2),  # Return temperature
            'ID_WEB_Speicheristtemp': 45.0 + random.uniform(-3, 3), # Storage temperature
            'ID_WEB_Temperatur_TA': 15.0 + random.uniform(-5, 5),   # Outside temperature
            'ID_WEB_Temperatur_THG': 25.0 + random.uniform(-2, 2),  # Heat source temperature
            'ID_WEB_Temperatur_TBW': 40.0 + random.uniform(-2, 2),  # Hot water temperature
            'ID_WEB_HEIZEN': 1,                                     # Heating mode
            'ID_WEB_WARMWASSER': 1,                                 # Hot water mode
            'ID_WEB_ABSENKEN': 0,                                   # Reduced mode
            'ID_WEB_Adapterkennung': 1,                             # Adapter ID
            'ID_WEB_Adapterfirmware': 100,                          # Adapter firmware
            'ID_WEB_Adapterstatus': 1,                              # Adapter status
        }

        self.parameters = {
            'ID_WEB_Temperatur_TVL_Soll': 35.0,                     # Flow set temperature
            'ID_WEB_Temperatur_TRL_Soll': 32.0,                     # Return set temperature
            'ID_WEB_Speicher_Soll': 45.0,                           # Storage set temperature
            'ID_WEB_Temperatur_TA_Einfluss': 0.5,                   # Outside temperature influence
            'ID_WEB_Heizungstemp_Max': 60.0,                        # Max heating temperature
            'ID_WEB_Heizungstemp_Min': 20.0,                        # Min heating temperature
            'ID_WEB_Pumpenstatus': 1,                               # Pump status
            'ID_WEB_Comfort': 1,                                    # Comfort mode
        }

        self.visibilities = {
            'ID_WEB_Vis_Temp_Vorlauf': 1,                           # Flow temperature visibility
            'ID_WEB_Vis_Temp_Ruecklauf': 1,                         # Return temperature visibility
            'ID_WEB_Vis_Temp_Speicher': 1,                          # Storage temperature visibility
            'ID_WEB_Vis_Temp_Aussen': 1,                            # Outside temperature visibility
            'ID_WEB_Vis_Temp_Brauchwasser': 1,                      # Hot water temperature visibility
        }

    def update_sensor_data(self):
        """Update sensor data with realistic variations"""
        # Simulate gradual temperature changes
        self.calculations['ID_WEB_Temperatur_TVL'] += random.uniform(-0.5, 0.5)
        self.calculations['ID_WEB_Temperatur_TRL'] += random.uniform(-0.5, 0.5)
        self.calculations['ID_WEB_Speicheristtemp'] += random.uniform(-0.3, 0.3)
        self.calculations['ID_WEB_Temperatur_TA'] += random.uniform(-0.2, 0.2)

        # Keep temperatures within realistic ranges
        self.calculations['ID_WEB_Temperatur_TVL'] = max(10, min(60, self.calculations['ID_WEB_Temperatur_TVL']))
        self.calculations['ID_WEB_Temperatur_TRL'] = max(10, min(55, self.calculations['ID_WEB_Temperatur_TRL']))
        self.calculations['ID_WEB_Speicheristtemp'] = max(20, min(65, self.calculations['ID_WEB_Speicheristtemp']))
        self.calculations['ID_WEB_Temperatur_TA'] = max(-20, min(40, self.calculations['ID_WEB_Temperatur_TA']))

    def handle_client(self, client_socket, address):
        """Handle a client connection"""
        print(f"Mock heat pump: Connection from {address}")
        self.connections += 1

        try:
            while self.running:
                # Receive command
                command_data = client_socket.recv(4)
                if not command_data:
                    break

                command = struct.unpack('!I', command_data)[0]
                print(f"Mock heat pump: Received command {command}")

                # Handle different commands
                if command == 3004:  # Read calculations
                    response = self.handle_read_calculations()
                elif command == 3005:  # Read parameters
                    response = self.handle_read_parameters()
                elif command == 3006:  # Read visibilities
                    response = self.handle_read_visibilities()
                else:
                    print(f"Mock heat pump: Unknown command {command}")
                    response = struct.pack('!I', 0)  # Empty response

                # Send response
                client_socket.send(response)

                # Update data for next request
                self.update_sensor_data()

        except Exception as e:
            print(f"Mock heat pump: Error handling client {address}: {e}")
        finally:
            client_socket.close()
            print(f"Mock heat pump: Connection from {address} closed")

    def handle_read_calculations(self):
        """Handle read calculations command"""
        # Pack calculations data
        data = b''
        for i, (key, value) in enumerate(self.calculations.items()):
            # Pack as float
            data += struct.pack('!f', float(value))

        # Prepend length
        response = struct.pack('!I', len(data)) + data
        return response

    def handle_read_parameters(self):
        """Handle read parameters command"""
        # Pack parameters data
        data = b''
        for i, (key, value) in enumerate(self.parameters.items()):
            # Pack as float
            data += struct.pack('!f', float(value))

        # Prepend length
        response = struct.pack('!I', len(data)) + data
        return response

    def handle_read_visibilities(self):
        """Handle read visibilities command"""
        # Pack visibilities data
        data = b''
        for i, (key, value) in enumerate(self.visibilities.items()):
            # Pack as integer
            data += struct.pack('!I', int(value))

        # Prepend length
        response = struct.pack('!I', len(data)) + data
        return response

    def start(self):
        """Start the mock heat pump server"""
        print(f"Mock heat pump: Starting server on {self.host}:{self.port}")

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind to all interfaces to make it accessible from Docker containers
            bind_host = '0.0.0.0' if self.host == 'localhost' else self.host
            self.server_socket.bind((bind_host, self.port))
            self.server_socket.listen(5)

            self.running = True
            print(f"Mock heat pump: Server listening on {bind_host}:{self.port}")
        except Exception as e:
            print(f"Mock heat pump: Failed to start server: {e}")
            return

        try:
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)  # Timeout to allow checking self.running
                    client_socket, address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"Mock heat pump: Error accepting connections: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the mock heat pump server"""
        print("Mock heat pump: Stopping server")
        self.running = False

        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None

        print("Mock heat pump: Server stopped")

def main():
    """Main function to run the mock heat pump server"""
    import argparse

    parser = argparse.ArgumentParser(description='Mock Heat Pump Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8889, help='Port to listen on')

    args = parser.parse_args()

    server = MockHeatPumpServer(args.host, args.port)

    try:
        server.start()
    except KeyboardInterrupt:
        print("\nMock heat pump: Received interrupt signal")
    finally:
        server.stop()

if __name__ == "__main__":
    main()
