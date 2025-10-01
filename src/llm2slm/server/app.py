import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

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

# Check for privacy module availability
try:
    from llm2slm.privacy import (
        AnonymizationConfig,
        AnonymizationMethod,
        ContentCategory,
        ContentFilter,
        FilterAction,
        FilterConfig,
        PIIAnonymizer,
        PrivacyLevel,
        PrivacyValidator,
        detoxify_available,
        presidio_available,
    )

    PRIVACY_AVAILABLE = True
except ImportError:
    PRIVACY_AVAILABLE = False
    logger.warning("Privacy module not available. Install with: pip install llm2slm[privacy]")


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


# Privacy API models
class AnonymizeRequest(BaseModel):
    """Request model for PII anonymization."""

    text: str = Field(..., description="Text to anonymize")
    method: str = Field(
        default="mask", description="Anonymization method: mask, redact, replace, hash, encrypt"
    )
    entities: list[str] = Field(
        default=["EMAIL_ADDRESS", "PHONE_NUMBER"],
        description="PII entities to detect and anonymize",
    )
    score_threshold: float = Field(
        default=0.6, ge=0.0, le=1.0, description="Detection confidence threshold"
    )


class AnonymizeResponse(BaseModel):
    """Response model for PII anonymization."""

    original_text: str
    anonymized_text: str
    pii_detected: int
    entities_found: list[str]
    method_used: str


class FilterRequest(BaseModel):
    """Request model for content filtering."""

    text: str = Field(..., description="Text to filter")
    action: str = Field(default="flag", description="Filter action: allow, flag, redact, reject")
    categories: list[str] = Field(
        default=["toxicity", "severe_toxicity"],
        description="Content categories to check",
    )
    threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Detection threshold")


class FilterResponse(BaseModel):
    """Response model for content filtering."""

    original_text: str
    filtered_text: str
    passed: bool
    violations: list[Dict[str, Any]]
    scores: Dict[str, float]
    action_taken: str


class ValidateRequest(BaseModel):
    """Request model for privacy validation."""

    text: str = Field(..., description="Text to validate")
    level: str = Field(
        default="medium", description="Privacy level: none, low, medium, high, strict"
    )
    check_pii: bool = Field(default=True, description="Check for PII")
    check_content: bool = Field(default=True, description="Check content policy")


class ValidateResponse(BaseModel):
    """Response model for privacy validation."""

    passed: bool
    level: str
    pii_detected: bool
    pii_count: int
    content_violations: list[Dict[str, Any]]
    recommendations: list[str]


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


# Privacy API endpoints
@app.post("/anonymize", response_model=AnonymizeResponse)
async def anonymize_text(request: AnonymizeRequest) -> AnonymizeResponse:
    """
    Anonymize PII in text.

    Detects and anonymizes Personally Identifiable Information (PII) such as
    emails, phone numbers, SSN, credit cards, names, etc.

    Requires privacy module: pip install llm2slm[privacy]
    """
    if not PRIVACY_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Privacy module not installed. Install with: pip install llm2slm[privacy]",
        )

    try:
        # Validate anonymization method
        try:
            method = AnonymizationMethod(request.method)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid method '{request.method}'. Use: mask, redact, replace, hash, encrypt",
            )

        # Configure anonymizer
        config = AnonymizationConfig(
            enabled=True,
            method=method,
            entities=set(request.entities),
            score_threshold=request.score_threshold,
        )

        # Initialize anonymizer
        anonymizer: Any
        if presidio_available():
            anonymizer = PIIAnonymizer(config)
        else:
            from llm2slm.privacy.anonymizer import RegexPIIAnonymizer

            anonymizer = RegexPIIAnonymizer(config)
            logger.warning("Using regex-based anonymizer (Presidio not available)")

        # Detect PII
        pii_entities = anonymizer.detect_pii(request.text)
        entity_types = list(set(e["entity_type"] for e in pii_entities))

        # Anonymize text
        anonymized = anonymizer.anonymize(request.text)

        logger.info(f"Anonymized text with {len(pii_entities)} PII entities detected")

        return AnonymizeResponse(
            original_text=request.text,
            anonymized_text=anonymized,
            pii_detected=len(pii_entities),
            entities_found=entity_types,
            method_used=request.method,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during anonymization: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Anonymization failed: {str(e)}") from e


@app.post("/filter", response_model=FilterResponse)
async def filter_content(request: FilterRequest) -> FilterResponse:
    """
    Filter harmful content in text.

    Detects and filters toxic, profane, hateful, or harmful content using
    ML-based semantic analysis.

    Requires privacy module: pip install llm2slm[privacy]
    """
    if not PRIVACY_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Privacy module not installed. Install with: pip install llm2slm[privacy]",
        )

    try:
        # Validate filter action
        try:
            action = FilterAction(request.action)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action '{request.action}'. Use: allow, flag, redact, reject",
            )

        # Convert category strings to enums
        categories = set()
        for cat in request.categories:
            try:
                categories.add(ContentCategory(cat))
            except ValueError:
                logger.warning(f"Unknown category '{cat}', skipping")

        if not categories:
            raise HTTPException(
                status_code=400, detail="At least one valid category must be specified"
            )

        # Configure filter
        config = FilterConfig(
            enabled=True,
            categories=categories,
            action=action,
            thresholds={cat: request.threshold for cat in categories},
        )

        # Initialize filter
        content_filter: Any
        if detoxify_available():
            content_filter = ContentFilter(config)
        else:
            from llm2slm.privacy.filter import RegexContentFilter

            content_filter = RegexContentFilter(config)
            logger.warning("Using regex-based filter (Detoxify not available)")

        # Filter content
        result = content_filter.filter(request.text)

        logger.info(
            f"Filtered content: passed={result.passed}, violations={len(result.violations)}"
        )

        return FilterResponse(
            original_text=request.text,
            filtered_text=result.text,
            passed=result.passed,
            violations=result.violations,
            scores=result.scores,
            action_taken=result.action_taken.value,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during content filtering: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Content filtering failed: {str(e)}") from e


@app.post("/validate", response_model=ValidateResponse)
async def validate_privacy(request: ValidateRequest) -> ValidateResponse:
    """
    Validate text for privacy compliance.

    Performs comprehensive privacy validation including PII detection and
    content policy checks based on specified privacy level.

    Requires privacy module: pip install llm2slm[privacy]
    """
    if not PRIVACY_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Privacy module not installed. Install with: pip install llm2slm[privacy]",
        )

    try:
        # Validate privacy level
        try:
            level = PrivacyLevel(request.level)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid level '{request.level}'. Use: none, low, medium, high, strict",
            )

        # Initialize validator
        validator = PrivacyValidator(level=level)

        # Initialize anonymizer if needed
        anonymizer: Any = None
        if request.check_pii:
            anon_config = AnonymizationConfig(enabled=True)
            if presidio_available():
                anonymizer = PIIAnonymizer(anon_config)
            else:
                from llm2slm.privacy.anonymizer import RegexPIIAnonymizer

                anonymizer = RegexPIIAnonymizer(anon_config)

        # Initialize content filter if needed
        content_filter: Any = None
        if request.check_content:
            filter_config = FilterConfig(enabled=True)
            if detoxify_available():
                content_filter = ContentFilter(filter_config)
            else:
                from llm2slm.privacy.filter import RegexContentFilter

                content_filter = RegexContentFilter(filter_config)

        # Validate
        result = validator.validate(request.text, anonymizer, content_filter)

        logger.info(
            f"Privacy validation: passed={result.passed}, level={level.value}, "
            f"pii_detected={result.pii_detected}, violations={len(result.content_violations)}"
        )

        return ValidateResponse(
            passed=result.passed,
            level=result.level.value,
            pii_detected=result.pii_detected,
            pii_count=result.pii_count,
            content_violations=result.content_violations,
            recommendations=result.recommendations,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during privacy validation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Privacy validation failed: {str(e)}") from e


@app.get("/privacy/status")
async def privacy_status() -> Dict[str, Any]:
    """
    Get privacy module status and capabilities.

    Returns information about which privacy features are available.
    """
    return {
        "privacy_module_available": PRIVACY_AVAILABLE,
        "presidio_available": presidio_available() if PRIVACY_AVAILABLE else False,
        "detoxify_available": detoxify_available() if PRIVACY_AVAILABLE else False,
        "features": {
            "anonymization": presidio_available() if PRIVACY_AVAILABLE else False,
            "content_filtering": detoxify_available() if PRIVACY_AVAILABLE else False,
            "privacy_validation": PRIVACY_AVAILABLE,
            "fallback_available": True,  # Regex-based fallbacks always available
        },
        "installation_command": "pip install llm2slm[privacy]",
    }


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
