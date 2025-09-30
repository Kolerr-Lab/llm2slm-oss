import json
import pickle
import tempfile
from pathlib import Path

import pytest

from llm2slm.core.config import Config
from llm2slm.slm.export import SLMExporter
from llm2slm.slm.metadata import SLMMetadataCreator
from llm2slm.slm.model import SLMModel
from llm2slm.slm.runtime import SLMRuntime


class TestSLMExporter:
    """Test suite for SLMExporter class."""

    def test_slm_exporter_init(self):
        """Test SLMExporter initialization."""
        config = Config(openai_api_key="test_key")
        exporter = SLMExporter(config)

        assert exporter.config == config
        assert exporter.export_formats == ["pickle", "onnx", "tensorrt", "native"]

    @pytest.mark.asyncio
    async def test_export_native_format(self):
        """Test exporting in native format."""
        config = Config(openai_api_key="test_key")
        exporter = SLMExporter(config)

        model_data = {
            "parameters": 1000000,
            "size": 500000,
            "compression_ratio": 0.5,
            "quantization": "8bit",
            "pruned": True,
            "distilled": False,
            "architecture": "transformer",
            "layers": ["layer1", "layer2"],
            "hidden_size": 768,
            "attention_heads": 12,
            "tokenizer": {"vocab_size": 30000},
        }

        model_info = {
            "model_id": "gpt-3.5-turbo",
            "provider": "openai",
            "parameters": 175000000,
            "size": 1000000,
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_slm"

            result = await exporter.export(model_data, output_path, model_info, "native")

            # Verify files were created
            assert (output_path / "metadata.json").exists()
            assert (output_path / "model.weights").exists()
            assert (output_path / "tokenizer.json").exists()
            assert (output_path / "config.json").exists()
            assert (output_path / "inference.py").exists()

            # Verify result structure
            assert result["format"] == "native"
            assert "files" in result
            assert "size" in result
            assert "checksum" in result
            assert len(result["files"]) == 5

    @pytest.mark.asyncio
    async def test_export_pickle_format(self):
        """Test exporting in pickle format."""
        config = Config(openai_api_key="test_key")
        exporter = SLMExporter(config)

        model_data = {"test": "data"}
        model_info = {"model_id": "test"}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_pickle"

            result = await exporter.export(model_data, output_path, model_info, "pickle")

            assert result["format"] == "pickle"
            assert (output_path / "model.pkl").exists()

    @pytest.mark.asyncio
    async def test_export_unsupported_format(self):
        """Test exporting with unsupported format."""
        config = Config(openai_api_key="test_key")
        exporter = SLMExporter(config)

        model_data = {"test": "data"}
        model_info = {"model_id": "test"}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_unknown"

            # Should default to native format
            result = await exporter.export(model_data, output_path, model_info, "unknown")

            assert result["format"] == "native"

    def test_create_metadata(self):
        """Test metadata creation."""

        model_data = {
            "parameters": 500000,
            "size": 250000,
            "compression_ratio": 0.5,
            "quantization": "8bit",
            "pruned": True,
            "distilled": False,
            "architecture": "transformer",
            "layers": ["layer1"],
            "hidden_size": 768,
            "attention_heads": 12,
            "tokenizer": {"vocab_size": 30000},
        }

        model_info = {
            "model_id": "gpt-3.5-turbo",
            "provider": "openai",
            "parameters": 175000000,
            "size": 1000000,
        }

        metadata = SLMMetadataCreator.create_metadata(model_data, model_info)

        assert metadata["format_version"] == "1.0"
        assert metadata["created_with"] == "llm2slm"
        assert metadata["original_model"]["id"] == "gpt-3.5-turbo"
        assert metadata["slm_model"]["parameters"] == 500000
        assert metadata["slm_model"]["compression_ratio"] == 0.5
        assert metadata["architecture"]["type"] == "transformer"


class TestSLMModel:
    """Test suite for SLMModel class."""

    def test_slm_model_init(self):
        """Test SLMModel initialization."""
        model_path = Path("/tmp/test")
        metadata = {"original_model": {"id": "gpt-3.5-turbo"}, "slm_model": {"parameters": 500000}}
        model_data = {"parameters": 500000, "size": 250000}

        model = SLMModel(model_path, metadata, model_data)

        assert model.model_path == model_path
        assert model.metadata == metadata
        assert model.model_data == model_data
        assert model.loaded_time is not None

    def test_slm_model_properties(self):
        """Test SLMModel properties."""
        model_path = Path("/tmp/test")
        metadata = {"original_model": {"id": "gpt-3.5-turbo"}, "slm_model": {"parameters": 500000}}
        model_data = {"parameters": 500000, "size": 250000}

        model = SLMModel(model_path, metadata, model_data)

        assert model.model_id == "gpt-3.5-turbo"
        assert model.parameters == 500000
        assert model.size == 250000

    def test_slm_model_properties_missing_data(self):
        """Test SLMModel properties with missing data."""
        model_path = Path("/tmp/test")
        metadata = {}
        model_data = {}

        model = SLMModel(model_path, metadata, model_data)

        assert model.model_id == "unknown"
        assert model.parameters == 0
        assert model.size == 0

    def test_slm_model_get_info(self):
        """Test SLMModel get_info method."""
        model_path = Path("/tmp/test")
        metadata = {
            "original_model": {"id": "gpt-3.5-turbo"},
            "slm_model": {"compression_ratio": 0.5, "quantization": "8bit"},
            "architecture": {"type": "transformer"},
            "runtime": {"engine": "native"},
        }
        model_data = {"parameters": 500000, "size": 250000}

        model = SLMModel(model_path, metadata, model_data)

        info = model.get_info()

        assert info["model_id"] == "gpt-3.5-turbo"
        assert info["parameters"] == 500000
        assert info["size"] == 250000
        assert info["compression_ratio"] == 0.5
        assert info["quantization"] == "8bit"
        assert info["architecture"]["type"] == "transformer"
        assert info["runtime"]["engine"] == "native"
        assert "loaded_time" in info


class TestSLMRuntime:
    """Test suite for SLMRuntime class."""

    def test_slm_runtime_init(self):
        """Test SLMRuntime initialization."""
        config = Config(openai_api_key="test_key")
        runtime = SLMRuntime(config)

        assert runtime.config == config
        assert runtime.loaded_models == {}
        assert runtime.inference_cache == {}

    @pytest.mark.asyncio
    async def test_load_model_native_format(self):
        """Test loading a native format SLM model."""
        config = Config(openai_api_key="test_key")
        runtime = SLMRuntime(config)

        # Create a mock native model directory
        with tempfile.TemporaryDirectory() as temp_dir:
            model_dir = Path(temp_dir) / "test_model"
            model_dir.mkdir(parents=True, exist_ok=True)

            # Create metadata.json
            metadata = {
                "original_model": {"id": "gpt-3.5-turbo"},
                "slm_model": {"parameters": 500000},
            }
            (model_dir / "metadata.json").write_text(json.dumps(metadata))

            # Create model.weights
            model_data = {"parameters": 500000, "size": 250000}
            with open(model_dir / "model.weights", "wb") as f:
                pickle.dump(model_data, f)

            # Load the model
            loaded_model = await runtime.load_model(model_dir)

            assert isinstance(loaded_model, SLMModel)
            assert loaded_model.model_id == "gpt-3.5-turbo"
            assert loaded_model.parameters == 500000

            # Test caching - should return same instance
            cached_model = await runtime.load_model(model_dir)
            assert cached_model is loaded_model

    @pytest.mark.asyncio
    async def test_load_model_pickle_format(self):
        """Test loading a pickle format SLM model."""
        config = Config(openai_api_key="test_key")
        runtime = SLMRuntime(config)

        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as temp_file:
            pickle_file = Path(temp_file.name)

            # Create pickle file with model data
            model_data = {
                "metadata": {"original_model": {"id": "gpt-4"}},
                "model_data": {"parameters": 1000000},
            }
            with open(pickle_file, "wb") as f:
                pickle.dump(model_data, f)

            loaded_model = await runtime.load_model(pickle_file)

            assert isinstance(loaded_model, SLMModel)
            assert loaded_model.model_id == "gpt-4"
            assert loaded_model.parameters == 1000000

    @pytest.mark.asyncio
    async def test_load_model_unsupported_format(self):
        """Test loading an unsupported model format."""
        config = Config(openai_api_key="test_key")
        runtime = SLMRuntime(config)

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            unsupported_file = Path(temp_file.name)
            temp_file.write(b"unsupported content")

        with pytest.raises(ValueError, match="Unsupported model format"):
            await runtime.load_model(unsupported_file)

    @pytest.mark.asyncio
    async def test_load_model_missing_metadata(self):
        """Test loading model with missing metadata."""
        config = Config(openai_api_key="test_key")
        runtime = SLMRuntime(config)

        with tempfile.TemporaryDirectory() as temp_dir:
            model_dir = Path(temp_dir) / "test_model"
            model_dir.mkdir()

            # Missing metadata.json
            with pytest.raises(FileNotFoundError):
                await runtime.load_model(model_dir)

    def test_slm_runtime_unload_model(self):
        """Test unloading a model from runtime."""
        config = Config(openai_api_key="test_key")
        runtime = SLMRuntime(config)

        # Create a mock model
        mock_model = SLMModel(Path("/tmp/test"), {}, {})

        # Manually add a model to cache
        model_path = Path("/tmp/test")
        runtime.loaded_models[str(model_path.absolute())] = mock_model

        # Unload the model
        result = runtime.unload_model(model_path)

        assert result is True
        assert str(model_path.absolute()) not in runtime.loaded_models

    def test_slm_runtime_clear_cache(self):
        """Test clearing the inference cache."""
        config = Config(openai_api_key="test_key")
        runtime = SLMRuntime(config)

        # Add some cache entries
        runtime.inference_cache["key1"] = "value1"
        runtime.inference_cache["key2"] = "value2"

        # Clear cache
        runtime.clear_cache()

        assert runtime.inference_cache == {}

    def test_slm_runtime_list_loaded_models(self):
        """Test listing loaded models."""
        config = Config(openai_api_key="test_key")
        runtime = SLMRuntime(config)

        # Create mock models
        mock_model1 = SLMModel(
            Path("/tmp/model1"), {"original_model": {"id": "model1"}}, {"parameters": 1000}
        )
        mock_model2 = SLMModel(
            Path("/tmp/model2"), {"original_model": {"id": "model2"}}, {"parameters": 2000}
        )

        # Add some loaded models
        runtime.loaded_models["/tmp/model1"] = mock_model1
        runtime.loaded_models["/tmp/model2"] = mock_model2

        loaded = runtime.list_loaded_models()

        assert len(loaded) == 2
        model_ids = [model["model_id"] for model in loaded]
        assert "model1" in model_ids
        assert "model2" in model_ids
