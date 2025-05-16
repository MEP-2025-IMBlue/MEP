FROM node:20-slim

WORKDIR /app

RUN npm install -g http-server

# Alles im aktuellen Verzeichnis kopieren (inkl. index.html, index.js, src/)
COPY . .

CMD ["http-server", ".", "-p", "8080"]
