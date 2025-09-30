import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from llm2slm.core import Config, convert_model, load_config, save_config


class TestConvertModel:
    """Test suite for convert_model function."""

    @patch("llm2slm.core.Config.load_from_env")
    @patch("llm2slm.core.Pipeline")
    @pytest.mark.asyncio
    async def test_convert_model_success(self, mock_pipeline_class, mock_load_config):
        """Test successful model conversion."""
        # Setup mocks
        mock_config = Config(openai_api_key="test_key")
        mock_load_config.return_value = mock_config

        mock_pipeline_instance = AsyncMock()
        mock_pipeline_instance.run.return_value = {"status": "completed", "result": "success"}
        mock_pipeline_class.return_value = mock_pipeline_instance

        # Execute
        result = await convert_model(
            input_model="test_model",
            output_path="output.slm",
            provider="openai",
            compression_factor=0.5,
        )

        # Verify
        assert result["status"] == "completed"
        assert result["result"] == "success"
        mock_load_config.assert_called_once()
        mock_pipeline_class.assert_called_once()
        mock_pipeline_instance.run.assert_called_once()

    @patch("llm2slm.core.Config.load_from_env")
    @pytest.mark.asyncio
    async def test_convert_model_config_fallback(self, mock_load_config):
        """Test convert_model with config fallback when env loading fails."""
        # Setup mock to raise ValueError
        mock_load_config.side_effect = ValueError("Missing env vars")

        with patch("llm2slm.core.Pipeline") as mock_pipeline_class:
            mock_pipeline_instance = AsyncMock()
            mock_pipeline_instance.run.return_value = {"status": "completed"}
            mock_pipeline_class.return_value = mock_pipeline_instance

            # Execute
            result = await convert_model(input_model="test_model", output_path="output.slm")

            # Verify fallback config was used
            assert result["status"] == "completed"
            mock_pipeline_class.assert_called_once()
            call_args = mock_pipeline_class.call_args[0][0]  # First positional arg
            assert call_args["openai_api_key"] == "dummy_key"

    @patch("llm2slm.core.Config.load_from_env")
    @pytest.mark.asyncio
    async def test_convert_model_with_custom_config(self, mock_load_config):
        """Test convert_model with custom config provided."""
        custom_config = Config(openai_api_key="custom_key", model_name="custom-model")

        with patch("llm2slm.core.Pipeline") as mock_pipeline_class:
            mock_pipeline_instance = AsyncMock()
            mock_pipeline_instance.run.return_value = {"status": "completed"}
            mock_pipeline_class.return_value = mock_pipeline_instance

            # Execute
            result = await convert_model(
                input_model="test_model", output_path="output.slm", config=custom_config
            )

            # Verify custom config was used (load_from_env not called)
            assert result["status"] == "completed"
            mock_load_config.assert_not_called()
            call_args = mock_pipeline_class.call_args[0][0]
            assert call_args["openai_api_key"] == "custom_key"
            assert call_args["model_name"] == "custom-model"


class TestLoadConfig:
    """Test suite for load_config function."""

    @patch("llm2slm.core.Config.load_from_env")
    def test_load_config_success(self, mock_load_config):
        """Test successful config loading."""
        mock_config = Config(
            openai_api_key="test_key",
            model_name="gpt-4",
            output_dir=Path("/tmp/output"),
            server_host="0.0.0.0",
            server_port=9000,
            log_level="DEBUG",
            pipeline_steps=["step1", "step2"],
            custom_settings={"custom": "value"},
        )
        mock_load_config.return_value = mock_config

        result = load_config()

        expected = {
            "openai_api_key": "test_key",
            "model_name": "gpt-4",
            "output_dir": str(Path("/tmp/output")),  # Convert to string to handle path separators
            "server_host": "0.0.0.0",
            "server_port": 9000,
            "log_level": "DEBUG",
            "pipeline_steps": ["step1", "step2"],
            "custom_settings": {"custom": "value"},
        }
        assert result == expected

    @patch("llm2slm.core.Config.load_from_env")
    def test_load_config_fallback(self, mock_load_config):
        """Test load_config fallback when env loading fails."""
        mock_load_config.side_effect = ValueError("Missing env vars")

        result = load_config()

        expected = {
            "openai_api_key": "",
            "model_name": "gpt-3.5-turbo",
            "output_dir": "./output",
            "server_host": "localhost",
            "server_port": 8000,
            "log_level": "INFO",
            "pipeline_steps": ["load", "compress", "export"],
            "custom_settings": {},
        }
        assert result == expected


class TestSaveConfig:
    """Test suite for save_config function."""

    def test_save_config_success(self):
        """Test successful config saving."""
        config_data = {
            "openai_api_key": "test_key",
            "model_name": "gpt-4",
            "output_dir": "/tmp/output",
            "server_host": "localhost",
            "server_port": 8000,
            "log_level": "INFO",
            "pipeline_steps": ["load", "compress", "export"],
            "custom_settings": {"test": "value"},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the home directory
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(temp_dir)

                save_config(config_data)

                # Verify file was created and contains correct data
                config_file = Path(temp_dir) / ".llm2slm" / "config.json"
                assert config_file.exists()

                with open(config_file, encoding="utf-8") as f:
                    saved_data = json.load(f)

                assert saved_data == config_data

    def test_save_config_creates_directory(self):
        """Test that save_config creates the config directory if it doesn't exist."""
        config_data = {"test": "value"}

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path(temp_dir)

                save_config(config_data)

                # Verify directory was created
                config_dir = Path(temp_dir) / ".llm2slm"
                assert config_dir.exists()
                assert config_dir.is_dir()
