import pytest
from unittest.mock import MagicMock, patch
from src.client import HeatPumpClient

class TestHeatPumpClient:
    @patch('src.client.Luxtronik')
    def test_connect_success(self, mock_lux):
        mock_instance = MagicMock()
        mock_lux.return_value = mock_instance
        
        client = HeatPumpClient("192.168.1.100")
        assert client.connect() is True
        assert client.connection is not None
    
    @patch('luxtronik.Luxtronik', side_effect=Exception("Connection failed"))
    def test_connect_failure(self, mock_lux):
        client = HeatPumpClient("192.168.1.100")
        assert client.connect() is False
        assert client.connection is None
    
    @patch('src.client.HeatPumpClient.connect')
    def test_get_all_sensors(self, mock_connect):
        mock_connect.return_value = True
        
        mock_data = {
            'calculations': {'temp1': 45.0, 'temp2': 30.5},
            'parameters': {'pressure': 2.1},
            'visibilities': {'status': 1}
        }
        
        client = HeatPumpClient("192.168.1.100")
        client.connection = MagicMock()
        client.connection.read.side_effect = lambda x: mock_data[x]
        
        readings = client.get_all_sensors()
        assert len(readings) > 0  # At least some readings should be returned
        assert any(k.startswith('calculations.') for k in readings.keys())
        assert any(k.startswith('parameters.') for k in readings.keys())
        assert any(k.startswith('visibilities.') for k in readings.keys())
    
    def test_get_all_sensors_no_connection(self):
        client = HeatPumpClient("192.168.1.100")
        with pytest.raises(ConnectionError):
            client.get_all_sensors()