# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create data and logs directories
RUN mkdir -p /app/data/daily /app/data/weekly /app/logs

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=""
ENV PORT=8888
ENV INTERVAL_SEC=30
ENV CSV_TIME="07:00"
ENV CACHE_PATH="/app/data/cache.db"
ENV OUTPUT_DIRS='{"daily": "/app/data/daily", "weekly": "/app/data/weekly"}'

# Run the application
CMD ["python", "main.py"]