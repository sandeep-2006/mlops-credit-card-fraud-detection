from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# URL for transaction service; default is the compose service name
TRANSACTION_URL = os.getenv("TRANSACTION_SERVICE_URL", "http://transaction-service:8080/transaction")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/transaction", methods=["POST"])
def proxy_transaction():
    payload = request.get_json(force=True)

    # Forward to transaction service
    try:
        resp = requests.post(TRANSACTION_URL, json=payload, timeout=5)
        resp.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": "transaction service unavailable", "details": str(e)}), 502

    # Pass through the transaction service response
    try:
        return jsonify(resp.json()), resp.status_code
    except ValueError:
        return jsonify({"error": "invalid response from transaction service"}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
