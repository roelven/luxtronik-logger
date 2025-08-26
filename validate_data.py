#!/usr/bin/env python3
"""
Data validation module for Luxtronik heat pump data quality assurance.

This module provides comprehensive validation checks to ensure:
- Data completeness and minimum sensor requirements
- Value ranges and data type consistency
- Critical sensor presence for meaningful analysis
- Timestamp validation and sequence checking
"""

import logging
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataValidator:
    """Comprehensive data validation for heat pump sensor readings"""

    # Critical temperature sensors that should always be present
    CRITICAL_TEMPERATURE_SENSORS = {
        'temperature_flow', 'temperature_return', 'temperature_ambient',
        'temperature_water', 'temperature_source', 'temperature_solar'
    }

    # Common temperature sensor prefixes/patterns
    TEMPERATURE_PATTERNS = {
        'temp', 'temperature', 'tvl', 'trl', 'ta', 'twa', 'twe', 'tsk', 'tss'
    }

    # Expected value ranges for common sensors (in Celsius for temperatures)
    EXPECTED_RANGES = {
        'temperature': (-30, 100),  # Most temperatures should be in this range
        'flow': (0, 100),           # Flow rates in l/min
        'pressure': (0, 10),        # Pressure in bar
        'energy': (0, 10000),       # Energy/power values
    }

    def __init__(self, min_sensor_count: int = 100, min_critical_sensors: int = 10):
        """
        Initialize data validator.

        Args:
            min_sensor_count: Minimum number of sensor readings required
            min_critical_sensors: Minimum number of critical temperature sensors required
        """
        self.min_sensor_count = min_sensor_count
        self.min_critical_sensors = min_critical_sensors
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []

    def validate_sensor_data(self, sensor_data: Dict[str, float],
                           timestamp: datetime) -> Tuple[bool, List[str]]:
        """
        Validate sensor data for completeness and quality.

        Args:
            sensor_data: Dictionary of sensor readings
            timestamp: Timestamp of the data collection

        Returns:
            Tuple of (is_valid, validation_messages)
        """
        self.validation_errors.clear()
        self.validation_warnings.clear()

        # Basic validation checks
        self._validate_data_completeness(sensor_data)
        self._validate_critical_sensors(sensor_data)
        self._validate_value_ranges(sensor_data)
        self._validate_data_types(sensor_data)
        self._validate_timestamp(timestamp)

        # Compile all messages
        all_messages = self.validation_errors + self.validation_warnings

        # Data is valid if no critical errors
        is_valid = len(self.validation_errors) == 0

        return is_valid, all_messages

    def _validate_data_completeness(self, sensor_data: Dict[str, float]):
        """Validate that we have sufficient sensor data"""
        sensor_count = len(sensor_data)

        if sensor_count == 0:
            self.validation_errors.append("❌ No sensor data received")
            return

        if sensor_count < self.min_sensor_count:
            self.validation_errors.append(
                f"❌ Insufficient sensor data: {sensor_count} readings "
                f"(minimum {self.min_sensor_count} expected)"
            )
        elif sensor_count < 500:
            self.validation_warnings.append(
                f"⚠️  Low sensor count: {sensor_count} readings "
                f"(typically 1000+ expected from healthy heat pump)"
            )
        else:
            logger.debug(f"✅ Good sensor count: {sensor_count} readings")

    def _validate_critical_sensors(self, sensor_data: Dict[str, float]):
        """Validate presence of critical temperature sensors"""
        sensor_keys = set(sensor_data.keys())
        found_critical_sensors = []

        # Check for temperature sensors using flexible pattern matching
        for key in sensor_keys:
            key_lower = key.lower()
            # Check for temperature patterns in the key
            if any(pattern in key_lower for pattern in ['temp', 'temperatur', 'tv', 'tr', 'ta', 'twa', 'twe', 'tsk', 'tss']):
                found_critical_sensors.append(key)

        # Also check for temperature patterns (for warning message)
        temperature_sensors = self._find_temperature_sensors(sensor_keys)

        if len(found_critical_sensors) < self.min_critical_sensors:
            self.validation_errors.append(
                f"❌ Missing critical temperature sensors: "
                f"found {len(found_critical_sensors)} of {self.min_critical_sensors} required"
            )
            if temperature_sensors:
                self.validation_warnings.append(
                    f"   Found temperature-related sensors: {list(temperature_sensors)[:5]}..."
                )
        else:
            logger.debug(f"✅ Found {len(found_critical_sensors)} critical temperature sensors")

    def _validate_value_ranges(self, sensor_data: Dict[str, float]):
        """Validate that sensor values are within reasonable ranges"""
        outlier_count = 0
        total_checked = 0

        for sensor_name, value in sensor_data.items():
            # Skip non-numeric or invalid values
            if not isinstance(value, (int, float)):
                continue

            total_checked += 1
            sensor_type = self._classify_sensor(sensor_name)

            if sensor_type in self.EXPECTED_RANGES:
                min_val, max_val = self.EXPECTED_RANGES[sensor_type]
                if not (min_val <= value <= max_val):
                    outlier_count += 1
                    if outlier_count <= 3:  # Only log first few outliers
                        self.validation_warnings.append(
                            f"⚠️  Outlier value: {sensor_name}={value} "
                            f"(expected {min_val}-{max_val})"
                        )

        if outlier_count > 0:
            self.validation_warnings.append(
                f"⚠️  Found {outlier_count} outlier values in {total_checked} sensors"
            )

    def _validate_data_types(self, sensor_data: Dict[str, float]):
        """Validate that all values are numeric"""
        non_numeric_count = 0

        for sensor_name, value in sensor_data.items():
            if not isinstance(value, (int, float)):
                non_numeric_count += 1
                if non_numeric_count <= 3:  # Only log first few
                    self.validation_warnings.append(
                        f"⚠️  Non-numeric value: {sensor_name}={value} "
                        f"(type: {type(value).__name__})"
                    )

        if non_numeric_count > 0:
            self.validation_warnings.append(
                f"⚠️  Found {non_numeric_count} non-numeric values"
            )

    def _validate_timestamp(self, timestamp: datetime):
        """Validate timestamp is reasonable"""
        now = datetime.now()
        time_diff = abs((now - timestamp).total_seconds())

        if time_diff > 3600:  # More than 1 hour difference
            self.validation_warnings.append(
                f"⚠️  Large timestamp difference: {time_diff:.0f} seconds "
                f"(current: {now}, data: {timestamp})"
            )

    def _find_temperature_sensors(self, sensor_keys: Set[str]) -> Set[str]:
        """Find all temperature-related sensors"""
        temperature_sensors = set()

        for key in sensor_keys:
            key_lower = key.lower()
            if any(pattern in key_lower for pattern in self.TEMPERATURE_PATTERNS):
                temperature_sensors.add(key)

        return temperature_sensors

    def _classify_sensor(self, sensor_name: str) -> str:
        """Classify sensor type based on name patterns"""
        name_lower = sensor_name.lower()

        if any(pattern in name_lower for pattern in self.TEMPERATURE_PATTERNS):
            return 'temperature'
        # Additional temperature patterns including German abbreviations
        elif any(pattern in name_lower for pattern in ['temp', 'temperatur', 'tv', 'tr', 'ta', 'twa', 'twe', 'tsk', 'tss', 'idl', 'web_temp']):
            return 'temperature'
        elif any(pattern in name_lower for pattern in ['flow', 'volum', 'rate']):
            return 'flow'
        elif any(pattern in name_lower for pattern in ['pressure', 'press', 'bar']):
            return 'pressure'
        elif any(pattern in name_lower for pattern in ['energy', 'power', 'watt', 'kwh']):
            return 'energy'
        else:
            return 'unknown'

    def generate_validation_report(self, sensor_data: Dict[str, float],
                                 timestamp: datetime) -> Dict[str, any]:
        """Generate comprehensive validation report"""
        is_valid, messages = self.validate_sensor_data(sensor_data, timestamp)

        report = {
            'timestamp': timestamp.isoformat(),
            'sensor_count': len(sensor_data),
            'is_valid': is_valid,
            'errors': self.validation_errors,
            'warnings': self.validation_warnings,
            'temperature_sensors': list(self._find_temperature_sensors(set(sensor_data.keys()))),
            'sample_data': dict(list(sensor_data.items())[:5]),  # First 5 items
        }

        return report


# Utility functions for standalone validation
def validate_sensor_data_standalone(sensor_data: Dict[str, float],
                                  timestamp: Optional[datetime] = None) -> Tuple[bool, List[str]]:
    """
    Standalone function for quick sensor data validation.

    Args:
        sensor_data: Dictionary of sensor readings
        timestamp: Optional timestamp (defaults to current time)

    Returns:
        Tuple of (is_valid, validation_messages)
    """
    validator = DataValidator()
    if timestamp is None:
        timestamp = datetime.now()

    return validator.validate_sensor_data(sensor_data, timestamp)


def quick_validation(sensor_data: Dict[str, float]) -> bool:
    """
    Quick validation check for sensor data.

    Args:
        sensor_data: Dictionary of sensor readings

    Returns:
        True if data appears valid, False otherwise
    """
    if not sensor_data:
        return False

    # Basic checks
    if len(sensor_data) < 100:
        return False

    # Check for some temperature sensors
    temp_sensors = 0
    for key in sensor_data.keys():
        if any(pattern in key.lower() for pattern in ['temp', 'temperature']):
            temp_sensors += 1
            if temp_sensors >= 10:  # Need at least 10 temperature sensors
                return True

    return False


if __name__ == "__main__":
    # Example usage and testing
    import json

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Test with sample data
    sample_data = {
        "temperature_flow": 45.2,
        "temperature_return": 38.7,
        "temperature_ambient": 22.1,
        "flow_rate": 12.5,
        "pressure": 2.3,
        "energy_consumption": 1250.8
    }

    validator = DataValidator()
    is_valid, messages = validator.validate_sensor_data(sample_data, datetime.now())

    print("Validation Results:")
    print(f"Valid: {is_valid}")
    print("Messages:")
    for message in messages:
        print(f"  {message}")

    # Generate detailed report
    report = validator.generate_validation_report(sample_data, datetime.now())
    print("\nDetailed Report:")
    print(json.dumps(report, indent=2, default=str))
