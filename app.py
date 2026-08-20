import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="OrionFleet Analytics", layout="wide")

st.title("📊 OrionFleet Logistics: Profit Leakage & Performance Dashboard")
st.markdown("Interactive Business Analytics & Operational Risk Assessment")

# 2. Data Loading & Cleaning
@st.cache_data
def load_data():
    customers = pd.read_csv('customers.csv')
    transactions = pd.read_csv('transactions.csv')
    products = pd.read_csv('products.csv')
    tickets = pd.read_csv('support_tickets.csv')
    
    # Merge datasets
    df = transactions.merge(products, on='product_id', how='left').merge(customers, on='customer_id', how='left')
    df['margin_pct'] = df['estimated_margin'] / df['net_revenue']
    return df, customers, tickets

df, customers, tickets = load_data()

# 3. Sidebar Filters
st.sidebar.header("Filter Options")
selected_region = st.sidebar.multiselect("Select Region", options=df['region'].dropna().unique(), default=df['region'].dropna().unique())
selected_category = st.sidebar.multiselect("Select Product Category", options=df['category'].dropna().unique(), default=df['category'].dropna().unique())

# Filtered DataFrame
filtered_df = df[(df['region'].isin(selected_region)) & (df['category'].isin(selected_category))]

# 4. Top Key Performance Indicators (KPIs)
col1, col2, col3, col4 = st.columns(4)
total_rev = filtered_df['net_revenue'].sum()
unpaid_rev = filtered_df[filtered_df['payment_status'] != 'Paid']['net_revenue'].sum()
neg_margin_count = len(filtered_df[filtered_df['estimated_margin'] < 0])
avg_margin = filtered_df['margin_pct'].mean() * 100

col1.metric("Net Billed Revenue", f"₹{total_rev:,.2f}")
col2.metric("Uncollected Exposure", f"₹{unpaid_rev:,.2f}", f"{(unpaid_rev/total_rev*100):.1f}% Risk", delta_color="inverse")
col3.metric("Avg Profit Margin", f"{avg_margin:.1f}%")
col4.metric("Negative Margin Sales", f"{neg_margin_count}", "Direct Losses", delta_color="inverse")

st.markdown("---")

# 5. Interactive Charts Layout
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("1. Revenue Exposure by Payment Status")
    pay_fig = px.bar(
        filtered_df.groupby('payment_status')['net_revenue'].sum().reset_index(),
        x='payment_status', y='net_revenue', color='payment_status',
        color_discrete_map={'Paid': '#2ca02c', 'Pending': '#ff7f0e', 'Failed': '#d62728', 'Refunded': '#9467bd'},
        labels={'net_revenue': 'Revenue (INR)', 'payment_status': 'Payment Status'}
    )
    st.plotly_chart(pay_fig, use_container_width=True)

with row1_col2:
    st.subheader("2. Profit Margin Erosion vs. Discount Rate")
    disc_summary = filtered_df.groupby('discount_pct')['margin_pct'].mean().reset_index()
    disc_fig = px.line(
        disc_summary, x='discount_pct', y='margin_pct', markers=True,
        labels={'discount_pct': 'Discount Rate', 'margin_pct': 'Margin %'},
        line_shape='linear'
    )
    st.plotly_chart(disc_fig, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("3. Uncollected Revenue Exposure by Region")
    unpaid_df = filtered_df[filtered_df['payment_status'] != 'Paid']
    reg_fig = px.bar(
        unpaid_df.groupby('region')['net_revenue'].sum().reset_index().sort_values(by='net_revenue', ascending=False),
        x='region', y='net_revenue', color='net_revenue', color_continuous_scale='Reds'
    )
    st.plotly_chart(reg_fig, use_container_width=True)

with row2_col2:
    st.subheader("4. Customer Health Distribution")
    cust_fig = px.pie(customers, names='account_status', hole=0.4, title="Customer Account Status")
    st.plotly_chart(cust_fig, use_container_width=True)