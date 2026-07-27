"""
==================================================================
 Banking Transaction Analysis Dashboard  (Enhanced Edition)
 Author: Anisha M.
==================================================================
 Core analysis (same as before):
   1. Synthetic transaction data (Indian names & cities)
   2. Unusual transaction detection (4 explainable rules)
   3. Account summaries
   4. Monthly transaction reports
   5. Customer activity analysis

 NEW in this edition (what makes it stand out):
   6. Risk rating badges (Low / Medium / High) per account
   7. Customer 360 - search & drill into one customer's full profile
   8. One-click CSV downloads for every report table
   9. Day-of-week x hour heatmap of unusual-transaction activity
  10. Month-over-month KPI trend arrows on the Overview page
  11. City / branch-wise comparison view
  12. Colour-coded balance alerts (red = negative, orange = low)
  13. Top Movers leaderboard (biggest balance changes this month)

 HOW TO RUN THIS ON WINDOWS:
    1. Open Command Prompt in this folder.
    2. Run:  pip install streamlit pandas numpy matplotlib
    3. Run:  streamlit run banking_dashboard_v2.py
    4. It opens automatically in your browser. If not, copy the
       "Local URL" from the Command Prompt into Chrome.
==================================================================
"""

import random
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# ------------------------------------------------------------------
# PART 1: BASIC SETTINGS
# ------------------------------------------------------------------
random.seed(42)
np.random.seed(42)

NUMBER_OF_CUSTOMERS = 60
MONTHS_OF_HISTORY = 12
TRANSACTIONS_PER_CUSTOMER_PER_MONTH = (3, 14)

FIRST_NAMES = [
    "Aarav", "Vihaan", "Aditya", "Sai", "Arjun", "Krishna", "Ishaan", "Rohan",
    "Kabir", "Aryan", "Ananya", "Diya", "Saanvi", "Ira", "Myra", "Anika",
    "Pari", "Kavya", "Meera", "Riya", "Karthik", "Vikram", "Suresh", "Ramesh",
    "Lakshmi", "Priya", "Sneha", "Divya", "Naveen", "Deepak", "Ganesh",
    "Harini", "Kalyani", "Manoj", "Nithya", "Pradeep", "Radha", "Sathish",
    "Tara", "Uma", "Vasanth", "Yamini", "Zoya", "Farhan", "Imran",
]
LAST_NAMES = [
    "Sharma", "Iyer", "Nair", "Reddy", "Rao", "Gupta", "Menon", "Pillai",
    "Krishnan", "Subramaniam", "Chowdhury", "Verma", "Patel", "Naidu",
    "Raghavan", "Balan", "Mahesh", "Chandran", "Venkatesh", "Prabhu",
]
CITIES = [
    "Chennai", "Coimbatore", "Madurai", "Bengaluru", "Hyderabad",
    "Mumbai", "Pune", "Kochi", "Trichy", "Salem", "Vizag", "Vijayawada",
]
ACCOUNT_TYPES = ["Savings", "Current", "Salary"]

TRANSACTION_CATEGORIES = {
    "Credit": ["Salary Credit", "Interest Credit", "Fund Transfer In", "Refund"],
    "Debit": [
        "ATM Withdrawal", "POS Purchase", "Online Shopping", "Utility Bill",
        "Fund Transfer Out", "EMI Payment", "Grocery", "Dining", "Fuel",
    ],
}

ALL_CATEGORIES = sum(TRANSACTION_CATEGORIES.values(), [])
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ------------------------------------------------------------------
# PART 2: BUILD THE CUSTOMER LIST (plain list of dictionaries)
# ------------------------------------------------------------------
def generate_customers(n):
    customers = []
    used_names = set()
    for i in range(1, n + 1):
        while True:
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            if name not in used_names:
                used_names.add(name)
                break
        customers.append({
            "customer_id": f"CUST{i:03d}",
            "name": name,
            "city": random.choice(CITIES),
            "account_number": f"ACC{100000 + i}",
            "account_type": random.choice(ACCOUNT_TYPES),
            "opening_balance": round(random.uniform(8000, 150000), 2),
        })
    return customers


# ------------------------------------------------------------------
# PART 3: BUILD THE TRANSACTION LIST (plain list of dictionaries)
# ------------------------------------------------------------------
def generate_transactions(customers, months=MONTHS_OF_HISTORY):
    transactions = []
    txn_counter = 1
    end_date = datetime(2026, 7, 27)
    start_date = end_date - timedelta(days=30 * months)

    for cust in customers:
        running_balance = cust["opening_balance"]
        total_days = (end_date - start_date).days

        for month_index in range(months):
            n_txns = random.randint(*TRANSACTIONS_PER_CUSTOMER_PER_MONTH)
            for _ in range(n_txns):
                day_offset = random.randint(
                    month_index * 30, min((month_index + 1) * 30, total_days) - 1
                )
                txn_date = start_date + timedelta(days=day_offset)
                hour = int(np.clip(np.random.normal(14, 5), 0, 23))
                minute = random.randint(0, 59)
                txn_datetime = txn_date.replace(hour=hour, minute=minute)

                txn_type = random.choices(["Credit", "Debit"], weights=[0.35, 0.65])[0]
                category = random.choice(TRANSACTION_CATEGORIES[txn_type])

                if category == "Salary Credit":
                    amount = round(random.uniform(25000, 90000), 2)
                elif category == "ATM Withdrawal":
                    amount = round(random.choice([500, 1000, 2000, 5000, 10000]), 2)
                elif txn_type == "Credit":
                    amount = round(random.uniform(500, 20000), 2)
                else:
                    amount = round(random.uniform(150, 15000), 2)

                is_seeded_unusual = random.random() < 0.015
                if is_seeded_unusual:
                    amount = round(amount * random.uniform(6, 15), 2)

                if txn_type == "Credit":
                    running_balance += amount
                else:
                    running_balance -= amount

                transactions.append({
                    "transaction_id": f"TXN{txn_counter:06d}",
                    "customer_id": cust["customer_id"],
                    "name": cust["name"],
                    "account_number": cust["account_number"],
                    "account_type": cust["account_type"],
                    "city": cust["city"],
                    "date": txn_datetime,
                    "month": txn_datetime.strftime("%Y-%m"),
                    "day_name": txn_datetime.strftime("%A"),
                    "hour": txn_datetime.hour,
                    "type": txn_type,
                    "category": category,
                    "amount": amount,
                    "balance_after": round(running_balance, 2),
                })
                txn_counter += 1

    transactions.sort(key=lambda t: t["date"])
    return transactions


# ------------------------------------------------------------------
# PART 4: UNUSUAL TRANSACTION DETECTION
# ------------------------------------------------------------------
def detect_unusual_transactions(df):
    df = df.copy()
    df["is_unusual"] = False
    df["unusual_reasons"] = [[] for _ in range(len(df))]

    stats = df.groupby("customer_id")["amount"].agg(["mean", "std"]).reset_index()
    stats.columns = ["customer_id", "cust_mean", "cust_std"]
    df = df.merge(stats, on="customer_id", how="left")
    df["cust_std"] = df["cust_std"].fillna(0)
    fallback_std = df["cust_mean"] * 0.5 + 1
    safe_std = np.where(df["cust_std"] == 0, fallback_std, df["cust_std"])
    df["z_score"] = (df["amount"] - df["cust_mean"]) / safe_std

    for idx in df.index[df["z_score"] > 4]:
        df.at[idx, "is_unusual"] = True
        df.at[idx, "unusual_reasons"].append("Amount far above customer's usual pattern")

    late_night_mask = (df["date"].dt.hour >= 23) | (df["date"].dt.hour <= 4)
    for idx in df.index[late_night_mask]:
        df.at[idx, "is_unusual"] = True
        df.at[idx, "unusual_reasons"].append("Unusual transaction time (late night)")

    df["date_only"] = df["date"].dt.date
    daily_counts = df.groupby(["customer_id", "date_only"]).size()
    busy_days = daily_counts[daily_counts >= 5].index
    busy_set = set(busy_days)
    for idx, row in df.iterrows():
        if (row["customer_id"], row["date_only"]) in busy_set:
            df.at[idx, "is_unusual"] = True
            df.at[idx, "unusual_reasons"].append("High transaction frequency in one day")

    large_debit_mask = (df["type"] == "Debit") & (df["amount"] > 75000)
    for idx in df.index[large_debit_mask]:
        df.at[idx, "is_unusual"] = True
        df.at[idx, "unusual_reasons"].append("Large single debit (over Rs. 75,000)")

    df["unusual_reasons_text"] = df["unusual_reasons"].apply(
        lambda r: "; ".join(sorted(set(r))) if r else ""
    )
    return df


# ------------------------------------------------------------------
# PART 5: ACCOUNT SUMMARY + RISK RATING
# ------------------------------------------------------------------
# Risk rating is deliberately simple and explainable:
#   unusual_rate = (flagged transactions) / (total transactions)
#   Bottom 60% of customers by unusual_rate  -> Low risk
#   Next 25%                                  -> Medium risk
#   Top 15%                                   -> High risk
# This is a monitoring/engagement indicator, NOT a credit score.
def build_account_summary(df, customers):
    rows = []
    for cust in customers:
        cust_txns = df[df["customer_id"] == cust["customer_id"]]
        total_credit = cust_txns.loc[cust_txns["type"] == "Credit", "amount"].sum()
        total_debit = cust_txns.loc[cust_txns["type"] == "Debit", "amount"].sum()
        closing_balance = cust["opening_balance"] + total_credit - total_debit
        unusual_count = int(cust_txns["is_unusual"].sum()) if len(cust_txns) else 0
        txn_count = len(cust_txns)
        unusual_rate = (unusual_count / txn_count) if txn_count else 0

        rows.append({
            "customer_id": cust["customer_id"],
            "name": cust["name"],
            "account_number": cust["account_number"],
            "account_type": cust["account_type"],
            "city": cust["city"],
            "opening_balance": round(cust["opening_balance"], 2),
            "total_credits": round(total_credit, 2),
            "total_debits": round(total_debit, 2),
            "closing_balance": round(closing_balance, 2),
            "transaction_count": txn_count,
            "unusual_count": unusual_count,
            "unusual_rate": round(unusual_rate, 4),
        })
    summary = pd.DataFrame(rows)

    # Risk rating via quantile cut-offs (adapts automatically to the data)
    try:
        summary["risk_rating"] = pd.qcut(
            summary["unusual_rate"].rank(method="first"),
            q=[0, 0.6, 0.85, 1.0],
            labels=["Low", "Medium", "High"],
        )
    except ValueError:
        summary["risk_rating"] = "Low"

    badge_map = {"Low": "Low", "Medium": "Medium", "High": "High"}
    emoji_map = {"Low": "\U0001F7E2 Low", "Medium": "\U0001F7E1 Medium", "High": "\U0001F534 High"}
    summary["risk_rating"] = summary["risk_rating"].astype(str).map(badge_map).fillna("Low")
    summary["risk_badge"] = summary["risk_rating"].map(emoji_map)
    return summary


# ------------------------------------------------------------------
# PART 6: MONTHLY TRANSACTION REPORT
# ------------------------------------------------------------------
def build_monthly_report(df):
    monthly = df.groupby("month").apply(
        lambda g: pd.Series({
            "total_credits": g.loc[g["type"] == "Credit", "amount"].sum(),
            "total_debits": g.loc[g["type"] == "Debit", "amount"].sum(),
            "transaction_count": len(g),
            "unusual_count": g["is_unusual"].sum(),
        })
    ).reset_index()
    monthly = monthly.sort_values("month")
    monthly["net_flow"] = monthly["total_credits"] - monthly["total_debits"]
    monthly["credit_change_pct"] = monthly["total_credits"].pct_change() * 100
    monthly["debit_change_pct"] = monthly["total_debits"].pct_change() * 100
    return monthly


# ------------------------------------------------------------------
# PART 7: CUSTOMER ACTIVITY ANALYSIS
# ------------------------------------------------------------------
def build_customer_activity(df, customers):
    rows = []
    max_txns = df.groupby("customer_id").size().max()
    max_volume = df.groupby("customer_id")["amount"].sum().max()

    for cust in customers:
        cust_txns = df[df["customer_id"] == cust["customer_id"]]
        if len(cust_txns) == 0:
            continue
        txn_count = len(cust_txns)
        volume = cust_txns["amount"].sum()
        variety = cust_txns["category"].nunique()
        top_category = cust_txns["category"].mode().iloc[0]
        last_txn_date = cust_txns["date"].max()

        freq_score = (txn_count / max_txns) * 40
        volume_score = (volume / max_volume) * 40
        variety_score = (variety / len(ALL_CATEGORIES)) * 20
        activity_score = round(freq_score + volume_score + variety_score, 1)

        rows.append({
            "customer_id": cust["customer_id"],
            "name": cust["name"],
            "city": cust["city"],
            "transaction_count": txn_count,
            "total_volume": round(volume, 2),
            "top_category": top_category,
            "last_transaction": last_txn_date.strftime("%d-%b-%Y"),
            "activity_score": activity_score,
        })

    result = pd.DataFrame(rows).sort_values("activity_score", ascending=False)
    return result


# ------------------------------------------------------------------
# PART 8: TOP MOVERS (biggest balance change, last month vs prior month)
# ------------------------------------------------------------------
def build_top_movers(df):
    months = sorted(df["month"].unique())
    if len(months) < 2:
        return pd.DataFrame(), None, None
    latest_month, prev_month = months[-1], months[-2]

    def month_end_balance(month):
        sub = df[df["month"] == month].sort_values("date")
        return sub.groupby("customer_id").last()["balance_after"]

    latest_bal = month_end_balance(latest_month)
    prev_bal = month_end_balance(prev_month)

    merged = pd.DataFrame({"latest_balance": latest_bal, "prev_balance": prev_bal}).dropna()
    merged["change"] = merged["latest_balance"] - merged["prev_balance"]
    merged = merged.reset_index()

    name_lookup = df.drop_duplicates("customer_id").set_index("customer_id")[
        ["name", "city", "account_number"]
    ]
    merged = merged.merge(name_lookup, on="customer_id", how="left")
    merged = merged.sort_values("change", ascending=False)
    return merged, latest_month, prev_month


# ------------------------------------------------------------------
# PART 9: CITY / BRANCH COMPARISON
# ------------------------------------------------------------------
def build_city_comparison(df, account_summary):
    city_txn = df.groupby("city").agg(
        transaction_count=("transaction_id", "count"),
        total_volume=("amount", "sum"),
        unusual_count=("is_unusual", "sum"),
    ).reset_index()
    city_txn["unusual_rate_pct"] = (
        city_txn["unusual_count"] / city_txn["transaction_count"] * 100
    ).round(2)

    city_balance = account_summary.groupby("city").agg(
        avg_closing_balance=("closing_balance", "mean"),
        customers=("customer_id", "count"),
    ).reset_index()
    city_balance["avg_closing_balance"] = city_balance["avg_closing_balance"].round(2)

    return city_txn.merge(city_balance, on="city", how="left").sort_values(
        "total_volume", ascending=False
    )


# ------------------------------------------------------------------
# PART 10: LOAD / CACHE EVERYTHING
# ------------------------------------------------------------------
@st.cache_data
def load_all_data():
    customers = generate_customers(NUMBER_OF_CUSTOMERS)
    transactions = generate_transactions(customers)
    txn_df = pd.DataFrame(transactions)
    txn_df = detect_unusual_transactions(txn_df)
    account_summary = build_account_summary(txn_df, customers)
    monthly_report = build_monthly_report(txn_df)
    customer_activity = build_customer_activity(txn_df, customers)
    top_movers, latest_month, prev_month = build_top_movers(txn_df)
    city_comparison = build_city_comparison(txn_df, account_summary)
    return (customers, txn_df, account_summary, monthly_report, customer_activity,
            top_movers, latest_month, prev_month, city_comparison)


def to_csv_download(df, label, filename, key):
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        key=key,
    )


def style_balances(df, balance_col="closing_balance"):
    def colour(val):
        if val < 0:
            return "background-color: #FDE2E2; color: #9B1C1C;"
        elif val < 10000:
            return "background-color: #FEF3C7; color: #92400E;"
        return ""
    styler = df.style
    if hasattr(styler, "map"):
        styler = styler.map(colour, subset=[balance_col])
    else:
        styler = styler.applymap(colour, subset=[balance_col])
    return styler.format({balance_col: "{:,.2f}"})


# ==================================================================
# PART 11: STREAMLIT DASHBOARD
# ==================================================================
st.set_page_config(
    page_title="Banking Transaction Analysis Dashboard",
    page_icon="\U0001F3E6",
    layout="wide",
)

CUSTOM_CSS = """
<style>
    .main-header {
        padding: 1.2rem 1.5rem;
        border-radius: 10px;
        background: linear-gradient(90deg, #0B1F3A 0%, #14315C 100%);
        color: #F4D35E;
        margin-bottom: 1.2rem;
    }
    .main-header h1 { color: #F4D35E; margin-bottom: 0.2rem; }
    .main-header p { color: #E8E8E8; margin: 0; }
    div[data-testid="stMetric"] {
        background-color: #0B1F3A0D;
        border: 1px solid #F4D35E55;
        border-radius: 8px;
        padding: 0.6rem 0.8rem;
    }
    .profile-card {
        padding: 1rem 1.2rem;
        border-radius: 10px;
        background-color: #F7F7F9;
        border: 1px solid #14315C33;
        margin-bottom: 1rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="main-header">
        <h1>Banking Transaction Analysis Dashboard</h1>
        <p>Unusual transaction detection - Account summaries - Monthly reports - Customer activity
        - Risk ratings - Customer 360 &nbsp;|&nbsp; Prepared by Anisha M.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

(customers, txn_df, account_summary, monthly_report, customer_activity,
 top_movers, latest_month, prev_month, city_comparison) = load_all_data()

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")
city_filter = st.sidebar.multiselect("City", sorted(txn_df["city"].unique()), default=[])
acct_type_filter = st.sidebar.multiselect("Account Type", sorted(txn_df["account_type"].unique()), default=[])
month_filter = st.sidebar.multiselect("Month", sorted(txn_df["month"].unique()), default=[])

filtered_df = txn_df.copy()
if city_filter:
    filtered_df = filtered_df[filtered_df["city"].isin(city_filter)]
if acct_type_filter:
    filtered_df = filtered_df[filtered_df["account_type"].isin(acct_type_filter)]
if month_filter:
    filtered_df = filtered_df[filtered_df["month"].isin(month_filter)]

st.sidebar.markdown("---")
st.sidebar.caption(
    f"Dataset: {len(customers)} customers, {len(txn_df)} transactions "
    f"across {txn_df['month'].nunique()} months (synthetic demo data)."
)

# ---------------- Top-level KPIs with month-over-month deltas ----------------
if latest_month is not None:
    last_row = monthly_report[monthly_report["month"] == latest_month].iloc[0]
    prev_row = monthly_report[monthly_report["month"] == prev_month].iloc[0]
    credit_delta = last_row["total_credits"] - prev_row["total_credits"]
    debit_delta = last_row["total_debits"] - prev_row["total_debits"]
    txn_delta = int(last_row["transaction_count"] - prev_row["transaction_count"])
    unusual_delta = int(last_row["unusual_count"] - prev_row["unusual_count"])
else:
    credit_delta = debit_delta = txn_delta = unusual_delta = None

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Customers", len(customers))
k2.metric("Total Transactions", f"{len(filtered_df):,}",
          delta=(f"{txn_delta:+d} vs last month" if txn_delta is not None else None))
k3.metric("Total Credits (Rs.)", f"{filtered_df.loc[filtered_df['type']=='Credit','amount'].sum():,.0f}",
          delta=(f"{credit_delta:+,.0f} vs last month" if credit_delta is not None else None))
k4.metric("Total Debits (Rs.)", f"{filtered_df.loc[filtered_df['type']=='Debit','amount'].sum():,.0f}",
          delta=(f"{debit_delta:+,.0f} vs last month" if debit_delta is not None else None),
          delta_color="inverse")
k5.metric("Flagged Unusual", int(filtered_df["is_unusual"].sum()),
          delta=(f"{unusual_delta:+d} vs last month" if unusual_delta is not None else None),
          delta_color="inverse")

st.caption(
    f"Month-over-month deltas compare {latest_month} to {prev_month} "
    "across the full dataset (independent of the sidebar filters above)."
)

st.markdown("")

tab_names = [
    "Overview", "Unusual Transactions", "Account Summaries", "Monthly Reports",
    "Customer Activity", "Customer 360", "City Comparison", "Top Movers",
]
tabs = st.tabs(tab_names)

# ================= TAB 1: OVERVIEW =================
with tabs[0]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Credits vs Debits by Month")
        m = monthly_report.copy()
        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.bar(m["month"], m["total_credits"], label="Credits", color="#1B4965")
        ax.bar(m["month"], -m["total_debits"], label="Debits", color="#F4A259")
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_ylabel("Amount (Rs.)")
        ax.legend()
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)

    with col2:
        st.subheader("Transaction Category Mix")
        cat_counts = filtered_df["category"].value_counts()
        fig2, ax2 = plt.subplots(figsize=(6, 3.5))
        ax2.pie(cat_counts.values, labels=cat_counts.index, autopct="%1.0f%%",
                colors=plt.cm.YlGnBu_r(np.linspace(0.2, 0.9, len(cat_counts))))
        st.pyplot(fig2)

    st.subheader("Transactions by City")
    city_counts = filtered_df["city"].value_counts()
    st.bar_chart(city_counts)

# ================= TAB 2: UNUSUAL TRANSACTIONS =================
with tabs[1]:
    st.subheader("Flagged Unusual Transactions")
    st.caption(
        "A transaction is flagged if it matches any rule: amount far above the "
        "customer's own average, unusual (late-night) timing, too many transactions "
        "in a single day, or a large single debit over Rs. 75,000."
    )
    unusual_df = filtered_df[filtered_df["is_unusual"]].sort_values("amount", ascending=False)
    st.metric("Total Flagged", len(unusual_df))

    display_cols = ["transaction_id", "date", "name", "account_number", "type",
                     "category", "amount", "unusual_reasons_text"]
    st.dataframe(
        unusual_df[display_cols].rename(columns={"unusual_reasons_text": "reason(s)"}),
        width="stretch", hide_index=True,
    )
    to_csv_download(unusual_df[display_cols], "Download flagged transactions (CSV)",
                     "unusual_transactions.csv", "dl_unusual")

    st.subheader("Top 10 Largest Flagged Amounts")
    top10 = unusual_df.head(10)
    fig3, ax3 = plt.subplots(figsize=(8, 3.5))
    ax3.barh(top10["name"] + " - " + top10["transaction_id"], top10["amount"], color="#C1121F")
    ax3.invert_yaxis()
    ax3.set_xlabel("Amount (Rs.)")
    st.pyplot(fig3)

    st.subheader("When Do Unusual Transactions Happen? (Day x Hour)")
    st.caption(
        "Darker cells mean more flagged transactions occurred in that day/hour slot - "
        "useful for spotting patterns like weekend spikes or odd-hour clusters."
    )
    heat_source = filtered_df[filtered_df["is_unusual"]]
    if len(heat_source) > 0:
        pivot = heat_source.pivot_table(
            index="day_name", columns="hour", values="transaction_id", aggfunc="count", fill_value=0
        ).reindex(DAY_ORDER)
        fig4, ax4 = plt.subplots(figsize=(10, 3.5))
        im = ax4.imshow(pivot.values, cmap="Reds", aspect="auto")
        ax4.set_xticks(range(len(pivot.columns)))
        ax4.set_xticklabels(pivot.columns)
        ax4.set_yticks(range(len(pivot.index)))
        ax4.set_yticklabels(pivot.index)
        ax4.set_xlabel("Hour of Day")
        fig4.colorbar(im, ax=ax4, label="Flagged transactions")
        st.pyplot(fig4)
    else:
        st.info("No unusual transactions in the current filter selection.")

# ================= TAB 3: ACCOUNT SUMMARIES =================
with tabs[2]:
    st.subheader("Per-Account Summary")
    st.caption(
        "Risk rating is a simple monitoring indicator based on each customer's own share "
        "of flagged transactions (bottom 60% = Low, next 25% = Medium, top 15% = High). "
        "Balances are colour-coded: red = negative, orange = below Rs. 10,000."
    )
    acct_display = account_summary.copy()
    if city_filter:
        acct_display = acct_display[acct_display["city"].isin(city_filter)]
    if acct_type_filter:
        acct_display = acct_display[acct_display["account_type"].isin(acct_type_filter)]

    show_cols = ["customer_id", "name", "account_number", "account_type", "city",
                 "opening_balance", "total_credits", "total_debits", "closing_balance",
                 "transaction_count", "unusual_count", "risk_badge"]
    st.dataframe(
        style_balances(acct_display[show_cols].rename(columns={"risk_badge": "risk_rating"}),
                        "closing_balance"),
        width="stretch", hide_index=True,
    )
    to_csv_download(acct_display[show_cols], "Download account summary (CSV)",
                     "account_summary.csv", "dl_accounts")

    r1, r2, r3 = st.columns(3)
    r1.metric("Low Risk Accounts", int((acct_display["risk_rating"] == "Low").sum()))
    r2.metric("Medium Risk Accounts", int((acct_display["risk_rating"] == "Medium").sum()))
    r3.metric("High Risk Accounts", int((acct_display["risk_rating"] == "High").sum()))

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Closing Balance Distribution")
        fig5, ax5 = plt.subplots(figsize=(6, 3.5))
        ax5.hist(acct_display["closing_balance"], bins=15, color="#1B4965", edgecolor="white")
        ax5.set_xlabel("Closing Balance (Rs.)")
        ax5.set_ylabel("Number of Accounts")
        st.pyplot(fig5)
    with col4:
        st.subheader("Top 10 Accounts by Closing Balance")
        top_accts = acct_display.sort_values("closing_balance", ascending=False).head(10)
        fig6, ax6 = plt.subplots(figsize=(6, 3.5))
        ax6.barh(top_accts["name"], top_accts["closing_balance"], color="#F4D35E", edgecolor="#0B1F3A")
        ax6.invert_yaxis()
        ax6.set_xlabel("Closing Balance (Rs.)")
        st.pyplot(fig6)

# ================= TAB 4: MONTHLY REPORTS =================
with tabs[3]:
    st.subheader("Month-by-Month Transaction Report")
    monthly_display = monthly_report.copy()
    monthly_display["credit_change_pct"] = monthly_display["credit_change_pct"].round(1)
    monthly_display["debit_change_pct"] = monthly_display["debit_change_pct"].round(1)
    st.dataframe(monthly_display, width="stretch", hide_index=True)
    to_csv_download(monthly_display, "Download monthly report (CSV)",
                     "monthly_report.csv", "dl_monthly")

    st.subheader("Net Flow Trend (Credits minus Debits)")
    fig7, ax7 = plt.subplots(figsize=(9, 3.5))
    colors = ["#1B4965" if v >= 0 else "#C1121F" for v in monthly_report["net_flow"]]
    ax7.bar(monthly_report["month"], monthly_report["net_flow"], color=colors)
    ax7.axhline(0, color="black", linewidth=0.8)
    ax7.set_ylabel("Net Flow (Rs.)")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig7)

    st.subheader("Unusual Transactions Flagged per Month")
    st.bar_chart(monthly_report.set_index("month")["unusual_count"])

# ================= TAB 5: CUSTOMER ACTIVITY =================
with tabs[4]:
    st.subheader("Customer Activity Ranking")
    st.caption(
        "Activity score (0-100) blends how often a customer transacts, how much "
        "money moves through their account, and how varied their spending is."
    )
    activity_display = customer_activity.copy()
    if city_filter:
        activity_display = activity_display[activity_display["city"].isin(city_filter)]

    st.dataframe(activity_display, width="stretch", hide_index=True)
    to_csv_download(activity_display, "Download customer activity (CSV)",
                     "customer_activity.csv", "dl_activity")

    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Top 10 Most Active Customers")
        top_active = activity_display.head(10)
        fig8, ax8 = plt.subplots(figsize=(6, 3.5))
        ax8.barh(top_active["name"], top_active["activity_score"], color="#1B4965")
        ax8.invert_yaxis()
        ax8.set_xlabel("Activity Score")
        st.pyplot(fig8)
    with col6:
        st.subheader("Most Common Spending Category (overall)")
        top_cat_counts = activity_display["top_category"].value_counts()
        fig9, ax9 = plt.subplots(figsize=(6, 3.5))
        ax9.bar(top_cat_counts.index, top_cat_counts.values, color="#F4A259")
        plt.xticks(rotation=45, ha="right")
        ax9.set_ylabel("Number of Customers")
        st.pyplot(fig9)

# ================= TAB 6: CUSTOMER 360 =================
with tabs[5]:
    st.subheader("Customer 360 - Search & Profile View")
    search_options = account_summary.apply(
        lambda r: f"{r['name']} ({r['customer_id']} / {r['account_number']})", axis=1
    ).tolist()
    choice = st.selectbox("Search for a customer by name, ID, or account number", search_options)
    chosen_id = choice.split("(")[1].split(" / ")[0]

    cust_row = account_summary[account_summary["customer_id"] == chosen_id].iloc[0]
    cust_activity_row = customer_activity[customer_activity["customer_id"] == chosen_id]
    cust_txns = txn_df[txn_df["customer_id"] == chosen_id].sort_values("date", ascending=False)

    st.markdown(
        f"""
        <div class="profile-card">
        <b>{cust_row['name']}</b> &nbsp;|&nbsp; {cust_row['account_number']} ({cust_row['account_type']})
        &nbsp;|&nbsp; {cust_row['city']} &nbsp;|&nbsp; Risk: {cust_row['risk_badge']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Closing Balance (Rs.)", f"{cust_row['closing_balance']:,.0f}")
    p2.metric("Total Transactions", int(cust_row["transaction_count"]))
    p3.metric("Flagged Unusual", int(cust_row["unusual_count"]))
    p4.metric("Activity Score", cust_activity_row["activity_score"].iloc[0] if len(cust_activity_row) else "-")

    st.subheader("Balance Over Time")
    fig10, ax10 = plt.subplots(figsize=(9, 3))
    ax10.plot(cust_txns.sort_values("date")["date"], cust_txns.sort_values("date")["balance_after"],
              color="#1B4965", linewidth=1.5)
    ax10.set_ylabel("Balance (Rs.)")
    st.pyplot(fig10)

    col7, col8 = st.columns([2, 1])
    with col7:
        st.subheader("Full Transaction History")
        hist_cols = ["transaction_id", "date", "type", "category", "amount", "balance_after", "is_unusual"]
        st.dataframe(cust_txns[hist_cols], width="stretch", hide_index=True)
        to_csv_download(cust_txns[hist_cols], "Download this customer's transactions (CSV)",
                         f"{chosen_id}_transactions.csv", "dl_customer_txns")
    with col8:
        st.subheader("Spending Mix")
        cat_counts = cust_txns["category"].value_counts()
        fig11, ax11 = plt.subplots(figsize=(4, 4))
        ax11.pie(cat_counts.values, labels=cat_counts.index, autopct="%1.0f%%",
                 colors=plt.cm.YlGnBu_r(np.linspace(0.2, 0.9, len(cat_counts))))
        st.pyplot(fig11)

# ================= TAB 7: CITY COMPARISON =================
with tabs[6]:
    st.subheader("City / Branch-wise Comparison")
    st.caption("Compares transaction volume, average balance, and unusual-transaction rate across cities.")
    st.dataframe(city_comparison, width="stretch", hide_index=True)
    to_csv_download(city_comparison, "Download city comparison (CSV)",
                     "city_comparison.csv", "dl_city")

    col9, col10 = st.columns(2)
    with col9:
        st.subheader("Total Transaction Volume by City")
        fig12, ax12 = plt.subplots(figsize=(6, 4))
        ordered = city_comparison.sort_values("total_volume", ascending=True)
        ax12.barh(ordered["city"], ordered["total_volume"], color="#1B4965")
        ax12.set_xlabel("Total Volume (Rs.)")
        st.pyplot(fig12)
    with col10:
        st.subheader("Unusual-Transaction Rate by City (%)")
        fig13, ax13 = plt.subplots(figsize=(6, 4))
        ordered2 = city_comparison.sort_values("unusual_rate_pct", ascending=True)
        colors2 = ["#C1121F" if v > ordered2["unusual_rate_pct"].median() else "#F4A259"
                   for v in ordered2["unusual_rate_pct"]]
        ax13.barh(ordered2["city"], ordered2["unusual_rate_pct"], color=colors2)
        ax13.set_xlabel("Unusual Rate (%)")
        st.pyplot(fig13)

# ================= TAB 8: TOP MOVERS =================
with tabs[7]:
    st.subheader("Top Movers - Biggest Balance Changes")
    if top_movers is None or len(top_movers) == 0:
        st.info("Not enough monthly history to compute movers.")
    else:
        st.caption(f"Comparing account balances at the end of {latest_month} vs {prev_month}.")
        gainers = top_movers.head(10)
        losers = top_movers.tail(10).sort_values("change")

        col11, col12 = st.columns(2)
        with col11:
            st.markdown("**Top 10 Balance Increases**")
            fig14, ax14 = plt.subplots(figsize=(6, 4))
            ax14.barh(gainers["name"], gainers["change"], color="#1B4965")
            ax14.invert_yaxis()
            ax14.set_xlabel("Balance Change (Rs.)")
            st.pyplot(fig14)
        with col12:
            st.markdown("**Top 10 Balance Decreases**")
            fig15, ax15 = plt.subplots(figsize=(6, 4))
            ax15.barh(losers["name"], losers["change"], color="#C1121F")
            ax15.invert_yaxis()
            ax15.set_xlabel("Balance Change (Rs.)")
            st.pyplot(fig15)

        st.subheader("Full Movers Table")
        movers_display = top_movers[["customer_id", "name", "city", "account_number",
                                      "prev_balance", "latest_balance", "change"]]
        st.dataframe(movers_display, width="stretch", hide_index=True)
        to_csv_download(movers_display, "Download top movers (CSV)",
                         "top_movers.csv", "dl_movers")

st.markdown("---")
st.caption(
    "Banking Transaction Analysis Dashboard | Synthetic demo data generated with a fixed "
    "random seed for repeatable results | Prepared by Anisha M."
)
