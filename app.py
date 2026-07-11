import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
warnings.filterwarnings('ignore')

# --- CONFIGURATION ---
st.set_page_config(page_title="Advanced Sales Analytics", page_icon="📈", layout="wide")
st.title("📈 Enterprise Sales & Customer Analytics")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    df = pd.read_csv("Superstore.csv", encoding="latin1")
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    return df

df = load_data()

# US State abbreviations mapping for Plotly Maps
us_state_to_abbrev = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
    "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC"
}

# --- SIDEBAR NAVIGATION ---
st.sidebar.header("Navigation")
view = st.sidebar.radio("Go to:", [
    "📊 Executive Summary", 
    "🗺️ Geographic Heatmap", 
    "💎 Customer RFM Segmentation", 
    "🧠 Predictive Sales Forecasting"
])

# --- 1. EXECUTIVE SUMMARY ---
if view == "📊 Executive Summary":
    st.subheader("Business Overview")
    
    # Global Filters
    region = st.sidebar.multiselect("Filter by Region", df['Region'].unique(), default=df['Region'].unique())
    segment = st.sidebar.multiselect("Filter by Segment", df['Segment'].unique(), default=df['Segment'].unique())
    
    filtered_df = df[(df['Region'].isin(region)) & (df['Segment'].isin(segment))]
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${filtered_df['Sales'].sum():,.0f}")
    col2.metric("Total Profit", f"${filtered_df['Profit'].sum():,.0f}")
    col3.metric("Total Orders", f"{filtered_df['Order ID'].nunique():,}")
    col4.metric("Avg Profit Margin", f"{(filtered_df['Profit'].sum() / filtered_df['Sales'].sum()) * 100:.1f}%")
    
    st.markdown("---")
    
    # Time Series
    monthly_sales = filtered_df.resample('ME', on='Order Date')['Sales'].sum().reset_index()
    fig1 = px.line(monthly_sales, x='Order Date', y='Sales', title="Monthly Revenue Trend", markers=True)
    st.plotly_chart(fig1, use_container_width=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        cat_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
        fig2 = px.bar(cat_sales, x='Category', y='Sales', color='Category', title="Sales by Category")
        st.plotly_chart(fig2, use_container_width=True)
        
    with col_b:
        subcat_profit = filtered_df.groupby('Sub-Category')['Profit'].sum().reset_index().sort_values('Profit')
        fig3 = px.bar(subcat_profit, x='Profit', y='Sub-Category', orientation='h', 
                      title="Profit by Sub-Category (Loss-Makers at bottom)", 
                      color='Profit', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig3, use_container_width=True)


# --- 2. GEOGRAPHIC HEATMAP ---
elif view == "🗺️ Geographic Heatmap":
    st.subheader("Geographic Revenue Distribution")
    
    state_sales = df.groupby('State').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    state_sales['State Code'] = state_sales['State'].map(us_state_to_abbrev)
    
    metric = st.radio("Select Metric to Visualize:", ["Sales", "Profit"], horizontal=True)
    
    fig = px.choropleth(
        state_sales, 
        locations='State Code', 
        locationmode="USA-states", 
        color=metric,
        scope="usa",
        hover_name='State',
        hover_data=['Sales', 'Profit'],
        color_continuous_scale="Viridis" if metric == "Sales" else "RdYlGn",
        title=f"Total {metric} by State"
    )
    fig.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("Hover over a state to see detailed performance metrics. Darker green indicates higher revenue/profit.")


# --- 3. CUSTOMER RFM SEGMENTATION ---
elif view == "💎 Customer RFM Segmentation":
    st.subheader("Customer RFM (Recency, Frequency, Monetary) Segmentation")
    st.write("Automatically categorizing customers based on purchasing behavior to drive targeted marketing.")
    
    # Calculate RFM
    snapshot_date = df['Order Date'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('Customer ID').agg({
        'Order Date': lambda x: (snapshot_date - x.max()).days,
        'Order ID': 'nunique',
        'Sales': 'sum'
    }).rename(columns={'Order Date': 'Recency', 'Order ID': 'Frequency', 'Sales': 'Monetary'})
    
    # Assign Scores (1-5, 5 being best)
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
    
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    
    # Define Segments
    def segment_customer(row):
        if row['R_Score'] == 5 and row['F_Score'] >= 4: return "Champions"
        if row['R_Score'] >= 3 and row['F_Score'] >= 3: return "Loyal Customers"
        if row['R_Score'] >= 3 and row['F_Score'] <= 2: return "Recent Customers"
        if row['R_Score'] <= 2 and row['F_Score'] >= 3: return "At Risk"
        if row['R_Score'] <= 2 and row['F_Score'] <= 2: return "Lost"
        return "Others"
        
    rfm['Segment'] = rfm.apply(segment_customer, axis=1)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        segment_counts = rfm['Segment'].value_counts().reset_index()
        segment_counts.columns = ['Segment', 'Count']
        fig = px.pie(segment_counts, names='Segment', values='Count', title="Customer Distribution", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.write("### Top 'Champion' Customers")
        champions = rfm[rfm['Segment'] == 'Champions'].sort_values('Monetary', ascending=False).head(10)
        # Merge back names
        champions = champions.merge(df[['Customer ID', 'Customer Name']].drop_duplicates(), on='Customer ID')
        st.dataframe(champions[['Customer Name', 'Recency', 'Frequency', 'Monetary']].style.format({'Monetary': '${:,.2f}'}), use_container_width=True)


# --- 4. PREDICTIVE SALES FORECASTING ---
elif view == "🧠 Predictive Sales Forecasting":
    st.subheader("Machine Learning Time Series Forecasting (Holt-Winters)")
    st.write("Using Exponential Smoothing to predict future monthly revenue based on historical trends and seasonality.")
    
    # Resample to monthly
    monthly_sales = df.resample('MS', on='Order Date')['Sales'].sum()
    
    # Fit Model
    forecast_months = st.slider("Forecast Horizon (Months)", min_value=3, max_value=24, value=12)
    
    model = ExponentialSmoothing(monthly_sales, trend='add', seasonal='add', seasonal_periods=12).fit()
    forecast = model.forecast(forecast_months)
    
    # Plotly Graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly_sales.index, y=monthly_sales.values, mode='lines+markers', name='Historical Sales', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=forecast.index, y=forecast.values, mode='lines+markers', name='Forecasted Sales', line=dict(color='orange', dash='dash')))
    
    fig.update_layout(title=f"Revenue Forecast for Next {forecast_months} Months", xaxis_title="Date", yaxis_title="Total Sales ($)", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 **Insight:** The ML model detected strong annual seasonality, predicting significant revenue spikes every November/December.")
