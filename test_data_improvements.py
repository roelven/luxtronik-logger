#!/usr/bin/env python3
"""
Comprehensive test script to validate data collection improvements.

This script tests the enhanced data collection methods, validation,
and debugging capabilities implemented to fix CSV generation issues.
"""

import os
import sys
import time
import json
import logging
import tempfile
import shutil
from datetime import datetime, timedelta

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_enhanced_data_collection():
    """Test the improved data collection methods"""
    print("🧪 TEST 1: Enhanced Data Collection Methods")
    print("=" * 50)

    try:
        from client import HeatPumpClient

        # Create client with debug logging
        client = HeatPumpClient("192.168.20.180", 8889)
        client.logger.setLevel(logging.DEBUG)

        print("Connecting to heat pump...")
        if not client.connect():
            print("❌ Connection failed")
            return False

        print("✅ Connection successful")
        print("Testing data collection methods...")

        # Test data collection
        start_time = time.time()
        sensor_data = client.get_all_sensors()
        collection_time = time.time() - start_time

        print(f"✅ Data collection completed in {collection_time:.2f}s")
        print(f"📊 Sensor readings collected: {len(sensor_data)}")

        if len(sensor_data) < 20:
            print("❌ WARNING: Low sensor count - expected 50+ readings")
            print("   This may indicate incomplete data collection")
            return False
        elif len(sensor_data) < 50:
            print("⚠️  WARNING: Moderate sensor count - expected 50+ readings")
            print("   Some sensors may not be available")
        else:
            print("✅ GOOD: 50+ sensor readings collected")

        # Show sample data
        print("\n📋 Sample sensor data (first 5 items):")
        sample_items = list(sensor_data.items())[:5]
        for key, value in sample_items:
            print(f"   {key}: {value}")

        # Check for critical sensors
        critical_sensors = ['temperature', 'flow', 'pressure']
        found_sensors = {}

        for sensor_type in critical_sensors:
            found = [key for key in sensor_data.keys() if sensor_type in key.lower()]
            found_sensors[sensor_type] = len(found)
            print(f"   {sensor_type.capitalize()} sensors: {len(found)}")

        # Validate we have at least some temperature sensors
        if found_sensors['temperature'] < 2:
            print("❌ ERROR: Insufficient temperature sensors")
            return False

        print("✅ Data collection test PASSED")
        return True

    except Exception as e:
        print(f"❌ Data collection test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_validation():
    """Test the data validation functionality"""
    print("\n🧪 TEST 2: Data Validation")
    print("=" * 50)

    try:
        from validate_data import DataValidator, quick_validation

        # Test with real heat pump data
        from client import HeatPumpClient
        client = HeatPumpClient("192.168.20.180", 8889)
        if client.connect():
            sample_data = client.get_all_sensors()
            print(f"Using real heat pump data with {len(sample_data)} sensor readings")
        else:
            print("❌ Failed to connect to heat pump for real data test")
            return False

        # Test quick validation
        print("Testing quick validation...")
        is_valid_quick = quick_validation(sample_data)
        print(f"Quick validation result: {'✅ PASS' if is_valid_quick else '❌ FAIL'}")

        # Test comprehensive validation
        print("Testing comprehensive validation...")
        validator = DataValidator()
        is_valid, messages = validator.validate_sensor_data(sample_data, datetime.now())

        print(f"Comprehensive validation result: {'✅ PASS' if is_valid else '❌ FAIL'}")
        print("Validation messages:")
        for message in messages:
            print(f"   {message}")

        # Test with insufficient data
        print("\nTesting with insufficient data...")
        bad_data = {"single_sensor": 25.0}
        is_valid_bad, bad_messages = validator.validate_sensor_data(bad_data, datetime.now())
        print(f"Bad data validation: {'✅ PASS' if not is_valid_bad else '❌ FAIL'}")

        if not is_valid_bad:
            print("✅ Correctly rejected insufficient data")
        else:
            print("❌ Should have rejected insufficient data")
            return False

        print("✅ Data validation test PASSED")
        return True

    except Exception as e:
        print(f"❌ Data validation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_storage_with_validation():
    """Test storage with data validation"""
    print("\n🧪 TEST 3: Storage with Validation")
    print("=" * 50)

    try:
        from storage import DataStorage

        # Create temporary storage
        temp_dir = tempfile.mkdtemp()
        cache_path = os.path.join(temp_dir, "test_cache.db")

        print(f"Using temporary cache: {cache_path}")

        # Create storage with validation enabled
        storage = DataStorage(cache_path, enable_validation=True)

        # Test with real heat pump data
        from client import HeatPumpClient
        client = HeatPumpClient("192.168.20.180", 8889)
        if client.connect():
            good_data = client.get_all_sensors()
            print(f"Using real heat pump data with {len(good_data)} sensor readings")
        else:
            print("❌ Failed to connect to heat pump for storage test")
            return False

        print("Testing storage with valid data...")
        is_valid, messages = storage.add(datetime.now(), good_data)
        success_count, total_count = storage.flush()

        print(f"Storage result: {success_count}/{total_count} data points stored")
        print(f"Validation: {'✅ PASS' if is_valid else '❌ FAIL'}")

        # Test with bad data
        bad_data = {"single_sensor": 25.0}
        print("Testing storage with invalid data...")
        is_valid_bad, bad_messages = storage.add(datetime.now(), bad_data)
        success_count_bad, total_count_bad = storage.flush()

        print(f"Bad data storage: {success_count_bad}/{total_count_bad} data points stored")
        print(f"Bad data validation: {'✅ PASS' if not is_valid_bad else '❌ FAIL'}")

        # Cleanup
        shutil.rmtree(temp_dir)

        if success_count == 1 and success_count_bad == 0:
            print("✅ Storage validation test PASSED")
            return True
        else:
            print("❌ Storage validation test FAILED")
            return False

    except Exception as e:
        print(f"❌ Storage validation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_debug_script():
    """Test the debug script functionality"""
    print("\n🧪 TEST 4: Debug Script")
    print("=" * 50)

    try:
        # Import and test debug functionality
        from debug_heatpump import HeatPumpDebugger

        debugger = HeatPumpDebugger("192.168.20.180", 8889)

        print("Testing debugger connection...")
        connected = debugger.connect_with_diagnostics()

        if not connected:
            print("❌ Debugger connection failed")
            return False

        print("✅ Debugger connection successful")
        print("Testing data inspection...")

        # Test data inspection
        all_data = debugger.inspect_all_data_methods()

        if not all_data:
            print("❌ Data inspection failed")
            return False

        print("✅ Data inspection successful")
        print("Testing data validation...")

        # Test data validation
        is_complete = debugger.validate_data_completeness(all_data)

        print(f"Data completeness: {'✅ PASS' if is_complete else '⚠️  WARNING'}")

        # Test report generation
        print("Testing report generation...")
        debugger.generate_detailed_report(all_data, "test_debug_report.json")

        if os.path.exists("test_debug_report.json"):
            print("✅ Debug report generated successfully")
            os.remove("test_debug_report.json")
        else:
            print("❌ Debug report generation failed")
            return False

        print("✅ Debug script test PASSED")
        return True

    except Exception as e:
        print(f"❌ Debug script test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all improvement tests"""
    print("🔥 COMPREHENSIVE DATA COLLECTION IMPROVEMENT TESTS")
    print("=" * 70)
    print()

    test_results = []

    # Run all tests
    test_results.append(("Enhanced Data Collection", test_enhanced_data_collection()))
    test_results.append(("Data Validation", test_data_validation()))
    test_results.append(("Storage with Validation", test_storage_with_validation()))
    test_results.append(("Debug Script", test_debug_script()))

    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    all_passed = True
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if not result:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("🎉 ALL TESTS PASSED! Data collection improvements are working correctly.")
        print("\n💡 NEXT STEPS:")
        print("1. Run the debug script for detailed analysis: python debug_heatpump.py")
        print("2. Test with live heat pump: python tests/test_live_heatpump.py")
        print("3. Generate CSV reports: python main.py --mode generate-reports")
    else:
        print("⚠️  SOME TESTS FAILED. Review the output above for issues.")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check heat pump connectivity")
        print("2. Verify python-luxtronik installation")
        print("3. Run debug script: python debug_heatpump.py")

    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
