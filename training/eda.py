import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


def preprocess(csv_path: str = "creditcard.csv", out_dir: str = "processed", test_size: float = 0.2, random_state: int = 42):
	"""Basic preprocessing for the creditcard dataset.

	Steps:
	- load CSV
	- drop duplicates
	- drop `Time` column if present
	- scale `Amount` with `StandardScaler`
	- split into train/test with stratification on the `Class` label
	- save `X_train`, `X_test`, `y_train`, `y_test` and the scaler in `out_dir`
	"""
	# load
	df = pd.read_csv(csv_path)
	print(f"Loaded {csv_path} with shape: {df.shape}")

	# basic checks
	missing = df.isnull().sum().sum()
	print(f"Total missing values: {missing}")

	# drop duplicates
	before = len(df)
	df = df.drop_duplicates()
	after = len(df)
	print(f"Dropped {before - after} duplicate rows")

	# drop Time if present
	if "Time" in df.columns:
		df = df.drop(columns=["Time"])
		print("Dropped column: Time")

	# scale Amount
	if "Amount" in df.columns:
		scaler = StandardScaler()
		df["Amount"] = scaler.fit_transform(df[["Amount"]])
		print("Scaled column: Amount")
	else:
		scaler = None

	# split features / label
	if "Class" not in df.columns:
		raise ValueError("Expected target column 'Class' not found in dataset")

	X = df.drop(columns=["Class"])
	y = df["Class"]

	X_train, X_test, y_train, y_test = train_test_split(
		X, y, test_size=test_size, random_state=random_state, stratify=y
	)

	os.makedirs(out_dir, exist_ok=True)
	X_train.to_csv(os.path.join(out_dir, "X_train.csv"), index=False)
	X_test.to_csv(os.path.join(out_dir, "X_test.csv"), index=False)
	y_train.to_csv(os.path.join(out_dir, "y_train.csv"), index=False)
	y_test.to_csv(os.path.join(out_dir, "y_test.csv"), index=False)

	# save scaler for later use
	if scaler is not None:
		try:
			import joblib

			joblib.dump(scaler, os.path.join(out_dir, "amount_scaler.joblib"))
			print("Saved scaler to amount_scaler.joblib")
		except Exception:
			print("joblib not available; skipping scaler save")

	print("Preprocessing complete. Processed files saved in:", out_dir)
	return {
		"X_train": os.path.join(out_dir, "X_train.csv"),
		"X_test": os.path.join(out_dir, "X_test.csv"),
		"y_train": os.path.join(out_dir, "y_train.csv"),
		"y_test": os.path.join(out_dir, "y_test.csv"),
	}


if __name__ == "__main__":
	preprocess(csv_path="creditcard.csv", out_dir="processed", test_size=0.2, random_state=42)

