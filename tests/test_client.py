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

    @patch('src.client.Luxtronik', side_effect=Exception("Connection failed"))
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

    @patch('src.client.HeatPumpClient.connect')
    def test_get_all_sensors_no_connection(self, mock_connect):
        mock_connect.return_value = False
        client = HeatPumpClient("192.168.1.100")
        with pytest.raises(ConnectionError):
            client.get_all_sensors()

    @patch('src.client.Luxtronik')
    def test_connect_with_retries(self, mock_lux):
        # Make first two attempts fail, third succeed
        mock_lux.side_effect = [Exception("Attempt 1"), Exception("Attempt 2"), MagicMock()]

        client = HeatPumpClient("192.168.1.100")
        with patch('time.sleep'):  # Don't actually sleep during tests
            result = client.connect()

        assert result is True
        assert client.connection is not None
        assert mock_lux.call_count == 3

    @patch('src.client.Luxtronik', side_effect=Exception("All attempts failed"))
    def test_connect_all_retries_fail(self, mock_lux):
        client = HeatPumpClient("192.168.1.100")
        with patch('time.sleep'):  # Don't actually sleep during tests
            result = client.connect()

        assert result is False
        assert client.connection is None
        assert mock_lux.call_count == 3
        if client.connection is not None:
            client.connection.parameters.__dict__ = {'pressure': 2.1}

        if client.connection is not None:
            # Replace the dict access with a property that raises an exception
            type(client.connection.calculations).__dict__ = property(lambda self: raise_exception())

        with pytest.raises(Exception):
            client.get_all_sensors()

        # Connection should be reset after exception
        assert client.connection is None
