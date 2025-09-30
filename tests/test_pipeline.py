from unittest.mock import AsyncMock, patch

import pytest

from llm2slm.core.pipeline import Pipeline, PipelineError


class TestPipelineError:
    """Test suite for PipelineError exception."""

    def test_pipeline_error_inheritance(self):
        """Test that PipelineError inherits from Exception."""
        error = PipelineError("test message")
        assert isinstance(error, Exception)
        assert str(error) == "test message"


class TestPipelineInit:
    """Test suite for Pipeline.__init__ method."""

    def test_init_success(self):
        """Test successful Pipeline initialization."""
        config = {"test": "value"}
        pipeline = Pipeline(config)

        assert pipeline.config == config
        assert pipeline.steps == ["load_model", "process_model", "export_slm"]

    def test_init_with_custom_steps(self):
        """Test Pipeline initialization with custom steps."""
        config = {"test": "value"}
        custom_steps = ["step1", "step2"]
        pipeline = Pipeline(config, custom_steps)

        assert pipeline.config == config
        assert pipeline.steps == custom_steps

    def test_init_invalid_config_none(self):
        """Test Pipeline initialization with None config."""
        with pytest.raises(PipelineError, match="Invalid configuration provided"):
            Pipeline(None)

    def test_init_invalid_config_empty(self):
        """Test Pipeline initialization with empty config."""
        with pytest.raises(PipelineError, match="Invalid configuration provided"):
            Pipeline({})

    def test_init_invalid_config_type(self):
        """Test Pipeline initialization with invalid config type."""
        with pytest.raises(PipelineError, match="Invalid configuration provided"):
            Pipeline("not_a_dict")


class TestPipelineRun:
    """Test suite for Pipeline.run method."""

    @pytest.mark.asyncio
    async def test_run_success(self):
        """Test successful pipeline execution."""
        config = {"test": "value"}
        pipeline = Pipeline(config)

        with patch.object(pipeline, "_execute_step", new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = [
                {"step1": "result1"},
                {"step2": "result2"},
                {"step3": "result3"},
            ]

            result = await pipeline.run()

            assert result["status"] == "completed"
            assert result["outputs"]["load_model"] == {"step1": "result1"}
            assert result["outputs"]["process_model"] == {"step2": "result2"}
            assert result["outputs"]["export_slm"] == {"step3": "result3"}
            assert mock_execute.call_count == 3

    @pytest.mark.asyncio
    async def test_run_with_failure(self):
        """Test pipeline execution with step failure."""
        config = {"test": "value"}
        pipeline = Pipeline(config)

        with patch.object(pipeline, "_execute_step", new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = [{"step1": "result1"}, Exception("Step 2 failed")]

            with pytest.raises(PipelineError, match="Pipeline failed at step process_model"):
                await pipeline.run()

    @pytest.mark.asyncio
    async def test_run_partial_failure_result(self):
        """Test that run returns partial results even on failure."""
        config = {"test": "value"}
        pipeline = Pipeline(config)

        with patch.object(pipeline, "_execute_step", new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = [{"step1": "result1"}, Exception("Step 2 failed")]

            with pytest.raises(PipelineError):
                await pipeline.run()

            # Note: This test verifies the exception is raised, but doesn't check
            # the result content since the exception prevents return

    @pytest.mark.asyncio
    async def test_run_custom_steps(self):
        """Test pipeline execution with custom steps."""
        config = {"test": "value"}
        custom_steps = ["custom_step1", "custom_step2"]
        pipeline = Pipeline(config, custom_steps)

        with patch.object(pipeline, "_execute_step", new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = [{"custom1": "result1"}, {"custom2": "result2"}]

            result = await pipeline.run()

            assert result["status"] == "completed"
            assert result["outputs"]["custom_step1"] == {"custom1": "result1"}
            assert result["outputs"]["custom_step2"] == {"custom2": "result2"}


class TestPipelineExecuteStep:
    """Test suite for Pipeline._execute_step method."""

    @pytest.mark.asyncio
    async def test_execute_step_load_model(self):
        """Test _execute_step with load_model step."""
        pipeline = Pipeline({"test": "value"})

        result = await pipeline._execute_step("load_model")

        assert result == {"model_loaded": True}

    @pytest.mark.asyncio
    async def test_execute_step_process_model(self):
        """Test _execute_step with process_model step."""
        pipeline = Pipeline({"test": "value"})

        result = await pipeline._execute_step("process_model")

        assert result == {"model_processed": True}

    @pytest.mark.asyncio
    async def test_execute_step_export_slm(self):
        """Test _execute_step with export_slm step."""
        pipeline = Pipeline({"test": "value"})

        result = await pipeline._execute_step("export_slm")

        assert result == {"slm_exported": True}

    @pytest.mark.asyncio
    async def test_execute_step_unknown_step(self):
        """Test _execute_step with unknown step."""
        pipeline = Pipeline({"test": "value"})

        with pytest.raises(PipelineError, match="Unknown step: unknown_step"):
            await pipeline._execute_step("unknown_step")

    @pytest.mark.asyncio
    async def test_execute_step_async_simulation(self):
        """Test that _execute_step simulates async operation."""
        pipeline = Pipeline({"test": "value"})

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await pipeline._execute_step("load_model")

            mock_sleep.assert_called_once_with(0.1)
