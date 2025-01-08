import streamlit as st
import pandas as pd
import json
import httpx
import asyncio
from datetime import datetime
from pathlib import Path
from query_analyzer import QueryAnalyzer
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Query Processing Analyzer", layout="wide")

def load_test_queries():
    """Load sample test queries from file or return defaults"""
    try:
        with open('test_queries.json', 'r') as f:
            return json.load(f)
    except:
        return [
            "Show me Lewis Hamilton's performance in 2023",
            "What was Max Verstappen's qualifying position in Monaco?",
            "Compare lap times between Leclerc and Sainz",
            "Who had the most podiums in 2022?",
            "Show me the pit stop times for Red Bull Racing"
        ]

def save_test_queries(queries):
    """Save test queries to file"""
    with open('test_queries.json', 'w') as f:
        json.dump(queries, f)

async def test_query(query: str, api_url: str = "http://localhost:8000"):
    """Test a single query against the API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_url}/api/v1/process_query",
                json={"query": query}
            )
            return response.json()
    except Exception as e:
        return {"error": str(e)}

def analyze_logs():
    """Analyze query processing logs"""
    analyzer = QueryAnalyzer()
    if analyzer.parse_logs():
        return analyzer.generate_report()
    return None

def plot_success_rate(report):
    """Create success rate visualization"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=report["summary"]["success_rate"] * 100,
        title={'text': "Query Success Rate"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "darkblue"},
               'steps': [
                   {'range': [0, 50], 'color': "red"},
                   {'range': [50, 80], 'color': "yellow"},
                   {'range': [80, 100], 'color': "green"}
               ]}
    ))
    return fig

def plot_failure_reasons(report):
    """Create failure reasons visualization"""
    failure_data = pd.DataFrame(
        report["failure_analysis"]["common_failures"].items(),
        columns=["Reason", "Count"]
    )
    if not failure_data.empty:
        fig = px.bar(failure_data, x="Count", y="Reason", orientation='h',
                    title="Common Failure Reasons")
        return fig
    return None

def plot_endpoint_usage(report):
    """Create endpoint usage visualization"""
    endpoint_data = pd.DataFrame(
        report["endpoint_analysis"]["endpoint_usage"].items(),
        columns=["Endpoint", "Count"]
    )
    if not endpoint_data.empty:
        fig = px.pie(endpoint_data, values="Count", names="Endpoint",
                    title="Endpoint Usage Distribution")
        return fig
    return None

def main():
    st.title("F1 Query Processing Analyzer")
    
    # Sidebar
    st.sidebar.header("Configuration")
    api_url = st.sidebar.text_input("API URL", "http://localhost:8000")
    
    # Test Queries Section
    st.header("Test Queries")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        test_queries = load_test_queries()
        edited_queries = st.text_area(
            "Test Queries (one per line)",
            value="\n".join(test_queries),
            height=200
        )
        
        # Update test queries
        current_queries = edited_queries.split("\n")
        if current_queries != test_queries:
            save_test_queries(current_queries)
    
    with col2:
        st.subheader("Run Tests")
        if st.button("Run All Queries"):
            with st.spinner("Testing queries..."):
                for query in current_queries:
                    if query.strip():
                        st.write(f"Testing: {query}")
                        result = asyncio.run(test_query(query, api_url))
                        st.json(result)
    
    # Analysis Section
    st.header("Analysis")
    
    if st.button("Analyze Logs"):
        report = analyze_logs()
        
        if report:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Summary")
                st.metric("Total Queries", report["summary"]["total_queries"])
                st.metric("Success Rate", f"{report['summary']['success_rate']*100:.1f}%")
                st.metric("Failed Queries", report["summary"]["failed_queries"])
                
                # Success Rate Gauge
                st.plotly_chart(plot_success_rate(report), use_container_width=True)
            
            with col2:
                # Failure Reasons
                failure_fig = plot_failure_reasons(report)
                if failure_fig:
                    st.plotly_chart(failure_fig, use_container_width=True)
            
            # Endpoint Usage
            st.subheader("Endpoint Usage")
            endpoint_fig = plot_endpoint_usage(report)
            if endpoint_fig:
                st.plotly_chart(endpoint_fig, use_container_width=True)
            
            # Export Section
            st.header("Export Data")
            if st.button("Export Failed Queries"):
                analyzer = QueryAnalyzer()
                if analyzer.export_failed_queries("failed_queries.csv"):
                    st.success("Exported failed queries to failed_queries.csv")
                else:
                    st.warning("No failed queries to export")
        else:
            st.warning("No logs available for analysis. Run some queries first.")

if __name__ == "__main__":
    main() 