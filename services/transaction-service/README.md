# Transaction Service

Purpose:
To handle incoming transaction requests, forward the transaction to the Fraud Service for scoring, and return the final transaction outcome (`approved` or `flagged`) along with the fraud probability.

Usage:

Build the image from the repository root:

```bash
docker build -t transaction-service:latest -f services/transaction-service/Dockerfile .
```

Run (example, assuming fraud-service is reachable at `http://fraud-service:8080`):

```bash
docker run --rm -p 8082:8080 -e FRAUD_SERVICE_URL=http://<fraud-host>:8080/predict transaction-service:latest
```

Endpoints:
- `GET /health` — service health
- `POST /transaction` — accept transaction JSON and return `{ "outcome": "approved"|"flagged", "probability": 0.123, "threshold": 0.5 }`

Configuration:
- `FRAUD_SERVICE_URL`: full URL to the fraud service predict endpoint (default: `http://fraud-service:8080/predict`)
- `FRAUD_THRESHOLD`: probability threshold to mark a transaction as flagged (default: `0.5`)
