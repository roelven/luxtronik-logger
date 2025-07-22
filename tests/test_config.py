import os
import pytest
from src.config import Config

class TestConfig:
    def test_defaults(self):
        config = Config()
        assert config.port == 8888
        assert config.interval_sec == 30
        assert config.csv_time == "07:00"

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("HOST", "192.168.1.100")
        monkeypatch.setenv("PORT", "9999")
        
        config = Config()
        config.load()
        assert config.host == "192.168.1.100"
        assert config.port == 9999

    def test_yaml_override(self, tmp_path):
        yaml_content = """
        HOST: 192.168.1.101
        INTERVAL_SEC: 60
        """
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(yaml_content)
        
        config = Config()
        config.load(str(config_file))
        assert config.host == "192.168.1.101"
        assert config.interval_sec == 60

    def test_validation(self):
        config = Config()
        with pytest.raises(ValueError, match="HOST must be specified"):
            config._validate()
        
        config.host = "valid"
        config.port = 0
        with pytest.raises(ValueError, match="PORT must be between"):
            config._validate()