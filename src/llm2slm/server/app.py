import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

"""
FastAPI application for the LLM2SLM server.

This module defines the main FastAPI application, including routes for health checks,
model conversion operations, and other API endpoints. It is designed for production
deployment with proper error handling, logging, and async patterns.
"""


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # type: ignore[no-untyped-def]
    """Handle application startup and shutdown events."""
    logger.info("Starting LLM2SLM server...")
    # Add any startup logic here, e.g., initializing connections
    yield
    logger.info("Shutting down LLM2SLM server...")
    # Add any shutdown logic here, e.g., closing connections


# Create FastAPI app instance
app = FastAPI(
    title="LLM2SLM API",
    description="API for converting Large Language Models to Small Language Models",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware for production deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str
    version: str


class ConversionRequest(BaseModel):
    """Request model for model conversion."""

    model_name: str
    parameters: Dict[str, Any]


class ConversionResponse(BaseModel):
    """Response model for model conversion."""

    message: str
    result: Dict[str, Any]


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # type: ignore[no-untyped-def]
    """Handle unexpected exceptions globally."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns the current status and version of the API.
    """
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/convert", response_model=ConversionResponse)
async def convert_model(request: ConversionRequest) -> ConversionResponse:
    """
    Convert a Large Language Model to a Small Language Model.

    This is a placeholder implementation. In a real scenario, integrate with
    the core conversion logic from the llm2slm package.
    """
    try:
        # Placeholder for actual conversion logic
        logger.info(f"Converting model: {request.model_name}")
        # Simulate conversion process
        result = {"converted_model": request.model_name, "status": "success"}
        return ConversionResponse(
            message="Model conversion initiated successfully",
            result=result,
        )
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        raise HTTPException(status_code=500, detail="Conversion failed") from e


# Additional routes can be added here as needed


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    This function creates a new FastAPI app instance with all routes,
    middleware, and configuration. It's used by the ASGI server (uvicorn/gunicorn)
    to start the application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    return app
