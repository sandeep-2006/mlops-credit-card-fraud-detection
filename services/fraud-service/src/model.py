import os
import joblib
import numpy as np


class FraudModel:
    def __init__(self):
        here = os.path.dirname(__file__)
        models_dir = os.path.abspath(os.path.join(here, "..", "models"))
        # fallback to repo training/models if service models folder not populated
        repo_models_dir = os.path.abspath(os.path.join(here, "..", "..", "..", "training", "models"))
        if not os.path.exists(models_dir) and os.path.exists(repo_models_dir):
            models_dir = repo_models_dir
        # expected model and scaler names
        model_path = os.path.join(models_dir, "logistic.joblib")
        scaler_path = os.path.join(models_dir, "amount_scaler.joblib")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")

        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None

    def _scale_amount(self, X):
        if self.scaler is None:
            return X
        X = X.copy()
        X["Amount"] = self.scaler.transform(X[["Amount"]])
        return X

    def predict_proba(self, X):
        Xs = self._scale_amount(X)
        probs = self.model.predict_proba(Xs)[:, 1]
        # return as Nx1 column vector for compatibility with caller
        return np.array(probs).reshape(-1, 1)
