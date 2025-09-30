"""SLM export functionality.

This module handles exporting compressed models to the Small Language Model
format, including serialization, optimization, and packaging.
"""

import json
import logging
import pickle
import zipfile
from pathlib import Path
from typing import Any, Dict

from ..core.config import Config
from .metadata import SLMMetadataCreator

logger = logging.getLogger(__name__)


class SLMExporter:
    """Exporter for Small Language Models."""

    def __init__(self, config: Config):
        """Initialize the SLM exporter."""
        self.config = config
        self.export_formats = ["pickle", "onnx", "tensorrt", "native"]

    async def export(
        self,
        model_data: Dict[str, Any],
        output_path: Path,
        model_info: Dict[str, Any],
        export_format: str = "native",
    ) -> Dict[str, Any]:
        """Export a compressed model to SLM format.

        Args:
            model_data: The compressed model data
            output_path: Path where to save the SLM
            model_info: Original model information
            export_format: Export format (pickle, onnx, tensorrt, native)

        Returns:
            Dictionary containing export information
        """
        logger.info(f"Exporting SLM to {output_path} in {export_format} format")

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        # Prepare SLM metadata
        slm_metadata = SLMMetadataCreator.create_metadata(model_data, model_info)

        # Export based on format
        if export_format == "pickle":
            return await self._export_pickle(model_data, output_path, slm_metadata)
        elif export_format == "onnx":
            return await self._export_onnx(model_data, output_path, slm_metadata)
        elif export_format == "tensorrt":
            return await self._export_tensorrt(model_data, output_path, slm_metadata)
        else:  # native
            return await self._export_native(model_data, output_path, slm_metadata)

    async def _export_native(
        self, model_data: Dict[str, Any], output_path: Path, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export in native SLM format."""
        # Save metadata
        metadata_file = output_path / "metadata.json"
        with open(metadata_file, "w") as mf:
            json.dump(metadata, mf, indent=2)

        # Save model weights (simulated)
        weights_file = output_path / "model.weights"
        with open(weights_file, "wb") as bf:
            # Simulate serialized weights
            weights_data = {
                "layers": model_data.get("layers", []),
                "parameters": model_data.get("parameters", 0),
                "size": model_data.get("size", 0),
                "quantization": model_data.get("quantization", "none"),
            }
            pickle.dump(weights_data, bf)

        # Save tokenizer
        tokenizer_file = output_path / "tokenizer.json"
        with open(tokenizer_file, "w") as tf:
            json.dump(model_data.get("tokenizer", {}), tf, indent=2)

        # Create configuration file
        config_file = output_path / "config.json"
        config_data = {
            "model_type": "slm",
            "architecture": metadata["architecture"],
            "runtime": metadata["runtime"],
            "files": {
                "metadata": "metadata.json",
                "weights": "model.weights",
                "tokenizer": "tokenizer.json",
            },
        }
        with open(config_file, "w") as cf:
            json.dump(config_data, cf, indent=2)

        # Create inference script
        self._create_inference_script(output_path)

        # Create package info
        package_info = {
            "format": "native",
            "files": [
                "metadata.json",
                "model.weights",
                "tokenizer.json",
                "config.json",
                "inference.py",
            ],
            "size": sum(f.stat().st_size for f in output_path.glob("*") if f.is_file()),
            "checksum": self._calculate_checksum(output_path),
        }

        logger.info(f"Native SLM exported successfully to {output_path}")
        return package_info

    async def _export_pickle(
        self, model_data: Dict[str, Any], output_path: Path, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export in pickle format."""
        model_file = output_path / "model.pkl"

        export_data = {"metadata": metadata, "model_data": model_data, "format": "pickle"}

        with open(model_file, "wb") as pf:
            pickle.dump(export_data, pf)

        # Create README
        readme_file = output_path / "README.md"
        with open(readme_file, "w") as rf:
            rf.write(
                f"""# SLM Model - {metadata['original_model']['id']}

This is a Small Language Model converted from {metadata['original_model']['id']}.

## Usage

```python
import pickle

# Load the model
with open('model.pkl', 'rb') as pf:
    model = pickle.load(pf)

# Access metadata
metadata = model['metadata']
model_data = model['model_data']
```

## Model Information

- Original Parameters: {metadata['original_model']['parameters']:,}
- Compressed Parameters: {metadata['slm_model']['parameters']:,}
- Compression Ratio: {metadata['slm_model']['compression_ratio']:.2f}
- Quantization: {metadata['slm_model']['quantization']}
"""
            )

        package_info = {
            "format": "pickle",
            "files": ["model.pkl", "README.md"],
            "size": model_file.stat().st_size + readme_file.stat().st_size,
            "checksum": self._calculate_checksum(output_path),
        }

        logger.info(f"Pickle SLM exported successfully to {output_path}")
        return package_info

    async def _export_onnx(
        self, model_data: Dict[str, Any], output_path: Path, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export in ONNX format."""
        # Note: This is a placeholder - real ONNX export would require
        # conversion of model weights to ONNX format

        onnx_file = output_path / "model.onnx"
        metadata_file = output_path / "metadata.json"

        # Save metadata
        with open(metadata_file, "w") as mf:
            json.dump(metadata, mf, indent=2)

        # Create placeholder ONNX file
        with open(onnx_file, "wb") as bf:
            # Placeholder for ONNX model data
            bf.write(b"ONNX_MODEL_PLACEHOLDER")

        package_info = {
            "format": "onnx",
            "files": ["model.onnx", "metadata.json"],
            "size": sum(f.stat().st_size for f in output_path.glob("*") if f.is_file()),
            "checksum": self._calculate_checksum(output_path),
        }

        logger.info(f"ONNX SLM exported successfully to {output_path}")
        return package_info

    async def _export_tensorrt(
        self, model_data: Dict[str, Any], output_path: Path, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export in TensorRT format."""
        # Note: This is a placeholder - real TensorRT export would require
        # TensorRT libraries and optimization

        trt_file = output_path / "model.trt"
        metadata_file = output_path / "metadata.json"

        # Save metadata
        with open(metadata_file, "w") as mf:
            json.dump(metadata, mf, indent=2)

        # Create placeholder TensorRT file
        with open(trt_file, "wb") as bf:
            # Placeholder for TensorRT engine data
            bf.write(b"TENSORRT_ENGINE_PLACEHOLDER")

        package_info = {
            "format": "tensorrt",
            "files": ["model.trt", "metadata.json"],
            "size": sum(f.stat().st_size for f in output_path.glob("*") if f.is_file()),
            "checksum": self._calculate_checksum(output_path),
        }

        logger.info(f"TensorRT SLM exported successfully to {output_path}")
        return package_info

    def _create_inference_script(self, output_path: Path) -> None:
        """Create a Python inference script for the SLM."""
        script_content = '''"""
Inference script for SLM model.

This script provides a simple interface to load and run inference
with the Small Language Model.
"""

import json
import pickle
from pathlib import Path
from typing import List, Optional


class SLMInference:
    """Simple inference interface for SLM models."""

    def __init__(self, model_path: Path):
        """Initialize with model path."""
        self.model_path = Path(model_path)
        self.metadata = None
        self.model_data = None
        self._load_model()

    def _load_model(self):
        """Load the model and metadata."""
        # Load metadata
        metadata_file = self.model_path / "metadata.json"
        with open(metadata_file, 'r') as mf:
            self.metadata = json.load(mf)

        # Load model weights
        weights_file = self.model_path / "model.weights"
        with open(weights_file, 'rb') as wf:
            self.model_data = pickle.load(wf)

        print(f"Loaded SLM model: {self.metadata['original_model']['id']}")
        print(f"Parameters: {self.model_data['parameters']:,}")

    def generate(self, prompt: str, max_length: int = 100) -> str:
        """Generate text from a prompt.

        Note: This is a placeholder implementation.
        Real inference would require the actual model runtime.
        """
        # Placeholder generation logic
        return f"Generated response for: {prompt[:50]}..."

    def get_info(self) -> dict:
        """Get model information."""
        return {
            "original_model": self.metadata["original_model"]["id"],
            "parameters": self.model_data["parameters"],
            "compression_ratio": self.metadata["slm_model"]["compression_ratio"],
            "quantization": self.metadata["slm_model"]["quantization"]
        }


def main():
    """Example usage."""
    model = SLMInference(Path("."))

    print("Model Info:", model.get_info())

    prompt = "Hello, how are you?"
    response = model.generate(prompt)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")


if __name__ == "__main__":
    main()
'''

        script_file = output_path / "inference.py"
        with open(script_file, "w") as sf:
            sf.write(script_content)

    def _calculate_checksum(self, directory: Path) -> str:
        """Calculate checksum for all files in directory."""
        import hashlib

        hasher = hashlib.md5()
        for file_path in sorted(directory.glob("*")):
            if file_path.is_file():
                with open(file_path, "rb") as bf:
                    hasher.update(bf.read())

        return hasher.hexdigest()

    async def create_package(self, model_path: Path, package_path: Path) -> Dict[str, Any]:
        """Create a distributable package from an SLM model."""
        logger.info(f"Creating package from {model_path} to {package_path}")

        with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in model_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(model_path)
                    zipf.write(file_path, arcname)

        package_info = {
            "package_path": str(package_path),
            "package_size": package_path.stat().st_size,
            "files_included": len(list(model_path.rglob("*"))),
            "created": "now",
        }

        logger.info(f"Package created successfully: {package_path}")
        return package_info
