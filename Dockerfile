# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies including networking tools for debugging
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    git \
    telnet \
    netcat-openbsd \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Install luxtronik from submodule to ensure correct version
RUN pip uninstall -y luxtronik && pip install -e ./python-luxtronik

# Create data and reports directories
RUN mkdir -p /app/data/reports/daily /app/data/reports/weekly /app/logs

# Make entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST="192.168.20.180"
ENV PORT=8889
ENV INTERVAL_SEC=30
ENV CSV_TIME="07:00"
ENV CACHE_PATH="/app/data/cache.db"
ENV OUTPUT_DIRS_DAILY="/app/data/reports/daily"
ENV OUTPUT_DIRS_WEEKLY="/app/data/reports/weekly"

# Expose both the logger port (for heat pump communication) and web interface port
EXPOSE 8889 8000

# Use entrypoint script to add routing
ENTRYPOINT ["/app/docker-entrypoint.sh"]
