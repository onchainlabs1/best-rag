"""FastAPI application."""

import time
from collections.abc import Awaitable, Callable

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import Response

from src import __version__
from src.api.v1 import agents, documents, health, queries
from src.config import settings
from src.observability.tracing import setup_tracing

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="RAG + Agent Knowledge Base",
    description="Knowledge Base system using RAG with LangGraph agents",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - configurable via environment
cors_origins_str = getattr(settings, "cors_origins", "*")
if cors_origins_str == "*":
    cors_origins = ["*"]
    if not settings.debug:
        logger.warning("CORS allows all origins - configure CORS_ORIGINS for production")
else:
    cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add timeout middleware for long-running requests
@app.middleware("http")
async def timeout_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Add timeout handling for long requests."""
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        logger.error("request_error", error=str(e), path=request.url.path)
        return JSONResponse(status_code=500, content={"detail": f"Request failed: {str(e)}"})


# Include routers
app.include_router(documents.router, prefix="/api/v1")
app.include_router(queries.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")

# Set rate limiter in router modules after app is created
documents.limiter = limiter
queries.limiter = limiter
agents.limiter = limiter


@app.on_event("startup")
async def startup_event() -> None:
    """Startup event handler."""
    logger.info("application_starting", version=__version__, debug=settings.debug)

    # Setup OpenTelemetry tracing
    setup_tracing()

    # Instrument FastAPI if tracing is enabled
    if settings.debug:
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # noqa: F401

            FastAPIInstrumentor.instrument_app(app)
            logger.info("fastapi_instrumented_for_tracing")
        except ImportError:
            pass  # OpenTelemetry not available


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Shutdown event handler."""
    logger.info("application_shutting_down")


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "RAG + Agent Knowledge Base API",
        "version": __version__,
        "docs": "/docs",
    }
