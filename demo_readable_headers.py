#!/usr/bin/env python3
"""
Demo script to show readable CSV headers feature in action.

This script demonstrates how the readable headers feature works by:
1. Creating sample sensor data with raw Luxtronik IDs
2. Generating CSV files with readable headers enabled
3. Showing the difference between raw and readable sensor names
"""

import os
import sys
import csv
from datetime import datetime

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from csvgen import CSVGenerator

def demo_readable_headers():
    """Demonstrate readable CSV headers feature"""
    print("📊 Luxtronik Logger - Readable CSV Headers Demo")
    print("=" * 50)

    # Create temporary output directories
    output_dir = "demo_output"
    daily_dir = os.path.join(output_dir, "daily")
    weekly_dir = os.path.join(output_dir, "weekly")
    os.makedirs(daily_dir, exist_ok=True)
    os.makedirs(weekly_dir, exist_ok=True)

    # Sample sensor data with raw Luxtronik IDs
    sample_data = [
        {
            "timestamp": datetime.now(),
            "data": {
                "calculations.ID_WEB_Temperatur_TVL": 42.5,
                "calculations.ID_WEB_Temperatur_TRL": 38.2,
                "calculations.ID_WEB_Temperatur_TA": 21.8,
                "calculations.ID_WEB_Temperatur_TBW": 48.0,
                "calculations.ID_WEB_Zaehler_BetrZeitVD1": 12500,
                "calculations.ID_WEB_Zaehler_BetrZeitWP": 8750,
                "parameters.ID_Soll_BWS_akt": 50.0,
                "parameters.ID_Ba_Hz_akt": "Automatic",
                "visibilities.ID_Visi_Heizung": 1,
                "visibilities.ID_Visi_Brauwasser": 1,
            }
        }
    ]

    output_dirs = {"daily": daily_dir, "weekly": weekly_dir}

    print("\n📝 Generating CSV with readable headers (READABLE_HEADERS=true)...")
    # Generate CSV with readable headers
    os.environ["READABLE_HEADERS"] = "true"
    generator = CSVGenerator(output_dirs)
    filepath = generator.generate_daily_csv(sample_data, datetime.now())

    print("\n📄 CSV Content Generated:")
    print("-" * 30)

    # Show the CSV content
    print("\n📋 CSV with Readable Headers:")
    with open(filepath, 'r') as f:
        content = f.read()
        print(content)

    print("\n📝 Explanation:")
    print("The CSV above shows human-readable sensor names like 'Flow Temperature' instead of")
    print("raw sensor IDs like 'calculations.ID_WEB_Temperatur_TVL'. This makes the data")
    print("much easier to understand and work with in spreadsheet applications.")

    print("✅ Demo completed successfully!")
    print(f"📁 Output file saved to: {os.path.abspath(filepath)}")

    # Clean up demo files
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
        os.rmdir(daily_dir)
        os.rmdir(weekly_dir)
        os.rmdir(output_dir)
        print("🧹 Cleaned up demo files")
    except Exception as e:
        print(f"Note: Some demo files may need manual cleanup: {e}")

if __name__ == "__main__":
    demo_readable_headers()
