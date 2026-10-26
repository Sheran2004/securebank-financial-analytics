import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Load database credentials
load_dotenv(BASE_DIR / ".env")

db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "securebank_analytics"),
}

if not db_config["password"]:
    raise ValueError(
        "DB_PASSWORD is missing. Please check your .env file."
    )

# Create a safe database URL
connection_url = URL.create(
    drivername="mysql+mysqlconnector",
    username=db_config["user"],
    password=db_config["password"],
    host=db_config["host"],
    database=db_config["database"],
)

engine = create_engine(connection_url)

# SQL query
query = """
SELECT
    t.transaction_id,
    c.customer_name,
    c.city,
    c.risk_category,
    t.transaction_date,
    t.transaction_type,
    t.amount,
    t.merchant_category,
    t.transaction_status
FROM transactions t
JOIN customers c
    ON t.customer_id = c.customer_id;
"""

try:
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    print("\n========== TRANSACTION DATA ==========")
    print(df.head())

    print("\n========== DATASET SUMMARY ==========")
    print(f"Total Transactions: {len(df)}")
    print(f"Total Transaction Amount: Rs. {df['amount'].sum():,.2f}")
    print(f"Average Transaction Amount: Rs. {df['amount'].mean():,.2f}")

    print("\n========== TRANSACTION STATUS ==========")
    print(df["transaction_status"].value_counts())

    print("\n========== CATEGORY-WISE ANALYSIS ==========")
    category_analysis = (
        df.groupby("merchant_category")
        .agg(
            total_transactions=("transaction_id", "count"),
            total_amount=("amount", "sum"),
        )
        .sort_values("total_amount", ascending=False)
    )
    print(category_analysis)

    print("\n========== FAILED TRANSACTIONS ==========")
    failed = df[df["transaction_status"] == "Failed"]
    print(
        failed[
            [
                "transaction_id",
                "customer_name",
                "amount",
                "merchant_category",
            ]
        ]
    )

    output_file = DATA_DIR / "transactions_analysis.csv"
    df.to_csv(output_file, index=False)
    print(f"\nAnalysis complete! CSV file saved to: {output_file}")

except Exception as error:
    print("MySQL connection or analysis failed!")
    print(error)

finally:
    engine.dispose()
