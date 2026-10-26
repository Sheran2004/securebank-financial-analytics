import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest

# Project paths
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "transactions_analysis.csv"
OUTPUT_FILE = BASE_DIR / "data" / "anomaly_results.csv"

# Load transaction data
df = pd.read_csv(INPUT_FILE)
df.columns = df.columns.str.strip()

# Validate required columns
required_columns = [
    "transaction_id",
    "customer_name",
    "amount",
    "transaction_status",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns: {', '.join(missing_columns)}"
    )

# Prepare numerical features
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

if df["amount"].isna().any():
    raise ValueError("Some transaction amounts are missing or invalid.")

# Detect unusual transaction amounts
X = df[["amount"]].copy()

model = IsolationForest(
    n_estimators=100,
    contamination=0.1,
    random_state=42
)

df["anomaly_prediction"] = model.fit_predict(X)

# Convert predictions into readable labels
df["anomaly_status"] = df["anomaly_prediction"].map({
    1: "Normal",
    -1: "Unusual"
})

# Display results
print("\n========== ANOMALY DETECTION RESULTS ==========")

print(
    df[
        [
            "transaction_id",
            "customer_name",
            "amount",
            "transaction_status",
            "anomaly_prediction",
            "anomaly_status",
        ]
    ].to_string(index=False)
)

# Show unusual transactions
print("\n========== UNUSUAL TRANSACTIONS ==========")

unusual = df[df["anomaly_status"] == "Unusual"]

if unusual.empty:
    print("No unusual transactions detected.")
else:
    print(
        unusual[
            [
                "transaction_id",
                "customer_name",
                "amount",
                "transaction_status",
                "anomaly_prediction",
            ]
        ].to_string(index=False)
    )

# Save results for the dashboard
df.to_csv(OUTPUT_FILE, index=False)

print(f"\nResults saved to: {OUTPUT_FILE}")