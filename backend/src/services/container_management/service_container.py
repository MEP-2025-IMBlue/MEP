# ─────────────────────────────────────────────────────────────────────────────
# File: routes_metrics.py
# Purpose: Expose Prometheus metrics for observability & monitoring
# Author: mRay Backend Team
# Endpoint: /metrics – Prometheus-compatible metrics endpoint
# ─────────────────────────────────────────────────────────────────────────────

from fastapi import APIRouter
import time

from src.utils.metrics import REQUEST_TIME, generate_metrics_response

router = APIRouter()

# ─────────────────────────────────────────────────────────────────────────────
# GET /metrics
# Returns all registered Prometheus metrics (used by Prometheus scrape jobs)
# Response: text/plain in Prometheus exposition format
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/metrics")
async def metrics():
    return generate_metrics_response()

# ─────────────────────────────────────────────────────────────────────────────
# GET /metrics-test
# Example endpoint to simulate a timed request and expose duration via metric
# Metric: REQUEST_TIME (Histogram or Summary)
# Usage: Validate that metrics are being recorded and exported correctly
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/metrics-test")
async def metrics_test():
    start = time.time()
    time.sleep(0.5)  # Simulate processing delay (500ms)
    duration = time.time() - start

    REQUEST_TIME.observe(duration)  # ⏱ Record request duration in seconds

    return {"status": "ok"}
