# Fraud Service

Simple Flask-based service that exposes a `/predict` endpoint to score transactions.

Build the Docker image from the repository root:

```bash
docker build -t fraud-service:latest -f services/fraud-service/Dockerfile .
```

Run locally:

```bash
docker run -p 8080:8080 fraud-service:latest
```

Example request:

```bash
curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" -d '{"V1": -1.23, "V2": 0.12, "Amount": 100.0}'
```