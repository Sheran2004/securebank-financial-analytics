import io
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.ensemble import IsolationForest
from auth import render_auth, render_logout

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="SecureBank Financial Analytics",
    page_icon="🔐",
    layout="wide",
)

# =========================================================
# AUTHENTICATION
# =========================================================

if not render_auth():
    st.stop()

render_logout()

# Keep the sidebar expanded on the deployed app
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            width: 300px !important;
            min-width: 300px !important;
            transform: none !important;
        }

        [data-testid="stSidebar"] > div {
            width: 300px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "anomaly_results.csv"

REQUIRED_COLUMNS = [
    "transaction_id",
    "customer_name",
    "city",
    "amount",
    "merchant_category",
    "transaction_status",
]

OPTIONAL_COLUMNS = [
    "risk_category",
    "transaction_date",
    "transaction_type",
]


# =========================================================
# DATA VALIDATION
# =========================================================

def validate_csv(uploaded_file):
    """Read and validate an uploaded CSV without saving it."""

    try:
        df = pd.read_csv(
            uploaded_file,
            dtype={"transaction_id": "string"},
        )
    except Exception as error:
        raise ValueError(
            "CSV file read nahi ho payi. Please valid CSV upload karein."
        ) from error

    df.columns = df.columns.str.strip().str.lower()

    if df.empty:
        raise ValueError("CSV file empty hai.")

    if df.columns.duplicated().any():
        raise ValueError("CSV mein duplicate column names hain.")

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Required columns missing hain: " + ", ".join(missing)
        )

    if df["transaction_id"].isna().any():
        raise ValueError("Transaction IDs missing nahi ho sakti.")

    df["transaction_id"] = df["transaction_id"].str.strip()

    if df["transaction_id"].eq("").any():
        raise ValueError("Kuch transaction IDs empty hain.")

    if df["transaction_id"].duplicated().any():
        raise ValueError(
            "Duplicate transaction IDs mili hain. "
            "Please duplicates resolve karke CSV upload karein."
        )

    text_columns = [
        "customer_name",
        "city",
        "merchant_category",
        "transaction_status",
    ]

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()

        if df[column].isna().any() or df[column].eq("").any():
            raise ValueError(
                f"Column '{column}' mein missing ya empty values hain."
            )

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    if df["amount"].isna().any():
        raise ValueError("Amount column mein invalid ya missing values hain.")

    if not df["amount"].map(
        lambda value: pd.notna(value) and abs(value) != float("inf")
    ).all():
        raise ValueError("Amount column mein invalid numeric values hain.")

    if (df["amount"] < 0).any():
        raise ValueError(
            "Negative amounts supported nahi hain. "
            "Refunds ke liye separate transaction type define karein."
        )

    df["transaction_status"] = (
        df["transaction_status"].str.title()
    )

    valid_statuses = {"Success", "Failed", "Pending"}

    if not df["transaction_status"].isin(valid_statuses).all():
        raise ValueError(
            "Transaction status sirf Success, Failed ya Pending ho sakta hai."
        )

    if "risk_category" not in df.columns:
        df["risk_category"] = "Unknown"

    if "transaction_date" in df.columns:
        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"],
            errors="coerce",
        )

    if "transaction_type" not in df.columns:
        df["transaction_type"] = "Unknown"

    return df


# =========================================================
# ANOMALY DETECTION
# =========================================================

def detect_anomalies(df):
    """Detect unusual amounts within the uploaded dataset."""

    result = df.copy()

    # A single record is insufficient to fit Isolation Forest.
    if len(result) < 2 or result["amount"].nunique() < 2:
        result["anomaly_prediction"] = 1
        result["anomaly_status"] = "Not Evaluated"
        return result

    model = IsolationForest(
        n_estimators=100,
        contamination=min(0.1, 1 / len(result)),
        random_state=42,
    )

    result["anomaly_prediction"] = model.fit_predict(
        result[["amount"]]
    )

    result["anomaly_status"] = result["anomaly_prediction"].map(
        {1: "Normal", -1: "Unusual"}
    )

    return result


# =========================================================
# HEADER
# =========================================================

st.title("🔐 SecureBank Financial Analytics")

st.caption(
    "Financial Transaction Monitoring | Analytics | Anomaly Detection"
)

st.info(
    "Educational analytics prototype. Unusual transaction ka matlab "
    "confirmed fraud nahi hai. Analysis ke liye uploaded data process "
    "kiya jata hai aur automatically MySQL mein save nahi hota."
)


# =========================================================
# DATA SOURCE
# =========================================================

st.sidebar.header("📂 Transaction Data")

data_source = st.sidebar.radio(
    "Choose data source",
    ["Sample Data", "Upload CSV"],
)

df = None

if data_source == "Sample Data":
    if not DATA_FILE.exists():
        st.error(
            "Sample data available nahi hai. "
            "Pehle analysis.py aur anomaly_detection.py run karein."
        )
        st.stop()

    try:
        df = validate_csv(DATA_FILE)
    except ValueError as error:
        st.error(str(error))
        st.stop()

else:
    current_user = st.session_state["user"]

    uploaded_file = st.sidebar.file_uploader(
        "Upload transaction CSV",
        type=["csv"],
        key=f"transaction_upload_user_{current_user['id']}",
        help=(
            "Required columns: transaction_id, customer_name, city, "
            "amount, merchant_category, transaction_status."
        ),
    )

    if uploaded_file is None:
        st.warning("Analysis start karne ke liye CSV upload karein.")
        st.stop()

    # Basic file size limit for this prototype.
    MAX_FILE_SIZE = 5 * 1024 * 1024

    if uploaded_file.size > MAX_FILE_SIZE:
        st.error("CSV file maximum 5 MB ki honi chahiye.")
        st.stop()

    try:
        df = validate_csv(uploaded_file)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    st.success(
        f"CSV successfully validated: {len(df):,} transactions."
    )

if df is None or df.empty:
    st.warning("Display karne ke liye transaction data available nahi hai.")
    st.stop()


# =========================================================
# ANOMALY DETECTION
# =========================================================

df = detect_anomalies(df)


# =========================================================
# FILTERS
# =========================================================

st.sidebar.divider()
st.sidebar.header("🔎 Filters")

cities = ["All"] + sorted(df["city"].dropna().unique().tolist())

selected_city = st.sidebar.selectbox(
    "City",
    cities,
)

statuses = [
    "All"
] + sorted(df["transaction_status"].dropna().unique().tolist())

selected_status = st.sidebar.selectbox(
    "Transaction Status",
    statuses,
)

anomalies = [
    "All"
] + sorted(df["anomaly_status"].dropna().unique().tolist())

selected_anomaly = st.sidebar.selectbox(
    "Anomaly Status",
    anomalies,
)

filtered_df = df.copy()

if selected_city != "All":
    filtered_df = filtered_df[
        filtered_df["city"] == selected_city
    ]

if selected_status != "All":
    filtered_df = filtered_df[
        filtered_df["transaction_status"] == selected_status
    ]

if selected_anomaly != "All":
    filtered_df = filtered_df[
        filtered_df["anomaly_status"] == selected_anomaly
    ]


# =========================================================
# KEY PERFORMANCE INDICATORS
# =========================================================

st.subheader("📊 Key Performance Indicators")

total_transactions = len(filtered_df)
total_amount = filtered_df["amount"].sum()

average_amount = (
    filtered_df["amount"].mean()
    if total_transactions
    else 0
)

unusual_count = (
    filtered_df["anomaly_status"] == "Unusual"
).sum()

failed_count = (
    filtered_df["transaction_status"] == "Failed"
).sum()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Transactions", f"{total_transactions:,}")
col2.metric("Total Amount", f"₹{total_amount:,.2f}")
col3.metric("Average Amount", f"₹{average_amount:,.2f}")
col4.metric("Unusual Transactions", f"{unusual_count:,}")
col5.metric("Failed Transactions", f"{failed_count:,}")

st.divider()


# =========================================================
# CHARTS
# =========================================================

left, right = st.columns(2)

with left:
    st.subheader("💳 Amount by Merchant Category")

    category_data = (
        filtered_df.groupby(
            "merchant_category",
            as_index=False,
        )["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )

    if not category_data.empty:
        fig_category = px.bar(
            category_data,
            x="merchant_category",
            y="amount",
            color="merchant_category",
            title="Total Transaction Amount by Category",
            labels={
                "merchant_category": "Merchant Category",
                "amount": "Total Amount (₹)",
            },
        )

        fig_category.update_layout(
            xaxis_tickangle=-30,
            showlegend=False,
        )

        st.plotly_chart(
            fig_category,
            width="stretch",
        )
    else:
        st.info("No data available for the selected filters.")

with right:
    st.subheader("🚦 Transaction Status")

    status_data = (
        filtered_df["transaction_status"]
        .value_counts()
        .rename_axis("Status")
        .reset_index(name="Count")
    )

    if not status_data.empty:
        fig_status = px.pie(
            status_data,
            names="Status",
            values="Count",
            hole=0.55,
            title="Transaction Status Distribution",
        )

        st.plotly_chart(
            fig_status,
            width="stretch",
        )
    else:
        st.info("No data available for the selected filters.")


# =========================================================
# ANOMALY CHART
# =========================================================

st.subheader("⚠️ Normal vs Unusual Transactions")

anomaly_data = (
    filtered_df["anomaly_status"]
    .value_counts()
    .rename_axis("Anomaly Status")
    .reset_index(name="Count")
)

if not anomaly_data.empty:
    fig_anomaly = px.bar(
        anomaly_data,
        x="Anomaly Status",
        y="Count",
        color="Anomaly Status",
        title="Anomaly Detection Results",
    )

    st.plotly_chart(
        fig_anomaly,
        width="stretch",
    )


# =========================================================
# TRANSACTION TABLES
# =========================================================

st.divider()

st.subheader("🚨 Unusual Transactions")

unusual_df = filtered_df[
    filtered_df["anomaly_status"] == "Unusual"
]

if unusual_df.empty:
    st.success("No unusual transactions found for the selected filters.")
else:
    st.dataframe(
        unusual_df,
        width="stretch",
        hide_index=True,
    )

st.subheader("❌ Failed Transactions")

failed_df = filtered_df[
    filtered_df["transaction_status"] == "Failed"
]

if failed_df.empty:
    st.success("No failed transactions found for the selected filters.")
else:
    st.dataframe(
        failed_df,
        width="stretch",
        hide_index=True,
    )

st.subheader("📋 All Filtered Transactions")

st.dataframe(
    filtered_df,
    width="stretch",
    hide_index=True,
)


# =========================================================
# CSV DOWNLOAD
# =========================================================

st.subheader("📥 Download Analysis")

csv_buffer = io.StringIO()
filtered_df.to_csv(csv_buffer, index=False)

st.download_button(
    label="Download Analyzed Transactions CSV",
    data=csv_buffer.getvalue().encode("utf-8"),
    file_name="securebank_transactions_analysis.csv",
    mime="text/csv",
)

st.caption(
    "SecureBank Financial Analytics | Educational project. "
    "Isolation Forest flags unusual patterns for review; "
    "it does not establish fraud."
)