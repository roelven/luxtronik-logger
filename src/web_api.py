import sqlite3
import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import uvicorn
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Luxtronik Logger API", version="1.0.0")

# Configuration - using same paths as main logger
DB_PATH = "data/cache.db"
REPORTS_BASE_DIR = "data/reports"
DAILY_REPORTS_DIR = os.path.join(REPORTS_BASE_DIR, "daily")
WEEKLY_REPORTS_DIR = os.path.join(REPORTS_BASE_DIR, "weekly")

def get_latest_sensor_data() -> Dict:
    """Get the latest sensor data from the database"""
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database not found")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get the latest record
        cursor.execute("SELECT timestamp, data_json FROM sensor_data ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="No sensor data found")

        timestamp, data_json = row
        data = json.loads(data_json)

        # Extract key metrics
        status_data = {
            "timestamp": datetime.fromtimestamp(timestamp).isoformat(),
            "flow_temperature": data.get("calculations.ID_WEB_Temperatur_TVL"),
            "return_temperature": data.get("calculations.ID_WEB_Temperatur_TRL"),
            "ambient_temperature": data.get("calculations.ID_WEB_Temperatur_TA"),
            "hot_water_temperature": data.get("calculations.ID_WEB_Temperatur_TBW"),
            "system_flags": {
                "pump_active": data.get("calculations.ID_WEB_Zustand_Pumpe"),
                "heating_active": data.get("calculations.ID_WEB_Zustand_HZ"),
                "hot_water_active": data.get("calculations.ID_WEB_Zustand_BW"),
                "error_state": data.get("calculations.ID_WEB_ErrorState")
            }
        }

        conn.close()
        return status_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read database: {str(e)}")

def get_csv_reports() -> Dict:
    """Get list of available CSV reports"""
    reports = {
        "daily_reports": [],
        "weekly_reports": [],
        "total_size": 0
    }

    # Ensure directories exist
    os.makedirs(DAILY_REPORTS_DIR, exist_ok=True)
    os.makedirs(WEEKLY_REPORTS_DIR, exist_ok=True)

    # Get daily reports
    daily_files = glob.glob(os.path.join(DAILY_REPORTS_DIR, "*.csv"))
    for file_path in daily_files:
        stat = os.stat(file_path)
        reports["daily_reports"].append({
            "filename": os.path.basename(file_path),
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })
        reports["total_size"] += stat.st_size

    # Get weekly reports
    weekly_files = glob.glob(os.path.join(WEEKLY_REPORTS_DIR, "*.csv"))
    for file_path in weekly_files:
        stat = os.stat(file_path)
        reports["weekly_reports"].append({
            "filename": os.path.basename(file_path),
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })
        reports["total_size"] += stat.st_size

    return reports

@app.get("/status")
async def get_status():
    """Get latest heat pump status"""
    return get_latest_sensor_data()

@app.get("/reports")
async def get_reports():
    """Get list of available CSV reports"""
    return get_csv_reports()

@app.get("/download/{report_type}/{filename}")
async def download_report(report_type: str, filename: str):
    """Download a CSV report file"""
    # Validate report type
    if report_type not in ["daily", "weekly"]:
        raise HTTPException(status_code=400, detail="Invalid report type")

    # Validate filename (prevent directory traversal)
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Construct file path
    if report_type == "daily":
        file_path = os.path.join(DAILY_REPORTS_DIR, filename)
    else:  # weekly
        file_path = os.path.join(WEEKLY_REPORTS_DIR, filename)

    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Return file response
    return FileResponse(file_path, media_type='text/csv', filename=filename)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Luxtronik Logger API",
        "endpoints": {
            "status": "/status",
            "reports": "/reports",
            "download": "/download/{report_type}/{filename}"
        }
    }

def start_api_server(host="0.0.0.0", port=8000):
    """Start the API server"""
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    start_api_server()
