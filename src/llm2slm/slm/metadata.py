"""SLM metadata creation.

This module provides functionality for creating metadata for Small Language Models.
"""

from typing import Any, Dict


class SLMMetadataCreator:
    """Creator for SLM metadata."""

    @staticmethod
    def create_metadata(model_data: Dict[str, Any], model_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create SLM metadata.

        Args:
            model_data: The compressed model data
            model_info: Original model information

        Returns:
            SLM metadata dictionary
        """
        return {
            "format_version": "1.0",
            "created_with": "llm2slm",
            "original_model": {
                "id": model_info.get("model_id", "unknown"),
                "provider": model_info.get("provider", "unknown"),
                "parameters": model_info.get("parameters", 0),
                "size": model_info.get("size", 0),
            },
            "slm_model": {
                "parameters": model_data.get("parameters", 0),
                "size": model_data.get("size", 0),
                "compression_ratio": model_data.get("compression_ratio", 0.5),
                "quantization": model_data.get("quantization", "none"),
                "pruned": model_data.get("pruned", False),
                "distilled": model_data.get("distilled", False),
            },
            "architecture": {
                "type": model_data.get("architecture", "transformer"),
                "layers": model_data.get("layers", []),
                "hidden_size": model_data.get("hidden_size", 0),
                "attention_heads": model_data.get("attention_heads", 0),
            },
            "tokenizer": model_data.get("tokenizer", {}),
            "runtime": {
                "inference_engine": "native",
                "supported_backends": ["cpu", "gpu"],
                "memory_requirements": model_data.get("size", 0),
            },
        }
