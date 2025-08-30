import sqlite3
import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import nicegui

# Initialize FastAPI app
app = FastAPI(title="Luxtronik Logger Web Interface", version="1.0.0")

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

    # Validate filename (prevent directory traversal) - do this BEFORE constructing file path
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

# Create NiceGUI interface
@nicegui.ui.page('/')
def main_page():
    """Main dashboard page"""
    from nicegui import ui

    # Header
    with ui.header().classes('justify-between'):
        ui.label('Luxtronik Logger Dashboard').classes('text-h6')
        ui.button('Refresh', on_click=lambda: ui.notify('Status refreshed!')).props('flat')

    # Status panel
    with ui.card().classes('w-full'):
        ui.label('Current Status').classes('text-h6')

        # Temperature readings
        with ui.row().classes('w-full'):
            with ui.column():
                ui.label('Flow Temperature').classes('text-subtitle2')
                flow_temp_label = ui.label('-- °C').classes('text-h4')

            with ui.column():
                ui.label('Return Temperature').classes('text-subtitle2')
                return_temp_label = ui.label('-- °C').classes('text-h4')

            with ui.column():
                ui.label('Ambient Temperature').classes('text-subtitle2')
                ambient_temp_label = ui.label('-- °C').classes('text-h4')

        # System flags
        with ui.row().classes('w-full'):
            ui.label('System Status').classes('text-subtitle2')
            status_flags_label = ui.label('Loading...').classes('text-body1')

    # Reports section
    with ui.card().classes('w-full'):
        ui.label('Available Reports').classes('text-h6')
        reports_table = ui.table(columns=[
            {'name': 'filename', 'label': 'Filename', 'field': 'filename'},
            {'name': 'size', 'label': 'Size', 'field': 'size'},
            {'name': 'modified', 'label': 'Modified', 'field': 'modified'},
            {'name': 'actions', 'label': 'Actions', 'field': 'actions'}
        ], rows=[]).classes('w-full')

    # Load initial data
    def update_status():
        """Update status display with latest data"""
        try:
            status_data = get_latest_sensor_data()
            flow_temp_label.set_text(f"{status_data['flow_temperature']:.1f} °C" if status_data['flow_temperature'] is not None else '-- °C')
            return_temp_label.set_text(f"{status_data['return_temperature']:.1f} °C" if status_data['return_temperature'] is not None else '-- °C')
            ambient_temp_label.set_text(f"{status_data['ambient_temperature']:.1f} °C" if status_data['ambient_temperature'] is not None else '-- °C')

            # Update system flags
            flags = status_data['system_flags']
            flags_text = f"Pump: {'ON' if flags['pump_active'] else 'OFF'} | "
            flags_text += f"Heating: {'ON' if flags['heating_active'] else 'OFF'} | "
            flags_text += f"Hot Water: {'ON' if flags['hot_water_active'] else 'OFF'}"
            if flags['error_state']:
                flags_text += f" | ERROR: {flags['error_state']}"
            status_flags_label.set_text(flags_text)
        except Exception as e:
            ui.notify(f"Failed to update status: {str(e)}")

    def update_reports():
        """Update reports table"""
        try:
            reports_data = get_csv_reports()
            rows = []

            # Add daily reports
            for report in reports_data['daily_reports']:
                rows.append({
                    'filename': report['filename'],
                    'size': f"{report['size_bytes'] / 1024:.1f} KB",
                    'modified': report['modified'],
                    'actions': f"[Download](/download/daily/{report['filename']})"
                })

            # Add weekly reports
            for report in reports_data['weekly_reports']:
                rows.append({
                    'filename': report['filename'],
                    'size': f"{report['size_bytes'] / 1024:.1f} KB",
                    'modified': report['modified'],
                    'actions': f"[Download](/download/weekly/{report['filename']})"
                })

            reports_table.rows = rows
            reports_table.update()
        except Exception as e:
            ui.notify(f"Failed to update reports: {str(e)}")

    # Initial load
    update_status()
    update_reports()

    # Auto-refresh every 30 seconds
    ui.timer(30, update_status)
    ui.timer(60, update_reports)

def start_web_interface(port: int = 8000):
    """Start the web interface"""
    # Ensure reports directories exist
    os.makedirs(DAILY_REPORTS_DIR, exist_ok=True)
    os.makedirs(WEEKLY_REPORTS_DIR, exist_ok=True)

    # Start NiceGUI
    nicegui.ui.run(host='0.0.0.0', port=port, show=False, reload=False, title="Luxtronik Logger Dashboard")

if __name__ == "__main__":
    start_web_interface()
