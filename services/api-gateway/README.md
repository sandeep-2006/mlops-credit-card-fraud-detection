# API Gateway

Purpose:
The API Gateway receives requests from clients or the frontend and routes transaction-related requests to the Transaction Service. It returns the Transaction Service response back to the client. Cross-cutting concerns (auth, rate-limiting, logging) can be added later.

Endpoints:
- `GET /health` — health check
- `POST /transaction` — forwards request body to Transaction Service and returns its response

Configuration:
- `TRANSACTION_SERVICE_URL` — full URL to the Transaction Service endpoint (default: `http://transaction-service:8080/transaction`)

Build & run:

```bash
docker build -t api-gateway:latest -f services/api-gateway/Dockerfile .
docker run --rm -p 8080:8080 -e TRANSACTION_SERVICE_URL=http://<host>:8082/transaction api-gateway:latest
```
