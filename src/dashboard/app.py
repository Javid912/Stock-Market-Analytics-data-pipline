import streamlit as st

# Must be the first Streamlit command
st.set_page_config(page_title="DataPipe Analytics Dashboard", layout="wide")

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from pathlib import Path

# Clear any existing environment variables that might interfere
for key in ['POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB', 'POSTGRES_HOST', 'POSTGRES_PORT']:
    if key in os.environ:
        del os.environ[key]

# Load dashboard-specific environment variables
dashboard_dir = Path(__file__).parent
env_path = dashboard_dir / '.env'
if not env_path.exists():
    st.error(f"Could not find .env file in {dashboard_dir}")
else:
    st.success(f"Found .env file at {env_path}")
    load_dotenv(env_path)

# Debug connection parameters
connection_params = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432")
}

# Additional debug information
st.write("Debug - Environment File Path:", str(env_path))
st.write("Debug - Connection Parameters:", {k: v for k, v in connection_params.items() if k != "password"})

# Database connection with better error handling
def get_db_connection():
    try:
        return psycopg2.connect(
            **connection_params,
            cursor_factory=RealDictCursor
        )
    except psycopg2.Error as e:
        st.error(f"""
        Failed to connect to database. Please check:
        1. Docker containers are running
        2. Database port (5432) is exposed
        3. Database credentials are correct
        
        Error details: {str(e)}
        """)
        raise

# Data loading functions
def load_company_data():
    with get_db_connection() as conn:
        return pd.read_sql("""
            SELECT 
                symbol,
                company_name,
                sector,
                market_cap,
                pe_ratio,
                last_close_price,
                avg_daily_volume
            FROM marts.dim_company
            WHERE market_cap IS NOT NULL
            ORDER BY market_cap DESC
            LIMIT 100
        """, conn)

def load_stock_prices(symbol):
    with get_db_connection() as conn:
        return pd.read_sql("""
            SELECT 
                trading_date,
                close_price,
                volume
            FROM staging.stg_daily_prices
            WHERE symbol = %s
            ORDER BY trading_date DESC
            LIMIT 90
        """, conn, params=(symbol,))

# Dashboard layout
st.title("DataPipe Analytics Dashboard")

# Sidebar for filters
st.sidebar.header("Filters")
min_market_cap = st.sidebar.number_input(
    "Minimum Market Cap (Billions)",
    min_value=0.0,
    value=1.0,
    step=0.1
)

# Load data
try:
    companies_df = load_company_data()
    companies_df["market_cap_billions"] = companies_df["market_cap"] / 1e9
    filtered_companies = companies_df[companies_df["market_cap_billions"] >= min_market_cap]

    # Company Overview Section
    st.header("Company Overview")
    st.dataframe(
        filtered_companies[["symbol", "company_name", "sector", "market_cap_billions", "pe_ratio", "last_close_price"]],
        hide_index=True
    )

    # Stock Details Section
    st.header("Stock Details")
    selected_symbol = st.selectbox(
        "Select a company to view details",
        filtered_companies["symbol"].tolist()
    )

    if selected_symbol:
        col1, col2 = st.columns(2)
        
        # Company Info
        with col1:
            company = filtered_companies[filtered_companies["symbol"] == selected_symbol].iloc[0]
            st.subheader(f"{company['company_name']} ({selected_symbol})")
            st.metric("Market Cap (B)", f"${company['market_cap_billions']:.2f}B")
            st.metric("P/E Ratio", f"{company['pe_ratio']:.2f}" if pd.notna(company['pe_ratio']) else "N/A")
            st.metric("Last Close", f"${company['last_close_price']:.2f}")

        # Price Chart
        with col2:
            prices_df = load_stock_prices(selected_symbol)
            if not prices_df.empty:
                prices_df = prices_df.sort_values("trading_date")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=prices_df["trading_date"],
                    y=prices_df["close_price"],
                    name="Close Price"
                ))
                fig.update_layout(
                    title=f"{selected_symbol} - 90 Day Price History",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Data refreshes automatically every 24 hours. Last update: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 