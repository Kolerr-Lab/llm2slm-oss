"""SLM benchmarking functionality.

This module provides benchmarking capabilities for Small Language Models,
including performance metrics, memory usage estimation, and model comparison.
"""

import statistics
import time
from typing import Any, Callable, Dict, List, Optional

from .model import SLMModel


class SLMBenchmarker:
    """Benchmarker for Small Language Models."""

    def __init__(self) -> None:
        """Initialize the SLM benchmarker."""
        pass

    async def benchmark(
        self, model: SLMModel, generate_func: Callable, test_prompts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Benchmark an SLM model's performance.

        Args:
            model: Loaded SLM model
            generate_func: Async function to generate text
            test_prompts: List of test prompts (uses default if None)

        Returns:
            Benchmark results
        """
        if test_prompts is None:
            test_prompts = [
                "Hello, how are you?",
                "What is the capital of France?",
                "Explain quantum computing in simple terms.",
                "Write a short story about a robot.",
                "Translate 'hello world' to Spanish.",
            ]

        results: Dict[str, Any] = {
            "model_info": model.get_info(),
            "test_results": [],
            "performance_metrics": {},
        }
        test_results: List[Dict[str, Any]] = results["test_results"]

        latencies = []
        throughputs = []

        for _i, prompt in enumerate(test_prompts):
            start_time = time.time()
            response = await generate_func(model, prompt, max_length=50)
            end_time = time.time()

            latency = max(end_time - start_time, 0.001)  # Minimum 1ms to avoid division by zero
            throughput = len(response.split()) / latency  # words per second

            latencies.append(latency)
            throughputs.append(throughput)

            test_result = {
                "prompt": prompt,
                "response": response,
                "latency": latency,
                "throughput": throughput,
                "response_length": len(response),
            }
            test_results.append(test_result)  # type: ignore[attr-defined]

        # Calculate aggregate metrics
        results["performance_metrics"] = {
            "avg_latency": statistics.mean(latencies),
            "min_latency": min(latencies),
            "max_latency": max(latencies),
            "std_latency": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "avg_throughput": statistics.mean(throughputs),
            "min_throughput": min(throughputs),
            "max_throughput": max(throughputs),
            "total_tests": len(test_prompts),
            "memory_usage": self._estimate_memory_usage(model),
        }

        return results

    def _estimate_memory_usage(self, model: SLMModel) -> Dict[str, int]:
        """Estimate memory usage for the model."""
        # Rough estimation based on model size and parameters
        model_size = model.size
        runtime_overhead = model_size * 0.2  # 20% overhead estimate

        return {
            "model_size_bytes": model_size,
            "runtime_overhead_bytes": int(runtime_overhead),
            "total_estimated_bytes": int(model_size + runtime_overhead),
            "total_estimated_mb": int((model_size + runtime_overhead) / (1024 * 1024)),
        }

    def compare_models(
        self, benchmark_results: List[Dict[str, Any]], models: List[SLMModel]
    ) -> Dict[str, Any]:
        """Compare multiple SLM models based on benchmark results.

        Args:
            benchmark_results: List of benchmark results for each model
            models: List of SLM models

        Returns:
            Comparison results
        """
        comparison_results: Dict[str, Any] = {"models": [], "comparison_metrics": {}}
        models_list: List[Dict[str, Any]] = comparison_results["models"]

        # Add benchmark results to comparison
        for _i, (result, model) in enumerate(zip(benchmark_results, models)):
            models_list.append({"model_id": model.model_id, "benchmark": result})  # type: ignore[attr-defined]

        # Calculate comparison metrics
        if len(models) > 1:
            latencies = [
                result["benchmark"]["performance_metrics"]["avg_latency"] for result in models_list
            ]
            throughputs = [
                result["benchmark"]["performance_metrics"]["avg_throughput"]
                for result in models_list
            ]
            sizes = [model.size for model in models]

            comparison_results["comparison_metrics"] = {
                "fastest_model": models[latencies.index(min(latencies))].model_id,
                "highest_throughput": models[throughputs.index(max(throughputs))].model_id,
                "smallest_model": models[sizes.index(min(sizes))].model_id,
                "largest_model": models[sizes.index(max(sizes))].model_id,
                "latency_range": {"min": min(latencies), "max": max(latencies)},
                "throughput_range": {"min": min(throughputs), "max": max(throughputs)},
                "size_range": {"min": min(sizes), "max": max(sizes)},
            }

        return comparison_results
