import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from pathlib import Path
import logging
import traceback
import time
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('tech_market_dashboard')

# Page configuration
st.set_page_config(
    page_title="Tech Market Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Debug mode
DEBUG = True

# Function to handle and display errors
def handle_error(error: Exception, context: str, show_traceback: bool = True):
    error_msg = f"Error in {context}: {str(error)}"
    logger.error(error_msg)
    if show_traceback:
        logger.error(traceback.format_exc())
    st.error(error_msg)
    if DEBUG:
        with st.expander("Debug Information"):
            st.code(traceback.format_exc())
            st.json({
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context
            })

# Function to log performance metrics
def log_performance(func):
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
            if DEBUG:
                st.sidebar.info(f"{func.__name__} took {execution_time:.2f} seconds")
            return result
        except Exception as e:
            handle_error(e, func.__name__)
            return None
    return wrapper

# Custom CSS for modern UI
st.markdown("""
    <style>
    .stApp {
        background-color: #f5f5f5;
    }
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #1E88E5;
    }
    .stSelectbox {
        background-color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

# Debug environment loading
if DEBUG:
    logger.info(f"Project root: {project_root}")
    logger.info(f"Env file path: {env_path}")
    logger.info(f"Env file exists: {env_path.exists()}")

# Database connection configuration with fallback values
connection_params = {
    "dbname": os.getenv("POSTGRES_DB") or "stock_market_db",
    "user": os.getenv("POSTGRES_USER") or "postgres",
    "password": os.getenv("POSTGRES_PASSWORD") or "postgres",
    "host": os.getenv("POSTGRES_HOST") or "localhost",
    "port": os.getenv("POSTGRES_PORT") or "5432"
}

# Log connection parameters (excluding password)
logger.info("Database connection parameters:")
safe_params = {k: v for k, v in connection_params.items() if k != 'password'}
logger.info(f"Connection params: {safe_params}")

# Add connection retry logic
def get_db_connection():
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            # Try to connect with current parameters
            logger.info(f"Attempting database connection (Attempt {attempt + 1}/{max_retries})")
            logger.info(f"Using connection parameters: {safe_params}")
            
            conn = psycopg2.connect(**connection_params, cursor_factory=RealDictCursor)
            logger.info("Database connection established successfully")
            
            # Verify connection works
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            
            if DEBUG:
                st.sidebar.success(f"Database connection successful! (Attempt {attempt + 1})")
            return conn
            
        except psycopg2.Error as e:
            error_msg = f"Database Connection Error (Attempt {attempt + 1}/{max_retries}): {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                
                # If role doesn't exist, try connecting as superuser
                if "role" in str(e) and "does not exist" in str(e):
                    logger.info("Trying to connect with default superuser credentials")
                    connection_params.update({
                        "user": "postgres",
                        "password": "postgres"
                    })
            else:
                st.error(error_msg)
                if DEBUG:
                    st.sidebar.error(f"Connection Error Details: {str(e)}")
                raise

# Add system information debugging
def get_system_info():
    try:
        docker_status = os.popen('docker ps').read()
        postgres_container = os.popen('docker ps | grep postgres').read()
        return {
            "docker_running": bool(docker_status),
            "postgres_container": bool(postgres_container),
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "env_file_exists": os.path.exists(project_root / '.env')
        }
    except Exception as e:
        return {"error": str(e)}

# Display debug information in sidebar
if DEBUG:
    st.sidebar.title("Debug Information")
    
    # System Info
    with st.sidebar.expander("System Information"):
        sys_info = get_system_info()
        st.json(sys_info)
    
    # Connection Info
    with st.sidebar.expander("Connection Parameters"):
        st.json(safe_params)
    
    # Database Status
    with st.sidebar.expander("Database Status"):
        st.write("Click to check database status")
        if st.button("Test Connection"):
            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT version();")
                        version = cur.fetchone()[0]
                        st.success(f"Connected to PostgreSQL:\n{version}")
            except Exception as e:
                st.error(f"Connection failed:\n{str(e)}")

# Database health check
def check_database_health():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check if required tables exist
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'marts' 
                        AND table_name = 'dim_company'
                    );
                """)
                result = cur.fetchone()
                dim_company_exists = result['exists'] if result else False
                
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'staging' 
                        AND table_name = 'stg_daily_prices'
                    );
                """)
                result = cur.fetchone()
                daily_prices_exists = result['exists'] if result else False
                
                health_status = {
                    "database_connected": True,
                    "dim_company_exists": dim_company_exists,
                    "daily_prices_exists": daily_prices_exists
                }
                
                if DEBUG:
                    st.sidebar.write("Database Health Check:", health_status)
                
                logger.info(f"Database health check completed: {health_status}")
                return health_status
                
    except Exception as e:
        handle_error(e, "database_health_check")
        return {
            "database_connected": False,
            "dim_company_exists": False,
            "daily_prices_exists": False
        }

@log_performance
@st.cache_data(ttl=3600)
def load_tech_companies():
    try:
        with get_db_connection() as conn:
            query = """
                SELECT 
                    symbol,
                    company_name,
                    sector,
                    market_cap,
                    pe_ratio,
                    last_close_price,
                    avg_daily_volume,
                    currency
                FROM marts.dim_company
                WHERE sector IN ('Technology', 'Communication Services')
                AND market_cap IS NOT NULL
                ORDER BY market_cap DESC
            """
            logger.info("Executing tech companies query")
            if DEBUG:
                st.sidebar.code(query, language="sql")
            
            df = pd.read_sql(query, conn)
            logger.info(f"Retrieved {len(df)} tech companies")
            if DEBUG:
                st.sidebar.write("Query Result Shape:", df.shape)
                if not df.empty:
                    st.sidebar.write("Sample Data:", df.head(2))
            return df
    except Exception as e:
        handle_error(e, "load_tech_companies")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_stock_prices(symbol):
    try:
        with get_db_connection() as conn:
            query = f"""
                SELECT 
                    trading_date,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume
                FROM staging.stg_daily_prices
                WHERE symbol = '{symbol}'
                ORDER BY trading_date DESC
                LIMIT 180
            """
            if DEBUG:
                st.sidebar.code(query, language="sql")
            
            df = pd.read_sql(query, conn)
            if DEBUG:
                st.sidebar.write(f"Price Data Shape for {symbol}:", df.shape)
            return df
    except Exception as e:
        st.error(f"Error loading price data: {str(e)}")
        if DEBUG:
            st.sidebar.error(f"Load Prices Error: {str(e)}")
        return pd.DataFrame()

# Sidebar
st.sidebar.image("https://your-logo-url.com", width=50)  # Add your logo
st.sidebar.title("Tech Market Analytics")

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["Market Overview", "Company Analysis", "Sector Performance"]
)

# Filters
st.sidebar.header("Filters")
min_market_cap = st.sidebar.number_input(
    "Min Market Cap ($B)",
    min_value=0.0,
    value=10.0,
    step=5.0
)

# Main app execution
def main():
    try:
        logger.info("Starting dashboard application")
        
        # Perform health check
        health_status = check_database_health()
        if not health_status["database_connected"]:
            st.error("Cannot connect to database. Please check your configuration.")
            st.stop()
        
        if not health_status["dim_company_exists"]:
            st.warning("Company dimension table does not exist. Please run the data pipeline first.")
            st.stop()
            
        if not health_status["daily_prices_exists"]:
            st.warning("Daily prices table does not exist. Please run the data pipeline first.")
            st.stop()
        
        # Load data with loading indicator
        with st.spinner("Loading market data..."):
            companies_df = load_tech_companies()
            if companies_df.empty:
                st.warning("No company data available. Please check your database connection and data.")
                st.stop()
            
            companies_df["market_cap_billions"] = companies_df["market_cap"] / 1e9
            filtered_companies = companies_df[companies_df["market_cap_billions"] >= min_market_cap]
            
            if filtered_companies.empty:
                st.warning(f"No companies found with market cap >= ${min_market_cap}B")
                st.stop()
            
            if DEBUG:
                st.sidebar.write("Filtered Companies Shape:", filtered_companies.shape)
    except Exception as e:
        handle_error(e, "main_application")
        st.error("An unexpected error occurred. Please check the logs for details.")

if __name__ == "__main__":
    main()

if page == "Market Overview":
    st.title("Tech Market Overview")
    
    # Market Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        total_market_cap = filtered_companies["market_cap_billions"].sum()
        st.metric("Total Market Cap", f"${total_market_cap:.2f}B")
    with col2:
        avg_pe = filtered_companies["pe_ratio"].mean()
        st.metric("Average P/E", f"{avg_pe:.2f}")
    with col3:
        company_count = len(filtered_companies)
        st.metric("Companies", company_count)

    # Market Cap TreeMap
    fig = px.treemap(
        filtered_companies,
        path=[px.Constant("Tech Sector"), "sector", "symbol"],
        values="market_cap_billions",
        color="market_cap_billions",
        hover_data=["company_name", "last_close_price"],
        color_continuous_scale="RdBu",
        title="Market Cap Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "Company Analysis":
    st.title("Company Analysis")
    
    # Company selector
    selected_symbol = st.selectbox(
        "Select Company",
        filtered_companies["symbol"].tolist(),
        format_func=lambda x: f"{x} - {filtered_companies[filtered_companies['symbol'] == x].iloc[0]['company_name']}"
    )

    if selected_symbol:
        company = filtered_companies[filtered_companies["symbol"] == selected_symbol].iloc[0]
        
        # Company header
        st.header(f"{company['company_name']} ({selected_symbol})")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Market Cap", f"${company['market_cap_billions']:.2f}B")
        with col2:
            st.metric("P/E Ratio", f"{company['pe_ratio']:.2f}" if pd.notna(company['pe_ratio']) else "N/A")
        with col3:
            st.metric("Last Price", f"${company['last_close_price']:.2f}")
        with col4:
            st.metric("Avg Volume", f"{company['avg_daily_volume']:,.0f}")

        # Price chart
        prices_df = load_stock_prices(selected_symbol)
        if not prices_df.empty:
            prices_df = prices_df.sort_values("trading_date")
            
            # Create candlestick chart with volume
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                              vertical_spacing=0.03, row_heights=[0.7, 0.3])

            fig.add_trace(go.Candlestick(
                x=prices_df["trading_date"],
                open=prices_df["open_price"],
                high=prices_df["high_price"],
                low=prices_df["low_price"],
                close=prices_df["close_price"],
                name="Price"
            ), row=1, col=1)

            fig.add_trace(go.Bar(
                x=prices_df["trading_date"],
                y=prices_df["volume"],
                name="Volume",
                marker_color="rgba(0,0,255,0.3)"
            ), row=2, col=1)

            fig.update_layout(
                title=f"{selected_symbol} - Price History",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                yaxis2_title="Volume",
                height=800,
                showlegend=False,
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig, use_container_width=True)

elif page == "Sector Performance":
    st.title("Tech Sector Performance")
    
    # Sector breakdown
    sector_stats = filtered_companies.groupby("sector").agg({
        "market_cap_billions": "sum",
        "symbol": "count"
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            sector_stats,
            values="market_cap_billions",
            names="sector",
            title="Market Cap by Sector"
        )
        st.plotly_chart(fig)
    
    with col2:
        fig = px.bar(
            sector_stats,
            x="sector",
            y="symbol",
            title="Number of Companies by Sector"
        )
        st.plotly_chart(fig)

# Footer
st.markdown("---")
st.markdown(
    f"Data refreshes hourly. Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. "
    "Built with ❤️ using Streamlit, Plotly, and dbt."
) 