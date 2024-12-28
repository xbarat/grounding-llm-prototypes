import streamlit as st
import httpx
import json
import pandas as pd
import plotly.express as px
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="GIRAFFE Sandbox",
    page_icon="🦒",
    layout="wide"
)

# Backend configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")
TIMEOUT_SECONDS = 10.0

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'current_platform' not in st.session_state:
    st.session_state.current_platform = None
if 'platform_data' not in st.session_state:
    st.session_state.platform_data = {}
if 'backend_status' not in st.session_state:
    st.session_state.backend_status = False

async def check_backend_connection() -> bool:
    """Check if backend is accessible."""
    try:
        base_url = BACKEND_URL.replace("/api/v1", "")  # Get base URL without version
        endpoints = [
            f"{base_url}/health",  # Try health check endpoint first
            f"{base_url}/",        # Try root endpoint
            BACKEND_URL,           # Try API endpoint
        ]
        
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            for endpoint in endpoints:
                try:
                    response = await client.get(endpoint)
                    if response.status_code == 200:
                        return True
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        st.warning(f"Backend returned status code {response.status_code}")
                        return False
                except httpx.RequestError:
                    continue  # Try next endpoint
            
            st.error("""
            Backend server is not accessible. Please ensure:
            1. Backend server is running (uvicorn app.main:app --reload)
            2. Backend URL is correct in .env file
            3. No firewall is blocking the connection
            """)
            return False
            
    except Exception as e:
        st.error(f"Error checking backend connection: {str(e)}")
        return False

async def fetch_data(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Fetch data from backend API."""
    if not st.session_state.backend_status:
        st.error("Backend is not accessible. Please check your connection.")
        return {}
        
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(
                f"{BACKEND_URL}{endpoint}", 
                params=params or {}
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        st.error("Request timed out. Please try again.")
        return {}
    except httpx.HTTPError as e:
        st.error(f"Error fetching data: {str(e)}")
        return {}
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return {}

async def process_query(query: str) -> Dict[str, Any]:
    """Send query to backend for processing."""
    if not st.session_state.current_platform:
        st.error("Please select a platform first.")
        return {}
        
    if not st.session_state.backend_status:
        st.error("Backend is not accessible. Please check your connection.")
        return {}
        
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{BACKEND_URL}/platforms/analyze",
                json={
                    "query": query,
                    "platform": st.session_state.current_platform,
                    "platform_data": st.session_state.platform_data
                }
            )
            
            if response.status_code == 404:
                st.error("""
                API endpoint not found. Please ensure:
                1. Backend routes are properly configured
                2. API version matches (/api/v1)
                3. Endpoint path is correct (/platforms/analyze)
                """)
                return {}
            elif response.status_code == 401:
                st.error("Authentication required. Please check your credentials.")
                return {}
            elif response.status_code == 403:
                st.error("Access forbidden. Please check your permissions.")
                return {}
            elif response.status_code >= 500:
                st.error("Backend server error. Please check the server logs.")
                return {}
                
            response.raise_for_status()
            return response.json()
            
    except httpx.TimeoutException:
        st.error("""
        Request timed out. Please:
        1. Check backend server responsiveness
        2. Increase timeout in .env file
        3. Try again with a simpler query
        """)
        return {}
    except httpx.HTTPError as e:
        st.error(f"Error processing query: {str(e)}")
        return {}
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return {}

def display_visualization(data: pd.DataFrame, viz_type: str, config: Dict[str, Any]):
    """Display visualization based on analysis requirements."""
    if data.empty:
        st.warning("No data available for visualization.")
        return
        
    try:
        if viz_type == "line_chart":
            fig = px.line(data, **config)
        elif viz_type == "scatter_plot":
            fig = px.scatter(data, **config)
        elif viz_type == "bar_chart":
            fig = px.bar(data, **config)
        elif viz_type == "dual_line_chart":
            fig = px.line(data, **config)
        else:
            st.warning(f"Unsupported visualization type: {viz_type}")
            return
            
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")

def display_metrics(data: pd.DataFrame, metrics: List[str]):
    """Display metrics in a clean format."""
    if data.empty:
        st.warning("No data available for metrics.")
        return
        
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        try:
            value = data[metric].mean() if len(data) > 0 else 0
            col.metric(
                label=metric.replace('_', ' ').title(),
                value=f"{value:.2f}"
            )
        except Exception as e:
            col.error(f"Error calculating {metric}: {str(e)}")

# Check backend connection
if st.session_state.backend_status is False:
    with st.spinner("Checking backend connection..."):
        st.session_state.backend_status = asyncio.run(check_backend_connection())
        
    if st.session_state.backend_status:
        st.success("Connected to backend successfully!")
    else:
        st.error("Cannot connect to backend. Please check if the backend server is running.")

# Sidebar
with st.sidebar:
    st.title("🦒 GIRAFFE Sandbox")
    
    # Connection status
    status_color = "🟢" if st.session_state.backend_status else "🔴"
    st.write(f"{status_color} Backend Status")
    
    if not st.session_state.backend_status:
        if st.button("Retry Connection"):
            st.session_state.backend_status = asyncio.run(check_backend_connection())
    
    # Platform selection
    platform = st.selectbox(
        "Select Platform",
        ["F1", "TypeRacer"],
        index=0 if st.session_state.current_platform == "F1" else 1,
        disabled=not st.session_state.backend_status
    )
    
    if platform != st.session_state.current_platform:
        st.session_state.current_platform = platform
        st.session_state.platform_data = {}
    
    # Platform-specific inputs
    if platform == "F1":
        driver = st.text_input(
            "Driver Name (e.g., max_verstappen)",
            disabled=not st.session_state.backend_status
        )
        if driver:
            st.session_state.platform_data["driver"] = driver
    else:
        username = st.text_input(
            "TypeRacer Username",
            disabled=not st.session_state.backend_status
        )
        if username:
            st.session_state.platform_data["username"] = username
    
    # Query history
    st.subheader("Query History")
    for query in st.session_state.query_history[-5:]:  # Show last 5 queries
        st.text(query)

# Main content
st.title("Query Sandbox")

# Query input
query = st.text_area(
    "Enter your query",
    height=100,
    disabled=not st.session_state.backend_status
)
process_button = st.button(
    "Process Query",
    disabled=not st.session_state.backend_status or not query
)

if process_button and query:
    # Add to history
    st.session_state.query_history.append(query)
    
    # Process query
    with st.spinner("Processing query..."):
        result = asyncio.run(process_query(query))
        
        if result:
            # Display results in tabs
            tabs = st.tabs(["Visualization", "Raw Data", "Metrics"])
            
            with tabs[0]:
                if "visualization" in result:
                    display_visualization(
                        pd.DataFrame(result.get("data", {})),
                        result["visualization"]["type"],
                        result["visualization"]["config"]
                    )
                    
            with tabs[1]:
                if "data" in result:
                    st.dataframe(pd.DataFrame(result["data"]))
                    
            with tabs[2]:
                if "metrics" in result:
                    display_metrics(
                        pd.DataFrame(result.get("data", {})),
                        result["metrics"]
                    )

# Example queries
if st.session_state.backend_status:
    st.subheader("Example Queries")
    examples = {
        "F1": [
            "Show me Max Verstappen's performance trend in the last 5 races",
            "Compare Hamilton and Verstappen's qualifying performances",
            "Show the points distribution for all drivers this season"
        ],
        "TypeRacer": [
            "Show my typing speed trend over the last 100 races",
            "Compare my accuracy and WPM correlation",
            "Show my daily average performance"
        ]
    }

    current_platform = st.session_state.current_platform or "F1"
    for example in examples[current_platform]:
        if st.button(example):
            # Set the query and trigger processing
            query = example
            st.session_state.query_history.append(query)
            with st.spinner("Processing query..."):
                result = asyncio.run(process_query(query))
                
                if result:
                    # Display results in tabs
                    tabs = st.tabs(["Visualization", "Raw Data", "Metrics"])
                    
                    with tabs[0]:
                        if "visualization" in result:
                            display_visualization(
                                pd.DataFrame(result.get("data", {})),
                                result["visualization"]["type"],
                                result["visualization"]["config"]
                            )
                            
                    with tabs[1]:
                        if "data" in result:
                            st.dataframe(pd.DataFrame(result["data"]))
                            
                    with tabs[2]:
                        if "metrics" in result:
                            display_metrics(
                                pd.DataFrame(result.get("data", {})),
                                result["metrics"]
                            ) 