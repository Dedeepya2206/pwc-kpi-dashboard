import pandas as pd
import streamlit as st
import plotly.express as px

# ---------- Load Data ----------
@st.cache_data
def load_data():
    df = pd.read_csv("data/sales_data.csv", parse_dates=["date"])
    return df

df = load_data()

# ---------- Cleaning ----------
df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)
df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce").fillna(0)

# ---------- Title ----------
st.title("Enterprise Data Analytics & KPI Monitoring System")

# ---------- Filters ----------
st.subheader("Filters")

min_date = df["date"].min().date()      # ✔ uncommented
max_date = df["date"].max().date()

date_range = st.date_input(
    "Select Date Range",
    value=(min_date, max_date)
)

# Handle single date selection
if isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date = date_range
    end_date = date_range

# REGION FILTER
regions = filtered_df["region"].unique().tolist()
selected_region = st.selectbox("Select Region", ["All"] + regions)

if selected_region != "All":
    filtered_df = filtered_df[filtered_df["region"] == selected_region]

# PRODUCT FILTER
products = filtered_df["product_name"].unique().tolist()
selected_product = st.selectbox("Select Product", ["All"] + products)

if selected_product != "All":
    filtered_df = filtered_df[filtered_df["product_name"] == selected_product]


# ---------- KPIs ----------
total_revenue = filtered_df["revenue"].sum()
total_units = filtered_df["units_sold"].sum()
unique_customers = filtered_df["customer_id"].nunique()
avg_order_value = total_revenue / max(1, len(filtered_df))

# Monthly Revenue Growth
monthly = filtered_df.resample("Me", on="date")["revenue"].sum()

if len(monthly) > 1:
    growth = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2]) * 100
else:
    growth = 0

# ---------- KPI Cards ----------
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Revenue", f"₹{total_revenue:,}")
k2.metric("Units Sold", f"{total_units:,}")
k3.metric("Customers", f"{unique_customers:,}")
k4.metric("Avg Order Value", f"₹{avg_order_value:,.2f}")
k5.metric("Monthly Growth", f"{growth:.2f}%")


# ---------- Revenue Over Time Chart ----------
fig = px.line(
    filtered_df,
    x="date",
    y="revenue",
    title="Revenue Over Time"
)
st.plotly_chart(fig, width="stretch", key="revenue_time_chart")


# ---------- Revenue by Region Chart ----------
fig2 = px.bar(
    filtered_df,
    x="region",
    y="revenue",
    title="Revenue by Region"
)
st.plotly_chart(fig2, width="stretch", key="revenue_region_chart")


# ---------- Top Products ----------
st.subheader("Top Products")
top = filtered_df.groupby("product_name")[["revenue", "units_sold"]].sum().reset_index()
top = top.sort_values("revenue", ascending=False)
st.table(top)


# ---------- Revenue Share by Region (Pie Chart) ----------
region_pie = filtered_df.groupby("region")["revenue"].sum().reset_index()

fig3 = px.pie(
    region_pie,
    names="region",
    values="revenue",
    title="Revenue Distribution by Region"
)
st.plotly_chart(fig3, width="stretch", key="revenue_pie_chart")


# ---------- Product Performance ----------
product_perf = filtered_df.groupby("product_name")[["revenue", "units_sold"]].sum().reset_index()

fig4 = px.bar(
    product_perf,
    x="product_name",
    y="revenue",
    color="units_sold",
    title="Product Performance (Revenue vs Units Sold)",
)
st.plotly_chart(fig4, width="stretch", key="product_performance_chart")



# ---------- Download Filtered Data ----------
st.subheader("Download Data")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name="filtered_data.csv",
    mime="text/csv"
)
