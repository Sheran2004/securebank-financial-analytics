# 🏦 SecureBank Financial Analytics

### Financial Transaction Monitoring & Anomaly Detection

<p align="center">
  <a href="https://securebank-financial-analytics-iipg98umtvqjmzxezkxucn.streamlit.app/">
    <img src="https://img.shields.io/badge/🚀_Live_Demo-Open_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo">
  </a>
</p>

**🔴 Live App:** https://securebank-financial-analytics-iipg98umtvqjmzxezkxucn.streamlit.app/

A data analytics project that explores banking transactions using SQL and Python, identifies unusual transaction patterns using Machine Learning, and presents key financial insights through an interactive Streamlit dashboard.


## 📌 Project Overview

Financial transaction monitoring helps identify unusual activities, analyze transaction behavior, and understand potential risks.

This project combines SQL-based financial analysis, Python data processing, and machine learning-based anomaly detection to explore a sample banking transaction dataset.

**Note:** This project uses synthetic sample data for educational purposes. Unusual transactions are not confirmed fraudulent transactions.

## 🎯 Project Objectives

* Analyze customer and transaction data using SQL.
* Measure transaction volumes and amounts.
* Examine successful and failed transactions.
* Analyze merchant categories and customer risk categories.
* Identify unusual transaction amounts using Isolation Forest.
* Build an interactive dashboard for financial insights.

## ✨ Key Features

* **SQL Analysis:** Data retrieval, joins, aggregations, and category-wise analysis.
* **Transaction Monitoring:** Summaries of transaction amounts and statuses.
* **Anomaly Detection:** Isolation Forest identifies potentially unusual transaction amounts.
* **Interactive Dashboard:** Visualize financial metrics, transaction categories, and anomaly results.
* **Dynamic Filters:** Filter transactions by city, transaction status, and anomaly status.
* **CSV Export:** Download filtered transaction data for further analysis.

## 🛠️ Technologies Used

* Python
* MySQL
* SQL
* Pandas
* Scikit-learn
* Streamlit
* Plotly
* python-dotenv

## 📂 Project Structure

```text
SecureBank-Financial-Analytics/
│
├── database/
│   └── schema.sql
│
├── queries/
│   ├── 01_basic_queries.sql
│   ├── 02_joins.sql
│   ├── 03_financial_analysis.sql
│   └── 04_anomaly_detection.sql
│
├── data/
│   ├── transactions_analysis.csv
│   └── anomaly_results.csv
│
├── connect_db.py
├── analysis.py
├── anomaly_detection.py
├── dashboard.py
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md
```

## 📊 Dashboard Metrics

The current sample dataset contains:

| Metric                     |     Result |
| -------------------------- | ---------: |
| Total Transactions         |         15 |
| Total Transaction Amount   |  ₹5,29,000 |
| Average Transaction Amount | ₹35,266.67 |
| Successful Transactions    |         14 |
| Failed Transactions        |          1 |
| Unusual Transactions       |          2 |

These figures describe the current sample dataset and may change when the data changes.

## 🤖 Anomaly Detection

The project uses the **Isolation Forest** algorithm from Scikit-learn to flag unusual transaction amounts.

The current model uses transaction amount as its numerical feature.

Example findings from the sample dataset:

* Transaction 105: ₹95,000, flagged as unusual.
* Transaction 113: ₹1,20,000, flagged as unusual and marked failed.

These results are model-generated anomaly flags, not proof of fraud. The dataset is small and is not sufficient to validate a production fraud detection system.

## ⚙️ Setup and Installation

### 1. Prerequisites

Install the following:

* Python 3.11
* MySQL Server
* MySQL Workbench (optional)
* Visual Studio Code (optional)

### 2. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SecureBank-Financial-Analytics
```

Replace the placeholder with your repository URL after creating the GitHub repository.

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=securebank_analytics
```

Replace `YOUR_MYSQL_PASSWORD` with your own local MySQL password.

**Security:** Never commit `.env` or database credentials to GitHub.

### 6. Set Up the Database

Create the `securebank_analytics` database in MySQL and execute the SQL schema and sample-data setup scripts.

Verify that the `customers` and `transactions` tables exist and contain sample records.

### 7. Test the Database Connection

```bash
python connect_db.py
```

### 8. Run Financial Analysis

```bash
python analysis.py
```

This script retrieves transaction data and generates `data/transactions_analysis.csv`.

### 9. Run Anomaly Detection

```bash
python anomaly_detection.py
```

This script generates `data/anomaly_results.csv`.

### 10. Launch the Dashboard

```bash
python -m streamlit run dashboard.py
```

Open the local address displayed in the terminal to view the dashboard.

## 🔐 Security Notes

* Database credentials are stored in a local `.env` file.
* The `.env` file should not be committed to version control.
* Use synthetic or properly anonymized data for demonstrations.
* Do not use this educational model to make real-world financial decisions.

## 🚧 Limitations and Future Improvements

* Expand the sample dataset for more meaningful analysis.
* Evaluate anomaly detection using labeled transaction data.
* Explore additional features, such as transaction frequency and time-based patterns.
* Add automated data validation and model evaluation.
* Improve dashboard table usability and reporting.
* Consider a secure, production-grade deployment architecture.

## 👨‍💻 Project Purpose

This project demonstrates practical skills in SQL, Python, data analysis, machine learning, and dashboard development through a financial transaction monitoring use case.

---

**Built for learning and portfolio demonstration.**
