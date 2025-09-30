"""SLM model representation.

This module contains the SLMModel class for representing loaded Small Language Models.
"""

import time
from pathlib import Path
from typing import Any, Dict


class SLMModel:
    """Loaded SLM model for inference."""

    def __init__(self, model_path: Path, metadata: Dict[str, Any], model_data: Dict[str, Any]):
        """Initialize SLM model.

        Args:
            model_path: Path to the model file or directory
            metadata: Model metadata dictionary
            model_data: Model data dictionary
        """
        self.model_path = model_path
        self.metadata = metadata
        self.model_data = model_data
        self.loaded_time = time.time()

    @property
    def model_id(self) -> str:
        """Get the original model ID."""
        return str(self.metadata.get("original_model", {}).get("id", "unknown"))  # type: ignore[no-any-return]

    @property
    def parameters(self) -> int:
        """Get number of parameters."""
        return int(self.model_data.get("parameters", 0))  # type: ignore[no-any-return]

    @property
    def size(self) -> int:
        """Get model size in bytes."""
        return int(self.model_data.get("size", 0))  # type: ignore[no-any-return]

    def get_info(self) -> Dict[str, Any]:
        """Get comprehensive model information."""
        return {
            "model_id": self.model_id,
            "parameters": self.parameters,
            "size": self.size,
            "compression_ratio": self.metadata.get("slm_model", {}).get("compression_ratio", 0),
            "quantization": self.metadata.get("slm_model", {}).get("quantization", "none"),
            "architecture": self.metadata.get("architecture", {}),
            "loaded_time": self.loaded_time,
            "runtime": self.metadata.get("runtime", {}),
        }
