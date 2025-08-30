#!/bin/bash

# Script to run both the Luxtronik logger service and web interface together

# Function to handle cleanup on exit
cleanup() {
    echo "Stopping services..."
    # Kill all background processes
    kill 0
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the logger service in the background
echo "Starting Luxtronik logger service..."
python main.py --mode service &
LOGGER_PID=$!

# Start the web interface in the background
echo "Starting web interface..."
python main.py --mode web &
WEB_PID=$!

echo "Logger PID: $LOGGER_PID"
echo "Web interface PID: $WEB_PID"

# Wait for all background processes
wait
