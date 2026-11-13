
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Configuration
st.set_page_config(
    page_title="Bank Churn Dashboard",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Bank Customer Churn Dashboard")
st.caption("Interactive Customer Retention & Churn Analysis")

# Load Dataset
uploaded_file = st.sidebar.file_uploader(
    "Upload Bank Dataset",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
elif os.path.exists("Churn_Modelling.csv"):
    df = pd.read_csv("Churn_Modelling.csv")
else:
    st.info("Please upload Churn_Modelling.csv")
    st.stop()

# Data Preparation
df.columns = df.columns.str.strip()
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

df = df.drop(
    columns=["RowNumber", "CustomerId", "Surname"],
    errors="ignore"
)

df["AgeGroup"] = pd.cut(
    df["Age"],
    bins=[0, 25, 35, 45, 55, 100],
    labels=["18-25", "26-35", "36-45", "46-55", "55+"]
)

# Sidebar Filters
st.sidebar.header("Dashboard Filters")

geographies = ["All"] + sorted(
    df["Geography"].dropna().unique().tolist()
)

genders = ["All"] + sorted(
    df["Gender"].dropna().unique().tolist()
)

selected_geo = st.sidebar.selectbox(
    "Select Geography", geographies
)

selected_gender = st.sidebar.selectbox(
    "Select Gender", genders
)

filtered = df.copy()

if selected_geo != "All":
    filtered = filtered[
        filtered["Geography"] == selected_geo
    ]

if selected_gender != "All":
    filtered = filtered[
        filtered["Gender"] == selected_gender
    ]

# KPI Calculations
total = len(filtered)
exited = int(filtered["Exited"].sum())
retained = total - exited

churn_rate = (
    exited / total * 100 if total else 0
)

# KPI Cards
st.subheader("Business KPIs")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Customers", f"{total:,}")
c2.metric("Exited Customers", f"{exited:,}")
c3.metric("Retained Customers", f"{retained:,}")
c4.metric("Churn Rate", f"{churn_rate:.2f}%")

st.divider()

# Geography and Gender Charts
st.subheader("Customer Churn Analysis")

col1, col2 = st.columns(2)

with col1:
    geo = filtered.groupby(
        "Geography"
    )["Exited"].mean().mul(100).reset_index()

    fig = px.bar(
        geo,
        x="Geography",
        y="Exited",
        color="Geography",
        title="Geography-wise Churn Rate",
        labels={"Exited": "Churn Rate (%)"}
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    gender = filtered.groupby(
        "Gender"
    )["Exited"].mean().mul(100).reset_index()

    fig = px.pie(
        gender,
        names="Gender",
        values="Exited",
        title="Gender-wise Churn Rate",
        hole=0.4
    )

    st.plotly_chart(fig, use_container_width=True)

# Age and Product Analysis
col3, col4 = st.columns(2)

with col3:
    age = filtered.groupby(
        "AgeGroup",
        observed=False
    )["Exited"].mean().mul(100).reset_index()

    fig = px.bar(
        age,
        x="AgeGroup",
        y="Exited",
        title="Age-wise Churn Rate",
        labels={"Exited": "Churn Rate (%)"}
    )

    st.plotly_chart(fig, use_container_width=True)

with col4:
    product = filtered.groupby(
        "NumOfProducts"
    )["Exited"].mean().mul(100).reset_index()

    fig = px.bar(
        product,
        x="NumOfProducts",
        y="Exited",
        title="Product-wise Churn Rate",
        labels={"Exited": "Churn Rate (%)"}
    )

    st.plotly_chart(fig, use_container_width=True)

# Active Member Analysis
st.subheader("Active Member Analysis")

active = filtered.groupby(
    "IsActiveMember"
)["Exited"].mean().mul(100).reset_index()

active["Member Status"] = active[
    "IsActiveMember"
].map({1: "Active", 0: "Inactive"})

fig = px.bar(
    active,
    x="Member Status",
    y="Exited",
    color="Member Status",
    title="Active vs Inactive Churn Rate",
    labels={"Exited": "Churn Rate (%)"}
)

st.plotly_chart(fig, use_container_width=True)

# Customer Data
st.subheader("Customer Details")

status = st.selectbox(
    "Customer Status",
    ["All", "Exited", "Retained"]
)

if status == "Exited":
    display_data = filtered[filtered["Exited"] == 1]
elif status == "Retained":
    display_data = filtered[filtered["Exited"] == 0]
else:
    display_data = filtered

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)

# Download Filtered Data
csv = display_data.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Customer Data",
    data=csv,
    file_name="filtered_customers.csv",
    mime="text/csv"
)

st.caption("Bank Customer Churn Analysis | Python & Streamlit")
