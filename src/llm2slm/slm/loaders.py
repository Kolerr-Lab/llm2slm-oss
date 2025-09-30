"""SLM model loaders.

This module provides loaders for different SLM model formats.
"""

import json
import pickle
from pathlib import Path

from .model import SLMModel


class SLMModelLoader:
    """Base class for SLM model loaders."""

    async def load_model(self, path: Path) -> SLMModel:
        """Load a model from the given path.

        Args:
            path: Path to the model file or directory

        Returns:
            Loaded SLM model
        """
        raise NotImplementedError


class PickleModelLoader(SLMModelLoader):
    """Loader for pickle format SLM models."""

    async def load_model(self, model_file: Path) -> SLMModel:
        """Load a pickle format SLM model."""
        with open(model_file, "rb") as f:
            data = pickle.load(f)

        metadata = data.get("metadata", {})
        model_data = data.get("model_data", {})

        return SLMModel(model_file.parent, metadata, model_data)


class NativeModelLoader(SLMModelLoader):
    """Loader for native format SLM models."""

    async def load_model(self, model_dir: Path) -> SLMModel:
        """Load a native format SLM model."""
        # Load metadata
        metadata_file = model_dir / "metadata.json"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        with open(metadata_file) as f:
            metadata = json.load(f)

        # Load model data
        weights_file = model_dir / "model.weights"
        if weights_file.exists():
            with open(weights_file, "rb") as f:
                model_data = pickle.load(f)
        else:
            # Fallback to metadata information
            model_data = metadata.get("slm_model", {})

        return SLMModel(model_dir, metadata, model_data)


class SLMModelLoaderFactory:
    """Factory for creating appropriate model loaders."""

    @staticmethod
    def get_loader(path: Path) -> SLMModelLoader:
        """Get the appropriate loader for the given path.

        Args:
            path: Path to the model file or directory

        Returns:
            Appropriate model loader instance

        Raises:
            ValueError: If no suitable loader is found
        """
        if path.is_file() and (path.suffix == ".pkl" or path.suffix == ".pickle"):
            return PickleModelLoader()
        elif path.is_dir():
            return NativeModelLoader()
        else:
            raise ValueError(f"Unsupported model format: {path}")
