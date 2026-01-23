"""OpenTelemetry tracing configuration."""

import structlog

from src.config import settings

logger = structlog.get_logger()


def setup_tracing() -> None:
    """Setup OpenTelemetry tracing."""
    if not settings.debug:
        # Only enable tracing in debug mode or when explicitly configured
        logger.info("tracing_disabled", reason="debug_mode_disabled")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

        # Create tracer provider
        provider = TracerProvider()
        trace.set_tracer_provider(provider)

        # Add console exporter (for development)
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))

        logger.info("tracing_initialized", exporter="console")
    except ImportError:
        logger.warning(
            "opentelemetry_not_available",
            message="OpenTelemetry packages not installed. Install with: pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi",
        )
    except Exception as e:
        logger.error("tracing_setup_failed", error=str(e))


def get_tracer(name: str):
    """Get a tracer instance."""
    try:
        from opentelemetry import trace

        return trace.get_tracer(name)
    except ImportError:
        return None
