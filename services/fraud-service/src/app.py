from flask import Flask, request, jsonify
import os
import pandas as pd

from model import FraudModel

app = Flask(__name__)
model = FraudModel()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(force=True)

    # accept either single record (dict) or list of records
    if isinstance(payload, dict):
        records = [payload]
    else:
        records = payload

    df = pd.json_normalize(records)

    # expected features (V1..V28 and Amount). If missing, fill with 0.
    expected = [f"V{i}" for i in range(1, 29)] + ["Amount"]
    for c in expected:
        if c not in df.columns:
            df[c] = 0.0

    X = df[expected]

    probs = model.predict_proba(X)
    preds = (probs >= 0.5).astype(int)

    out = []
    for p, pr in zip(preds.tolist(), probs.tolist()):
        out.append({"prediction": int(p[0]), "probability": float(pr[0])})

    return jsonify(out)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
