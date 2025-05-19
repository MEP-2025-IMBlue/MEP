FROM python:3.12-slim

# Setze Arbeitsverzeichnis
WORKDIR /app

# PYTHONPATH setzen, damit 'services', 'api' gibi modüller tanınsın
ENV PYTHONPATH=/app

# requirements installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Nur den Inhalt von src/ ins Container-Verzeichnis kopieren
COPY src/ .

# Starte FastAPI mit Uvicorn und berücksichtige den Pfad zu main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]