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

# Hide Streamlit's hosted-app chrome (GitHub/source controls and footer badge).
st.markdown(
    """
    <style>
        [data-testid="stHeader"] {
            display: none !important;
        }
        [data-testid="stToolbar"] {
            display: none !important;
        }
        [data-testid="stDecoration"] {
            display: none !important;
        }
        [data-testid="stStatusWidget"] {
            display: none !important;
        }
        [data-testid="stFooter"] {
            display: none !important;
        }
        #MainMenu {
            visibility: hidden !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# AUTHENTICATION
# =========================================================

if not render_auth():
    st.stop()

# The public demo is read-only and uses illustrative mock data only.
if st.session_state.get("demo_mode", False) and st.session_state.get("user") is None:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:0.5rem;">
          <svg width="54" height="54" viewBox="0 0 64 64" role="img"
               aria-label="SecureBank logo" xmlns="http://www.w3.org/2000/svg">
            <rect x="5" y="5" width="54" height="54" rx="14" fill="#123B5D"/>
            <path d="M12 24 L32 13 L52 24 Z" fill="#FFFFFF"/>
            <path d="M15 26 H49 V30 H15 Z" fill="#5CC8B2"/>
            <rect x="17" y="32" width="5" height="13" rx="1" fill="#FFFFFF"/>
            <rect x="29.5" y="32" width="5" height="13" rx="1" fill="#FFFFFF"/>
            <rect x="42" y="32" width="5" height="13" rx="1" fill="#FFFFFF"/>
            <path d="M12 47 H52 V51 H12 Z" fill="#5CC8B2"/>
          </svg>
          <span style="font-size:2.5rem;font-weight:700;line-height:1.2;">
            SecureBank Live Demo
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Read-only preview · All figures and transactions below are illustrative mock data.")
    _, top_right = st.columns([5, 1])
    with top_right:
        if st.button("← Back to Login", key="demo_back_to_login", width="stretch"):
            st.session_state["demo_mode"] = False
            st.rerun()

    demo_transactions = pd.DataFrame(
        [
            {"Transaction ID": "DEMO-1001", "Date": "2026-10-02", "Description": "Salary credit", "Category": "Income", "Amount (₹)": 85000, "Status": "Success"},
            {"Transaction ID": "DEMO-1002", "Date": "2026-10-04", "Description": "House rent", "Category": "Housing", "Amount (₹)": -18000, "Status": "Success"},
            {"Transaction ID": "DEMO-1003", "Date": "2026-10-06", "Description": "Groceries", "Category": "Food", "Amount (₹)": -6200, "Status": "Success"},
            {"Transaction ID": "DEMO-1004", "Date": "2026-10-09", "Description": "Electricity bill", "Category": "Utilities", "Amount (₹)": -2400, "Status": "Success"},
            {"Transaction ID": "DEMO-1005", "Date": "2026-10-12", "Description": "Online purchase", "Category": "Shopping", "Amount (₹)": -5100, "Status": "Success"},
            {"Transaction ID": "DEMO-1006", "Date": "2026-10-15", "Description": "Freelance payment", "Category": "Income", "Amount (₹)": 12000, "Status": "Success"},
            {"Transaction ID": "DEMO-1007", "Date": "2026-10-18", "Description": "Restaurant", "Category": "Food", "Amount (₹)": -1850, "Status": "Success"},
            {"Transaction ID": "DEMO-1008", "Date": "2026-10-21", "Description": "ATM withdrawal", "Category": "Cash", "Amount (₹)": -3000, "Status": "Success"},
            {"Transaction ID": "DEMO-1009", "Date": "2026-10-24", "Description": "Unusual transfer", "Category": "Transfer", "Amount (₹)": -25000, "Status": "Review"},
        ]
    )
    monthly_summary = pd.DataFrame(
        [
            {"Month": "May", "Income": 76000, "Expenses": 39000, "Available Cash": 92000, "Net Worth": 420000},
            {"Month": "Jun", "Income": 79000, "Expenses": 41500, "Available Cash": 99500, "Net Worth": 438000},
            {"Month": "Jul", "Income": 81000, "Expenses": 43000, "Available Cash": 108000, "Net Worth": 455000},
            {"Month": "Aug", "Income": 80000, "Expenses": 40500, "Available Cash": 119000, "Net Worth": 477000},
            {"Month": "Sep", "Income": 84000, "Expenses": 44700, "Available Cash": 131000, "Net Worth": 501000},
            {"Month": "Oct", "Income": 97000, "Expenses": 62550, "Available Cash": 150450, "Net Worth": 528000},
        ]
    )

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Available Cash", "₹1,50,450")
    metric2.metric("Monthly Income", "₹97,000")
    metric3.metric("Monthly Expenses", "₹62,550")
    metric4.metric("Estimated Net Worth", "₹5,28,000")

    st.divider()
    chart_left, chart_right = st.columns(2)
    with chart_left:
        st.subheader("Monthly Income vs Expenses")
        income_expense = monthly_summary.melt(
            id_vars="Month", value_vars=["Income", "Expenses"],
            var_name="Type", value_name="Amount (₹)"
        )
        fig_monthly = px.bar(
            income_expense, x="Month", y="Amount (₹)", color="Type",
            barmode="group", title="Illustrative monthly cash flow"
        )
        st.plotly_chart(fig_monthly, width="stretch")
    with chart_right:
        st.subheader("Available Cash & Net Worth")
        networth_data = monthly_summary.melt(
            id_vars="Month", value_vars=["Available Cash", "Net Worth"],
            var_name="Metric", value_name="Amount (₹)"
        )
        fig_networth = px.line(
            networth_data, x="Month", y="Amount (₹)", color="Metric",
            markers=True, title="Illustrative financial position"
        )
        st.plotly_chart(fig_networth, width="stretch")

    st.subheader("Transaction Drill-Down")
    selected_transaction = st.selectbox(
        "Choose a mock transaction to inspect",
        demo_transactions["Transaction ID"].tolist(),
        key="demo_transaction_detail",
    )
    selected_row = demo_transactions.loc[
        demo_transactions["Transaction ID"] == selected_transaction
    ].iloc[0]
    detail_cols = st.columns(4)
    detail_cols[0].metric("Transaction ID", selected_row["Transaction ID"])
    detail_cols[1].metric("Amount", f"₹{selected_row['Amount (₹)']:,.0f}")
    detail_cols[2].metric("Category", selected_row["Category"])
    detail_cols[3].metric("Status", selected_row["Status"])
    st.write(f"**Description:** {selected_row['Description']}  ·  **Date:** {selected_row['Date']}")
    st.dataframe(demo_transactions, width="stretch", hide_index=True)
    st.caption("Demo only: illustrative figures, not real customer or bank records. No data is saved.")
    st.stop()

if st.session_state.get("guest_mode", False) and st.session_state.get("user") is None:
    guest_left, guest_right = st.columns([5, 1])
    with guest_left:
        st.info("Guest mode · Use sample data or upload a CSV. Uploaded files are processed on the app server and are not automatically saved.")
    with guest_right:
        if st.button("← Exit Guest", key="exit_guest_mode", width="stretch"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state["user"] = None
            st.rerun()
else:
    render_logout()

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

st.markdown(
    """
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:0.5rem;">
      <svg width="54" height="54" viewBox="0 0 64 64" role="img"
           aria-label="SecureBank logo" xmlns="http://www.w3.org/2000/svg">
        <rect x="5" y="5" width="54" height="54" rx="14" fill="#123B5D"/>
        <path d="M12 24 L32 13 L52 24 Z" fill="#FFFFFF"/>
        <path d="M15 26 H49 V30 H15 Z" fill="#5CC8B2"/>
        <rect x="17" y="32" width="5" height="13" rx="1" fill="#FFFFFF"/>
        <rect x="29.5" y="32" width="5" height="13" rx="1" fill="#FFFFFF"/>
        <rect x="42" y="32" width="5" height="13" rx="1" fill="#FFFFFF"/>
        <path d="M12 47 H52 V51 H12 Z" fill="#5CC8B2"/>
      </svg>
      <span style="font-size:2.5rem;font-weight:700;line-height:1.2;">
        SecureBank Financial Analytics
      </span>
    </div>
    """,
    unsafe_allow_html=True,
)

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
    current_user = st.session_state.get("user")
    uploader_key = (
        f"transaction_upload_user_{current_user['id']}"
        if current_user
        else "transaction_upload_guest"
    )

    uploaded_file = st.file_uploader(
        "Upload transaction CSV",
        type=["csv"],
        key=uploader_key,
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

st.subheader("🔎 Transaction Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)

cities = ["All"] + sorted(df["city"].dropna().unique().tolist())

with filter_col1:
    selected_city = st.selectbox(
        "City",
        cities,
        key="main_city_filter",
    )

statuses = [
    "All"
] + sorted(df["transaction_status"].dropna().unique().tolist())

with filter_col2:
    selected_status = st.selectbox(
        "Transaction Status",
        statuses,
        key="main_status_filter",
    )

anomalies = [
    "All"
] + sorted(df["anomaly_status"].dropna().unique().tolist())

with filter_col3:
    selected_anomaly = st.selectbox(
        "Anomaly Status",
        anomalies,
        key="main_anomaly_filter",
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

st.divider()

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