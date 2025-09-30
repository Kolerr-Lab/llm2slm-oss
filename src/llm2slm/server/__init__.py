import logging

from .app import app

"""
llm2slm.server module

This module provides the FastAPI-based REST API server for the LLM to SLM conversion service.
It includes configuration, routing, middleware, and production-ready setup for deployment.
"""


async def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """
    Run the FastAPI server for the LLM2SLM API.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to
    """
    try:
        import uvicorn

        logging.info(f"Starting server on {host}:{port}")
        uvicorn.run("llm2slm.server.app:app", host=host, port=port, reload=False, log_level="info")
    except ImportError:
        logging.error("uvicorn not installed. Please install it with: pip install uvicorn")
        raise
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        raise


__all__ = ["app", "run_server"]
