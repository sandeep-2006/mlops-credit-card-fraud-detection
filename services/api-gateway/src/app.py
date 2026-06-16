from flask import Flask, request, jsonify
import os
import requests
from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)

# URL for transaction service; default is the compose service name
TRANSACTION_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://transaction-service:8080/transaction")

# Prometheus metrics
request_count = Counter('gateway_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('gateway_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
transaction_errors = Counter('gateway_transaction_errors_total', 'Transaction errors', ['error_type'])


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest()


@app.route("/transaction", methods=["POST"])
def proxy_transaction():
    import time
    start = time.time()
    payload = request.get_json(force=True)

    # Forward to transaction service
    try:
        resp = requests.post(TRANSACTION_URL, json=payload, timeout=5)
        resp.raise_for_status()
        request_count.labels(method='POST', endpoint='/transaction', status=resp.status_code).inc()
        request_duration.labels(method='POST', endpoint='/transaction').observe(time.time() - start)
    except requests.RequestException as e:
        transaction_errors.labels(error_type='service_unavailable').inc()
        request_count.labels(method='POST', endpoint='/transaction', status=502).inc()
        request_duration.labels(method='POST', endpoint='/transaction').observe(time.time() - start)
        return jsonify({"error": "transaction service unavailable", "details": str(e)}), 502

    # Pass through the transaction service response
    try:
        return jsonify(resp.json()), resp.status_code
    except ValueError:
        transaction_errors.labels(error_type='invalid_response').inc()
        request_count.labels(method='POST', endpoint='/transaction', status=502).inc()
        request_duration.labels(method='POST', endpoint='/transaction').observe(time.time() - start)
        return jsonify({"error": "invalid response from transaction service"}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
