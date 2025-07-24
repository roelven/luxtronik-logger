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

# Create data and logs directories
RUN mkdir -p /app/data/daily /app/data/weekly /app/logs

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST="192.168.20.180"
ENV PORT=8889
ENV INTERVAL_SEC=30
ENV CSV_TIME="07:00"
ENV CACHE_PATH="/app/data/cache.db"
ENV OUTPUT_DIRS_DAILY="/app/data/daily"
ENV OUTPUT_DIRS_WEEKLY="/app/data/weekly"

# Run the application
CMD ["python", "main.py"]