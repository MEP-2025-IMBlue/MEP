FROM node:20-slim

WORKDIR /app

RUN npm install -g http-server

COPY src/ .

CMD ["http-server", ".", "-p", "8080"]
