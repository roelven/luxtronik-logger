import pytest
import os
from unittest.mock import patch, MagicMock
from src.utils import check_disk_usage

class TestCheckDiskUsage:
    def test_valid_disk_usage_below_threshold(self):
        """Test disk usage check when usage is below threshold"""
        paths = ["/tmp"]
        threshold = 90

        # Mock disk usage to return 50% usage
        with patch("shutil.disk_usage", return_value=(1000, 500, 500)):
            with patch("logging.Logger.debug") as mock_debug:
                result = check_disk_usage(paths, threshold)
                assert result == []
                mock_debug.assert_called()

    def test_valid_disk_usage_above_threshold(self):
        """Test disk usage check when usage is above threshold"""
        paths = ["/tmp"]
        threshold = 30

        # Mock disk usage to return 50% usage
        with patch("shutil.disk_usage", return_value=(1000, 500, 500)):
            with patch("logging.Logger.warning") as mock_warning:
                result = check_disk_usage(paths, threshold)
                assert len(result) == 1
                assert result[0][0] == "/tmp"
                assert result[0][1] == 50.0
                mock_warning.assert_called()

    def test_multiple_paths_mixed_usage(self):
        """Test disk usage check with multiple paths having different usage levels"""
        paths = ["/tmp", "/var"]
        threshold = 40

        # Mock disk usage for different calls
        def disk_usage_side_effect(path):
            if path == "/tmp":
                return (1000, 300, 700)  # 30% usage
            elif path == "/var":
                return (1000, 500, 500)  # 50% usage
            return (1000, 0, 1000)       # 0% usage

        with patch("shutil.disk_usage", side_effect=disk_usage_side_effect):
            with patch("logging.Logger.debug") as mock_debug:
                with patch("logging.Logger.warning") as mock_warning:
                    result = check_disk_usage(paths, threshold)
                    assert len(result) == 1
                    assert result[0][0] == "/var"
                    assert result[0][1] == 50.0
                    mock_debug.assert_called()
                    mock_warning.assert_called()

    def test_invalid_threshold(self):
        """Test disk usage check with invalid threshold values"""
        paths = ["/tmp"]

        # Test threshold <= 0
        with pytest.raises(ValueError, match="Threshold must be between 1-99"):
            check_disk_usage(paths, 0)

        # Test threshold >= 100
        with pytest.raises(ValueError, match="Threshold must be between 1-99"):
            check_disk_usage(paths, 100)

    def test_nonexistent_path(self):
        """Test disk usage check with non-existent path"""
        paths = ["/nonexistent/path"]
        threshold = 50

        with patch("os.path.exists", return_value=False):
            with patch("os.path.dirname", side_effect=lambda x: "/" if x != "/" else ""):
                with patch("logging.Logger.warning") as mock_warning:
                    result = check_disk_usage(paths, threshold)
                    assert result == []
                    mock_warning.assert_called()

    def test_disk_usage_exception(self):
        """Test disk usage check when exception occurs"""
        paths = ["/tmp"]
        threshold = 50

        with patch("shutil.disk_usage", side_effect=Exception("Permission denied")):
            with patch("logging.Logger.error") as mock_error:
                result = check_disk_usage(paths, threshold)
                assert result == []
                mock_error.assert_called()
