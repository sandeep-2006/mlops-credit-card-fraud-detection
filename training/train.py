import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
	precision_recall_curve,
	roc_auc_score,
	auc,
	classification_report,
	confusion_matrix,
	roc_curve,
)


def recall_at_fpr(y_true, y_scores, fpr_target: float = 0.01):
	fpr, tpr, thresholds = roc_curve(y_true, y_scores)
	# find the max tpr where fpr <= fpr_target
	valid = np.where(fpr <= fpr_target)[0]
	if valid.size == 0:
		return 0.0
	return float(np.max(tpr[valid]))


def pr_auc(y_true, y_scores):
	p, r, _ = precision_recall_curve(y_true, y_scores)
	return float(auc(r, p))


def train_and_eval(X_train, X_test, y_train, y_test, out_dir):
	os.makedirs(out_dir, exist_ok=True)

	results = {}

	# Baseline: LogisticRegression
	print("Training LogisticRegression (class_weight='balanced')")
	lr = LogisticRegression(max_iter=1000, class_weight="balanced", solver="liblinear")
	lr.fit(X_train, y_train)
	y_scores = lr.predict_proba(X_test)[:, 1]
	results["logistic"] = {
		"pr_auc": pr_auc(y_test, y_scores),
		"roc_auc": roc_auc_score(y_test, y_scores),
		"recall_at_fpr_0.01": recall_at_fpr(y_test, y_scores, 0.01),
	}
	print("Logistic results:", results["logistic"])
	joblib.dump(lr, os.path.join(out_dir, "logistic.joblib"))

	# (Removed XGBoost and LightGBM training — LogisticRegression baseline only)

	# Print a short classification report for baseline at default threshold 0.5
	lr_pred = (lr.predict_proba(X_test)[:, 1] >= 0.5).astype(int)
	print("Classification report (Logistic, thresh=0.5):")
	print(classification_report(y_test, lr_pred))
	print("Confusion matrix:")
	print(confusion_matrix(y_test, lr_pred))

	# Save results summary
	with open(os.path.join(out_dir, "results_summary.txt"), "w") as fh:
		fh.write(str(results))

	return results


def load_processed(processed_dir):
	paths = {
		"X_train": os.path.join(processed_dir, "X_train.csv"),
		"X_test": os.path.join(processed_dir, "X_test.csv"),
		"y_train": os.path.join(processed_dir, "y_train.csv"),
		"y_test": os.path.join(processed_dir, "y_test.csv"),
	}
	for k, p in paths.items():
		if not os.path.exists(p):
			return None

	X_train = pd.read_csv(paths["X_train"]) 
	X_test = pd.read_csv(paths["X_test"]) 
	y_train = pd.read_csv(paths["y_train"]).squeeze()
	y_test = pd.read_csv(paths["y_test"]).squeeze()
	return X_train, X_test, y_train, y_test


if __name__ == "__main__":
	here = os.path.dirname(__file__)
	processed_dir = os.path.join(here, "processed")

	# If processed data not present, run preprocess
	data = load_processed(processed_dir)
	if data is None:
		print("Processed data not found in", processed_dir)
		print("Running preprocessing to generate processed files...")
		try:
			# Run eda.py with the same Python executable to avoid launcher issues
			import subprocess, sys

			# support either eda.py or processed.py (file created earlier)
			candidate1 = os.path.join(here, "eda.py")
			candidate2 = os.path.join(here, "processed.py")
			if os.path.exists(candidate1):
				eda_file = candidate1
			elif os.path.exists(candidate2):
				eda_file = candidate2
			else:
				raise FileNotFoundError("Neither eda.py nor processed.py found in training folder")
			print("Running", eda_file, "with", sys.executable)
			subprocess.check_call([sys.executable, eda_file], cwd=here)
		except Exception as e:
			print("Failed to run preprocessing via subprocess:", e)
			raise
		data = load_processed(processed_dir)

	X_train, X_test, y_train, y_test = data

	out_dir = os.path.join(here, "models")
	results = train_and_eval(X_train, X_test, y_train, y_test, out_dir)
	print("All done. Results written to", out_dir)

