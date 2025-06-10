from prometheus_client import Summary, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from fastapi.responses import Response

#  Hilfsfunktion: Holt vorhandenen Metriknamen aus dem Registry oder erstellt neuen
def get_or_create_gauge(name, beschreibung, labels):
    try:
        return REGISTRY._names_to_collectors[name]
    except KeyError:
        return Gauge(name, beschreibung, labels)

def get_or_create_summary(name, beschreibung):
    try:
        return REGISTRY._names_to_collectors[name]
    except KeyError:
        return Summary(name, beschreibung)

#  Gauge-Metriken für Container-Ressourcennutzung
CONTAINER_CPU_USAGE = get_or_create_gauge("container_cpu_usage", "CPU-Auslastung in Prozent", ["container_id"])
CONTAINER_MEMORY_USAGE = get_or_create_gauge("container_memory_usage_bytes", "Speichernutzung in Bytes", ["container_id"])

# ⏱ Summary-Metrik für Request-Zeitmessung
REQUEST_TIME = get_or_create_summary("request_processing_seconds", "Verarbeitungszeit pro Anfrage")

#  Antwortfunktion für Prometheus /metrics-Endpunkt
def generate_metrics_response():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
