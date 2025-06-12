# src/api/routes/routes_metrics.py
from fastapi import APIRouter
import time
from src.utils.metrics import REQUEST_TIME, generate_metrics_response

router = APIRouter()

@router.get("/metrics")
async def metrics():
    return generate_metrics_response()

@router.get("/metrics-test")
async def metrics_test():
    start = time.time()
    time.sleep(0.5)
    duration = time.time() - start
    REQUEST_TIME.observe(duration)  #METRİK speicherung
    return {"status": "ok"}
