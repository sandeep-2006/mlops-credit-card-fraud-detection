from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# URL of the fraud service predict endpoint (override via env)
FRAUD_URL = os.getenv("FRAUD_SERVICE_URL", "http://fraud-service:8080/predict")
# probability threshold to flag a transaction as fraud
THRESHOLD = float(os.getenv("FRAUD_THRESHOLD", "0.5"))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/transaction", methods=["POST"])
def transaction():
    payload = request.get_json(force=True)

    # forward to fraud service
    try:
        # Send the payload as-is; fraud service accepts single object or list
        resp = requests.post(FRAUD_URL, json=payload, timeout=5)
        resp.raise_for_status()
        pred = resp.json()

        # Normalize response: expect a list of prediction objects
        if isinstance(pred, list):
            first = pred[0]
        elif isinstance(pred, dict):
            first = pred
        else:
            return jsonify({"error": "unexpected response from fraud service"}), 502

        prob = float(first.get("probability", 0.0))
        outcome = "flagged" if prob >= THRESHOLD else "approved"

        return jsonify({"outcome": outcome, "probability": prob, "threshold": THRESHOLD})

    except requests.RequestException as e:
        return jsonify({"error": "failed to contact fraud service", "details": str(e)}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
