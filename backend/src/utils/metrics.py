from prometheus_client import Summary, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from fastapi.responses import Response

# Metriği tekrar oluşturmamak için kontrol
metric_name = "request_processing_seconds"
existing = [m for m in REGISTRY.collect() if m.name == metric_name]

if existing:
    REQUEST_TIME = next(m for m in REGISTRY.collect() if m.name == metric_name)
else:
    REQUEST_TIME = Summary(metric_name, "Time spent processing request")

def generate_metrics_response():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
