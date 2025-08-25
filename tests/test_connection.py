#!/usr/bin/env python3
"""
Simple connection test script to verify the mock heat pump is working.
"""

import socket
import struct
import time

def test_connection():
    """Test connection to the mock heat pump"""
    try:
        # Connect to the mock heat pump
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        print("Connecting to localhost:8889...")
        sock.connect(('localhost', 8889))
        print("Connected successfully!")

        # Send a test command (read calculations = 3004)
        command = struct.pack('!I', 3004)
        sock.send(command)
        print("Sent read calculations command")

        # Receive response
        length_data = sock.recv(4)
        if not length_data:
            print("No response received")
            return False

        length = struct.unpack('!I', length_data)[0]
        print(f"Response length: {length} bytes")

        if length > 0:
            data = sock.recv(length)
            print(f"Received {len(data)} bytes of data")

        sock.close()
        print("Connection test successful!")
        return True

    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
