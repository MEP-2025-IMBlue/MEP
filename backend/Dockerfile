FROM python:3.12-slim

# Setze Arbeitsverzeichnis
WORKDIR /app

# requirements installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Nur den Inhalt von src/ ins Container-Verzeichnis kopieren
COPY src/ .

# Starte FastAPI mit Uvicorn und berücksichtige den Pfad zu main.py
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
