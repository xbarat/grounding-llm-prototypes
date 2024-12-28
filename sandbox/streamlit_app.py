import streamlit as st
import httpx
import json
import pandas as pd
import plotly.express as px
from typing import Dict, Any, List
import asyncio
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="GIRAFFE Sandbox",
    page_icon="🦒",
    layout="wide"
)

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'current_platform' not in st.session_state:
    st.session_state.current_platform = None
if 'platform_data' not in st.session_state:
    st.session_state.platform_data = {}

# Backend configuration
BACKEND_URL = "http://localhost:8000/api/v1"

async def fetch_data(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Fetch data from backend API."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BACKEND_URL}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            st.error(f"Error fetching data: {str(e)}")
            return {}

async def process_query(query: str) -> Dict[str, Any]:
    """Send query to backend for processing."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BACKEND_URL}/platforms/analyze",
                json={"query": query, "platform": st.session_state.current_platform}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            st.error(f"Error processing query: {str(e)}")
            return {}

def display_visualization(data: pd.DataFrame, viz_type: str, config: Dict[str, Any]):
    """Display visualization based on analysis requirements."""
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

# Sidebar
with st.sidebar:
    st.title("🦒 GIRAFFE Sandbox")
    
    # Platform selection
    platform = st.selectbox(
        "Select Platform",
        ["F1", "TypeRacer"],
        index=0 if st.session_state.current_platform == "F1" else 1
    )
    
    if platform != st.session_state.current_platform:
        st.session_state.current_platform = platform
        st.session_state.platform_data = {}
    
    # Platform-specific inputs
    if platform == "F1":
        driver = st.text_input("Driver Name (e.g., max_verstappen)")
        if driver:
            st.session_state.platform_data["driver"] = driver
    else:
        username = st.text_input("TypeRacer Username")
        if username:
            st.session_state.platform_data["username"] = username
    
    # Query history
    st.subheader("Query History")
    for query in st.session_state.query_history[-5:]:  # Show last 5 queries
        st.text(query)

# Main content
st.title("Query Sandbox")

# Query input
query = st.text_area("Enter your query", height=100)
process_button = st.button("Process Query")

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
                        pd.DataFrame(result["data"]),
                        result["visualization"]["type"],
                        result["visualization"]["config"]
                    )
                    
            with tabs[1]:
                if "data" in result:
                    st.dataframe(pd.DataFrame(result["data"]))
                    
            with tabs[2]:
                if "metrics" in result:
                    display_metrics(
                        pd.DataFrame(result["data"]),
                        result["metrics"]
                    )

# Example queries
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

for example in examples[platform]:
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
                            pd.DataFrame(result["data"]),
                            result["visualization"]["type"],
                            result["visualization"]["config"]
                        )
                        
                with tabs[1]:
                    if "data" in result:
                        st.dataframe(pd.DataFrame(result["data"]))
                        
                with tabs[2]:
                    if "metrics" in result:
                        display_metrics(
                            pd.DataFrame(result["data"]),
                            result["metrics"]
                        ) 