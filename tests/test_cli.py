from unittest.mock import patch

from click.testing import CliRunner

from llm2slm.cli import cli

"""
Tests for the CLI module of the llm2slm project.

This module contains unit tests for the command-line interface functionality,
ensuring that model conversion commands work correctly and handle errors properly.
"""


class TestCLI:
    """Test suite for CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_main_help(self):
        """Test that the main CLI command displays help correctly."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "convert" in result.output

    @patch("llm2slm.cli.convert_model")
    def test_convert_command_success(self, mock_convert):
        """Test successful model conversion via CLI."""
        mock_convert.return_value = {"status": "completed"}
        result = self.runner.invoke(cli, ["convert", "model.llm", "model.slm"])
        assert result.exit_code == 0
        assert "Conversion result" in result.output
        mock_convert.assert_called_once()

    @patch("llm2slm.cli.convert_model")
    def test_convert_command_failure(self, mock_convert):
        """Test model conversion failure via CLI."""
        mock_convert.side_effect = Exception("Invalid model format")
        result = self.runner.invoke(cli, ["convert", "invalid.llm", "output.slm"])
        assert result.exit_code == 1
        assert "Error during conversion" in result.output

    def test_convert_command_missing_args(self):
        """Test convert command with missing required arguments."""
        result = self.runner.invoke(cli, ["convert"])
        assert result.exit_code == 2  # Click error for missing args
        assert "Missing argument" in result.output
