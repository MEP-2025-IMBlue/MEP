# ─────────────────────────────────────────────────────────────────────────────
# File: metrics.py
# Purpose: Centralized Prometheus metric definitions and export logic
# Author: mRay Backend Team
# Notes: Metrics are reused from the global REGISTRY; avoids duplication
# ─────────────────────────────────────────────────────────────────────────────

from prometheus_client import (
    Summary,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY
)
from fastapi.responses import Response

# ─────────────────────────────────────────────────────────────────────────────
# Utility: Reuse or create a Gauge metric with specified labels
# Ensures metrics are not re-registered (avoids "Duplicated timeseries" error)
# ─────────────────────────────────────────────────────────────────────────────
def get_or_create_gauge(name: str, description: str, label_names: list) -> Gauge:
    """
    Returns existing Gauge or creates a new one with label support.
    """
    try:
        return REGISTRY._names_to_collectors[name]
    except KeyError:
        return Gauge(name, description, labelnames=label_names)

# ─────────────────────────────────────────────────────────────────────────────
# Utility: Reuse or create a Summary metric
# Used for request duration, latency, processing time etc.
# ─────────────────────────────────────────────────────────────────────────────
def get_or_create_summary(name: str, description: str) -> Summary:
    """
    Returns existing Summary or creates a new one.
    """
    try:
        return REGISTRY._names_to_collectors[name]
    except KeyError:
        return Summary(name, description)

# ─────────────────────────────────────────────────────────────────────────────
# Metric: Container CPU usage in percent
# Labels: container_id → allows per-container reporting
# ─────────────────────────────────────────────────────────────────────────────
CONTAINER_CPU_USAGE = get_or_create_gauge(
    name="container_cpu_usage",
    description="CPU usage per container in percent",
    label_names=["container_id"]
)

# ─────────────────────────────────────────────────────────────────────────────
# Metric: Container memory usage in bytes
# Labels: container_id → allows memory tracking per container
# ─────────────────────────────────────────────────────────────────────────────
CONTAINER_MEMORY_USAGE = get_or_create_gauge(
    name="container_memory_usage_bytes",
    description="Memory usage per container in bytes",
    label_names=["container_id"]
)

# ─────────────────────────────────────────────────────────────────────────────
# Metric: Request processing time
# Summary is ideal for capturing percentiles (P95, P99, etc.)
# ─────────────────────────────────────────────────────────────────────────────
REQUEST_TIME = get_or_create_summary(
    name="request_processing_seconds",
    description="Time spent processing request"
)

# ─────────────────────────────────────────────────────────────────────────────
# Function: /metrics endpoint response
# Returns current Prometheus metrics in text/plain format (OpenMetrics format)
# ─────────────────────────────────────────────────────────────────────────────
def generate_metrics_response() -> Response:
    """
    Exposes all registered metrics in Prometheus-compatible format.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
