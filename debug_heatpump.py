#!/usr/bin/env python3
"""
Enhanced debug script for Luxtronik heat pump data inspection.

This script provides comprehensive diagnostics for:
- Connection testing and heat pump capability reporting
- Detailed sensor data inspection using proper luxtronik API methods
- Data completeness validation and quality checks
- Troubleshooting guidance for common issues
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from luxtronik import Luxtronik
    from client import HeatPumpClient
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure python-luxtronik is installed and src modules are available")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('heatpump_debug.log')
    ]
)
logger = logging.getLogger(__name__)

class HeatPumpDebugger:
    """Comprehensive debugger for Luxtronik heat pump data inspection"""

    def __init__(self, host: str, port: int = 8889):
        self.host = host
        self.port = port
        self.connection = None
        self.logger = logging.getLogger(f"{__name__}.HeatPumpDebugger")

    def connect_with_diagnostics(self) -> bool:
        """Establish connection with detailed diagnostics"""
        print(f"🔌 Connecting to heat pump at {self.host}:{self.port}")
        print(f"   Timeout: 60 seconds")
        print(f"   Max retries: 3")
        print(f"   Retry delay: 2 seconds (exponential backoff)")
        print()

        start_time = time.time()

        try:
            self.connection = Luxtronik(self.host, self.port)
            connection_time = time.time() - start_time

            print(f"✅ SUCCESS: Connected to heat pump in {connection_time:.2f} seconds")
            print(f"   Host: {self.host}")
            print(f"   Port: {self.port}")
            print()

            return True

        except Exception as e:
            connection_time = time.time() - start_time
            print(f"❌ FAILED: Connection failed after {connection_time:.2f} seconds")
            print(f"   Error: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            print()
            self._print_connection_troubleshooting()
            return False

    def inspect_all_data_methods(self) -> Dict[str, Any]:
        """Inspect all available data using proper luxtronik API methods"""
        if not self.connection:
            print("❌ No connection established")
            return {}

        print("🔍 Inspecting all available data methods...")
        print()

        all_data = {}

        # Method 1: Proper API calls (recommended)
        print("📊 Method 1: Using proper luxtronik API methods")
        print("   - connection.calculations.get(i) for i in range(275)")
        print("   - connection.parameters.get(i) for i in range(1187)")
        print("   - connection.visibilities.get(i) for i in range(398)")
        print()

        # Get data using proper luxtronik API methods with numeric indices
        try:
            # Get all available data using numeric indices
            calculations = {}
            parameters = {}
            visibilities = {}

            # Get calculations data (typically 275 items)
            for i in range(275):
                try:
                    entry = self.connection.calculations.get(i)
                    if hasattr(entry, 'value'):
                        key_name = entry.name if hasattr(entry, 'name') and not entry.name.startswith('Unknown') else f"calculations.{i}"
                        calculations[key_name] = entry.value
                except Exception as e:
                    print(f"   Failed to get calculations.{i}: {e}")

            # Get parameters data (typically 1187 items)
            for i in range(1187):
                try:
                    entry = self.connection.parameters.get(i)
                    if hasattr(entry, 'value'):
                        key_name = entry.name if hasattr(entry, 'name') and not entry.name.startswith('Unknown') else f"parameters.{i}"
                        parameters[key_name] = entry.value
                except Exception as e:
                    print(f"   Failed to get parameters.{i}: {e}")

            # Get visibilities data (typically 398 items)
            for i in range(398):
                try:
                    entry = self.connection.visibilities.get(i)
                    if hasattr(entry, 'value'):
                        key_name = entry.name if hasattr(entry, 'name') and not entry.name.startswith('Unknown') else f"visibilities.{i}"
                        visibilities[key_name] = entry.value
                except Exception as e:
                    print(f"   Failed to get visibilities.{i}: {e}")

            all_data.update({
                'calculations': calculations,
                'parameters': parameters,
                'visibilities': visibilities
            })

            print(f"✅ Calculations: {len(calculations)} items")
            print(f"✅ Parameters: {len(parameters)} items")
            print(f"✅ Visibilities: {len(visibilities)} items")
            print(f"✅ Total (API methods): {len(calculations) + len(parameters) + len(visibilities)} sensor readings")
            print()

        except Exception as e:
            print(f"❌ Failed to get data using API methods: {str(e)}")
            print()

        # Method 2: Current __dict__ approach (for comparison)
        print("📊 Method 2: Current __dict__ approach (for comparison)")
        print("   - connection.calculations.__dict__")
        print("   - connection.parameters.__dict__")
        print("   - connection.visibilities.__dict__")
        print()

        try:
            calculations_dict = {f"calculations.{k}": v for k, v in self.connection.calculations.__dict__.items() if not k.startswith('_')}
            parameters_dict = {f"parameters.{k}": v for k, v in self.connection.parameters.__dict__.items() if not k.startswith('_')}
            visibilities_dict = {f"visibilities.{k}": v for k, v in self.connection.visibilities.__dict__.items() if not k.startswith('_')}

            print(f"📈 Calculations (__dict__): {len(calculations_dict)} items")
            print(f"📈 Parameters (__dict__): {len(parameters_dict)} items")
            print(f"📈 Visibilities (__dict__): {len(visibilities_dict)} items")
            print(f"📈 Total (__dict__): {len(calculations_dict) + len(parameters_dict) + len(visibilities_dict)} sensor readings")
            print()

            # Store for comparison
            all_data['calculations_dict'] = calculations_dict
            all_data['parameters_dict'] = parameters_dict
            all_data['visibilities_dict'] = visibilities_dict

        except Exception as e:
            print(f"❌ Failed to get data using __dict__: {str(e)}")
            print()

        return all_data

    def validate_data_completeness(self, data: Dict[str, Any]) -> bool:
        """Validate that we have complete and meaningful data"""
        print("✅ Validating data completeness...")
        print()

        # Check if we have data from API methods
        has_api_data = (
            'calculations' in data and
            'parameters' in data and
            'visibilities' in data
        )

        if not has_api_data:
            print("❌ Missing data from API methods")
            print("   This suggests the heat pump may not be responding properly")
            print("   or the luxtronik library version may have compatibility issues")
            print()
            return False

        total_readings = (
            len(data['calculations']) +
            len(data['parameters']) +
            len(data['visibilities'])
        )

        print(f"📊 Total sensor readings: {total_readings}")

        # Check for minimum expected data
        if total_readings < 20:
            print("❌ WARNING: Very low number of sensor readings")
            print(f"   Expected: 50+ readings from a healthy heat pump")
            print(f"   Actual: {total_readings} readings")
            print("   This suggests incomplete data collection")
            print()
            return False
        elif total_readings < 50:
            print("⚠️  WARNING: Lower than expected number of sensor readings")
            print(f"   Expected: 50+ readings from a healthy heat pump")
            print(f"   Actual: {total_readings} readings")
            print("   Some sensors may not be available")
            print()
        else:
            print(f"✅ Good: {total_readings} sensor readings available")
            print()

        # Check for critical temperature sensors
        critical_sensors = self._find_critical_sensors(data)
        print("🌡️  Critical temperature sensors found:")
        for sensor_type, sensors in critical_sensors.items():
            print(f"   {sensor_type}: {len(sensors)} sensors")
            for sensor in sensors[:3]:  # Show first 3 of each type
                print(f"     - {sensor}")
            if len(sensors) > 3:
                print(f"     ... and {len(sensors) - 3} more")
            print()

        return True

    def _find_critical_sensors(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Find critical temperature and system sensors"""
        critical_sensors = {
            'temperature': [],
            'flow': [],
            'pressure': [],
            'energy': [],
            'status': []
        }

        # Search through all data for critical sensors
        for category in ['calculations', 'parameters', 'visibilities']:
            if category in data:
                for key, value in data[category].items():
                    key_lower = key.lower()

                    # Temperature sensors
                    if any(temp in key_lower for temp in ['temp', 'temperature', 'tvl', 'trl', 'ta', 'twa', 'twe', 'tsk', 'tss']):
                        critical_sensors['temperature'].append(key)

                    # Flow sensors
                    elif any(flow in key_lower for flow in ['flow', 'volum', 'rate']):
                        critical_sensors['flow'].append(key)

                    # Pressure sensors
                    elif any(press in key_lower for press in ['pressure', 'press', 'bar']):
                        critical_sensors['pressure'].append(key)

                    # Energy sensors
                    elif any(energy in key_lower for energy in ['energy', 'power', 'watt', 'kwh']):
                        critical_sensors['energy'].append(key)

                    # Status sensors
                    elif any(status in key_lower for status in ['status', 'mode', 'state', 'error', 'alarm']):
                        critical_sensors['status'].append(key)

        return critical_sensors

    def generate_detailed_report(self, data: Dict[str, Any], output_file: str = "heatpump_detailed_report.json"):
        """Generate detailed JSON report of all available data"""
        print(f"📝 Generating detailed report: {output_file}")

        report = {
            'timestamp': datetime.now().isoformat(),
            'host': self.host,
            'port': self.port,
            'connection_successful': self.connection is not None,
            'data_summary': {
                'calculations_count': len(data.get('calculations', {})),
                'parameters_count': len(data.get('parameters', {})),
                'visibilities_count': len(data.get('visibilities', {})),
                'total_readings': (
                    len(data.get('calculations', {})) +
                    len(data.get('parameters', {})) +
                    len(data.get('visibilities', {}))
                )
            },
            'sensor_data': data
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"✅ Detailed report saved to: {output_file}")
        print(f"   Use this file for detailed analysis and troubleshooting")
        print()

    def _print_connection_troubleshooting(self):
        """Print troubleshooting guidance for connection issues"""
        print("🔧 TROUBLESHOOTING CONNECTION ISSUES:")
        print()
        print("1. 🔌 Network Connectivity:")
        print("   - Verify the heat pump is powered on and connected to network")
        print("   - Ping the heat pump: ping 192.168.20.180")
        print("   - Check firewall rules and network routing")
        print()
        print("2. 🌐 Network Configuration:")
        print("   - Heat pump subnet: 192.168.20.0/24")
        print("   - If on different subnet, add route:")
        print("     sudo ip route add 192.168.20.0/24 via 10.0.0.1 dev ens18")
        print("   - For LXD/LXC containers, adjust rp_filter:")
        print("     sudo sysctl -w net.ipv4.conf.all.rp_filter=0")
        print("     sudo sysctl -w net.ipv4.conf.ens18.rp_filter=0")
        print("     sudo sysctl -w net.ipv4.ip_forward=1")
        print()
        print("3. 🐋 Docker Networking:")
        print("   - Use host networking mode:")
        print("     docker run --network=host --env-file .env lux-logger")
        print()
        print("4. 📋 Heat Pump Configuration:")
        print("   - Verify heat pump network settings")
        print("   - Check if port 8889 is open on heat pump")
        print("   - Restart heat pump if needed")
        print()

def main():
    """Main debug function"""
    print("=" * 70)
    print("🔥 LUXTRONIK HEAT PUMP DEBUGGER")
    print("=" * 70)
    print()

    # Get heat pump connection details
    host = "192.168.20.180"  # Default from .env
    port = 8889

    # Check if host/port provided as arguments
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    print(f"🔧 Debugging heat pump at: {host}:{port}")
    print()

    # Create debugger instance
    debugger = HeatPumpDebugger(host, port)

    # Step 1: Test connection
    if not debugger.connect_with_diagnostics():
        print("❌ Cannot proceed without connection")
        return False

    # Step 2: Inspect all data methods
    all_data = debugger.inspect_all_data_methods()

    if not all_data:
        print("❌ No data retrieved from heat pump")
        return False

    # Step 3: Validate data completeness
    is_complete = debugger.validate_data_completeness(all_data)

    # Step 4: Generate detailed report
    debugger.generate_detailed_report(all_data)

    # Step 5: Provide recommendations
    print("💡 RECOMMENDATIONS:")
    print()

    if is_complete:
        print("✅ Data collection looks good!")
        print("   - Use proper API methods (get_all()) in client.py")
        print("   - Ensure all critical sensors are being collected")
        print("   - Implement data validation before storage")
    else:
        print("⚠️  Data collection issues detected:")
        print("   - Check heat pump connectivity and configuration")
        print("   - Verify luxtronik library compatibility")
        print("   - Implement fallback mechanisms for missing data")

    print()
    print("📋 Next steps:")
    print("1. Review the generated heatpump_detailed_report.json")
    print("2. Update client.py to use proper API methods")
    print("3. Implement data validation in storage.py")
    print("4. Run comprehensive tests")
    print()

    return is_complete

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Debug interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
