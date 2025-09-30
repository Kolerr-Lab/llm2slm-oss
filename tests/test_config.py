import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from llm2slm.core.config import Config


class TestConfigClass:
    """Test suite for Config dataclass."""

    def test_config_default_values(self):
        """Test Config with default values."""
        config = Config(openai_api_key="test_key")

        assert config.openai_api_key == "test_key"
        assert config.model_name == "gpt-3.5-turbo"
        assert config.output_dir == Path("./output")
        assert config.server_host == "localhost"
        assert config.server_port == 8000
        assert config.log_level == "INFO"
        assert config.pipeline_steps == ["load", "compress", "export"]
        assert config.custom_settings == {}

    def test_config_custom_values(self):
        """Test Config with custom values."""
        custom_settings = {"custom": "value"}
        config = Config(
            openai_api_key="custom_key",
            model_name="gpt-4",
            output_dir=Path("/tmp/output"),
            server_host="0.0.0.0",
            server_port=9000,
            log_level="DEBUG",
            pipeline_steps=["step1", "step2"],
            custom_settings=custom_settings,
        )

        assert config.openai_api_key == "custom_key"
        assert config.model_name == "gpt-4"
        assert config.output_dir == Path("/tmp/output")
        assert config.server_host == "0.0.0.0"
        assert config.server_port == 9000
        assert config.log_level == "DEBUG"
        assert config.pipeline_steps == ["step1", "step2"]
        assert config.custom_settings == custom_settings


class TestConfigLoadFromEnv:
    """Test suite for Config.load_from_env method."""

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "test_key",
            "MODEL_NAME": "gpt-4",
            "OUTPUT_DIR": "/tmp/output",
            "SERVER_HOST": "0.0.0.0",
            "SERVER_PORT": "9000",
            "LOG_LEVEL": "DEBUG",
            "PIPELINE_STEPS": "load,process,export",
        },
    )
    def test_load_from_env_success(self):
        """Test successful loading from environment variables."""
        config = Config.load_from_env()

        assert config.openai_api_key == "test_key"
        assert config.model_name == "gpt-4"
        assert config.output_dir == Path("/tmp/output")
        assert config.server_host == "0.0.0.0"
        assert config.server_port == 9000
        assert config.log_level == "DEBUG"
        assert config.pipeline_steps == ["load", "process", "export"]

    @patch.dict(os.environ, {}, clear=True)
    def test_load_from_env_missing_api_key(self):
        """Test load_from_env with missing API key."""
        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
            Config.load_from_env()

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key", "SERVER_PORT": "invalid_port"})
    def test_load_from_env_invalid_port(self):
        """Test load_from_env with invalid server port."""
        with pytest.raises(ValueError, match="Invalid SERVER_PORT value: invalid_port"):
            Config.load_from_env()

    @patch.dict(
        os.environ, {"OPENAI_API_KEY": "test_key", "PIPELINE_STEPS": "step1, step2 , step3"}
    )
    def test_load_from_env_pipeline_steps_parsing(self):
        """Test load_from_env with pipeline steps parsing."""
        config = Config.load_from_env()

        assert config.pipeline_steps == ["step1", "step2", "step3"]

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}, clear=True)
    def test_load_from_env_defaults(self):
        """Test load_from_env with default values."""
        config = Config.load_from_env()

        assert config.model_name == "gpt-3.5-turbo"
        assert config.output_dir == Path("./output")
        assert config.server_host == "localhost"
        assert config.server_port == 8000
        assert config.log_level == "INFO"
        assert config.pipeline_steps == ["load", "compress", "export"]


class TestConfigLoadFromYaml:
    """Test suite for Config.load_from_yaml method."""

    def test_load_from_yaml_success(self):
        """Test successful loading from YAML file."""
        yaml_content = """
        openai_api_key: test_key
        model_name: gpt-4
        output_dir: /tmp/output
        server_host: 0.0.0.0
        server_port: 9000
        log_level: DEBUG
        pipeline_steps:
          - load
          - process
          - export
        custom_settings:
          custom: value
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_file = f.name

        try:
            config = Config.load_from_yaml(yaml_file)

            assert config.openai_api_key == "test_key"
            assert config.model_name == "gpt-4"
            assert config.output_dir == Path("/tmp/output")
            assert config.server_host == "0.0.0.0"
            assert config.server_port == 9000
            assert config.log_level == "DEBUG"
            assert config.pipeline_steps == ["load", "process", "export"]
            assert config.custom_settings == {"custom": "value"}
        finally:
            os.unlink(yaml_file)

    def test_load_from_yaml_file_not_found(self):
        """Test load_from_yaml with non-existent file."""
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            Config.load_from_yaml("non_existent_file.yaml")

    def test_load_from_yaml_missing_api_key(self):
        """Test load_from_yaml with missing API key."""
        yaml_content = """
        model_name: gpt-4
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_file = f.name

        try:
            with pytest.raises(ValueError, match="openai_api_key is required"):
                Config.load_from_yaml(yaml_file)
        finally:
            os.unlink(yaml_file)

    def test_load_from_yaml_invalid_port_type(self):
        """Test load_from_yaml with invalid port type."""
        yaml_content = """
        openai_api_key: test_key
        server_port: "not_a_number"
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_file = f.name

        try:
            with pytest.raises(ValueError, match="server_port must be an integer"):
                Config.load_from_yaml(yaml_file)
        finally:
            os.unlink(yaml_file)

    def test_load_from_yaml_invalid_pipeline_steps(self):
        """Test load_from_yaml with invalid pipeline steps."""
        yaml_content = """
        openai_api_key: test_key
        pipeline_steps: "not_a_list"
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_file = f.name

        try:
            with pytest.raises(ValueError, match="pipeline_steps must be a list"):
                Config.load_from_yaml(yaml_file)
        finally:
            os.unlink(yaml_file)

    def test_load_from_yaml_invalid_yaml(self):
        """Test load_from_yaml with invalid YAML."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [unbalanced")
            yaml_file = f.name

        try:
            with pytest.raises(yaml.YAMLError):
                Config.load_from_yaml(yaml_file)
        finally:
            os.unlink(yaml_file)

    def test_load_from_yaml_non_dict_content(self):
        """Test load_from_yaml with non-dictionary YAML content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("- item1\n- item2\n")
            yaml_file = f.name

        try:
            with pytest.raises(ValueError, match="YAML configuration must be a dictionary"):
                Config.load_from_yaml(yaml_file)
        finally:
            os.unlink(yaml_file)


class TestConfigSetupLogging:
    """Test suite for Config.setup_logging method."""

    def test_setup_logging_info_level(self):
        """Test setup_logging with INFO level."""
        config = Config(openai_api_key="test_key", log_level="INFO")

        with patch("logging.basicConfig") as mock_basic_config:
            config.setup_logging()

            mock_basic_config.assert_called_once()
            call_kwargs = mock_basic_config.call_args[1]
            assert call_kwargs["level"] == logging.INFO
            assert "format" in call_kwargs

    def test_setup_logging_debug_level(self):
        """Test setup_logging with DEBUG level."""
        config = Config(openai_api_key="test_key", log_level="DEBUG")

        with patch("logging.basicConfig") as mock_basic_config:
            config.setup_logging()

            call_kwargs = mock_basic_config.call_args[1]
            assert call_kwargs["level"] == logging.DEBUG

    def test_setup_logging_invalid_level(self):
        """Test setup_logging with invalid level defaults to INFO."""
        config = Config(openai_api_key="test_key", log_level="INVALID")

        with patch("logging.basicConfig") as mock_basic_config:
            config.setup_logging()

            call_kwargs = mock_basic_config.call_args[1]
            assert call_kwargs["level"] == logging.INFO


class TestConfigValidate:
    """Test suite for Config.validate method."""

    def test_validate_success(self):
        """Test successful validation."""
        config = Config(openai_api_key="test_key")
        # Should not raise any exception
        config.validate()

    def test_validate_invalid_log_level(self):
        """Test validate with invalid log level."""
        config = Config(openai_api_key="test_key", log_level="INVALID")

        with pytest.raises(ValueError, match="Invalid log_level: INVALID"):
            config.validate()

    def test_validate_empty_pipeline_steps(self):
        """Test validate with empty pipeline steps."""
        config = Config(openai_api_key="test_key", pipeline_steps=[])

        with pytest.raises(ValueError, match="pipeline_steps cannot be empty"):
            config.validate()

    def test_validate_invalid_custom_settings(self):
        """Test validate with invalid custom settings type."""
        config = Config(openai_api_key="test_key", custom_settings="not_a_dict")  # type: ignore

        with pytest.raises(ValueError, match="custom_settings must be a dictionary"):
            config.validate()
