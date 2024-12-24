import streamlit as st
import httpx
import json
import pandas as pd
from datetime import datetime
import asyncio
from typing import Dict, Any

# Constants
BASE_URL = "http://ergast.com/api/f1"

# Configure page
st.set_page_config(
    page_title="F1 API Explorer",
    page_icon="🏎️",
    layout="wide"
)

# Title and description
st.title("🏎️ Formula 1 API Explorer")
st.markdown("""
This app allows you to explore various Formula 1 API endpoints and their responses.
Data is provided by the Ergast Developer API.
""")

# Sidebar for endpoint selection
st.sidebar.header("Endpoint Configuration")

# Define available endpoints
ENDPOINTS = {
    "Current Season Schedule": "current",
    "Driver Standings": "current/driverStandings",
    "Constructor Standings": "current/constructorStandings",
    "Last Race Results": "current/last/results",
    "Qualifying Results": "current/last/qualifying",
    "Driver Season Results": "{year}/drivers/{driver_id}/results",
    "Circuit History": "circuits/{circuit_id}/results/1",
    "Head to Head": "current/last/results"
}

# Endpoint selection
selected_endpoint = st.sidebar.selectbox(
    "Select Endpoint",
    list(ENDPOINTS.keys())
)

# Parameters section in sidebar
st.sidebar.subheader("Parameters")

params = {}
if selected_endpoint == "Driver Season Results":
    params["year"] = st.sidebar.text_input("Year", "2023")
    params["driver_id"] = st.sidebar.text_input("Driver ID", "max_verstappen")
elif selected_endpoint == "Circuit History":
    params["circuit_id"] = st.sidebar.text_input("Circuit ID", "monaco")

# Function to fetch data
async def fetch_data(endpoint: str) -> Dict[str, Any]:
    """Fetch data from the Ergast API."""
    # Format endpoint with parameters if needed
    formatted_endpoint = endpoint
    if params:
        for key, value in params.items():
            formatted_endpoint = formatted_endpoint.replace(f"{{{key}}}", value)
    
    url = f"{BASE_URL}/{formatted_endpoint}.json"
    
    # Show the complete URL
    st.code(f"GET {url}", language="http")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            st.error(f"HTTP Error: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None

# Function to process and display data
def display_data(data: Dict[str, Any], endpoint_name: str):
    if not data:
        return

    # Extract relevant data based on endpoint
    if "MRData" in data:
        if "RaceTable" in data["MRData"]:
            if "Races" in data["MRData"]["RaceTable"]:
                races = data["MRData"]["RaceTable"]["Races"]
                if races:
                    if endpoint_name == "Current Season Schedule":
                        df = pd.json_normalize(races)
                        st.dataframe(df)
                        
                        # Display first race details
                        st.subheader("First Race Details")
                        st.json(races[0])
                    
                    elif "Results" in races[0]:
                        results = races[0]["Results"]
                        df = pd.json_normalize(results)
                        st.dataframe(df)
                        
                        # Display winner details
                        st.subheader("Winner Details")
                        st.json(results[0])
                    
                    elif "QualifyingResults" in races[0]:
                        quali = races[0]["QualifyingResults"]
                        df = pd.json_normalize(quali)
                        st.dataframe(df)
                        
                        # Display pole position details
                        st.subheader("Pole Position Details")
                        st.json(quali[0])
        
        elif "StandingsTable" in data["MRData"]:
            if "StandingsLists" in data["MRData"]["StandingsTable"]:
                standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]
                if "DriverStandings" in standings:
                    df = pd.json_normalize(standings["DriverStandings"])
                    st.dataframe(df)
                    
                    # Display top driver details
                    st.subheader("Top Driver Details")
                    st.json(standings["DriverStandings"][0])
                
                elif "ConstructorStandings" in standings:
                    df = pd.json_normalize(standings["ConstructorStandings"])
                    st.dataframe(df)
                    
                    # Display top constructor details
                    st.subheader("Top Constructor Details")
                    st.json(standings["ConstructorStandings"][0])

    # Display raw JSON response
    st.subheader("Raw JSON Response")
    st.json(data)

# Main app logic
if st.sidebar.button("Fetch Data"):
    endpoint = ENDPOINTS[selected_endpoint]
    
    # Create a spinner while fetching data
    with st.spinner("Fetching data..."):
        # Run async function
        data = asyncio.run(fetch_data(endpoint))
        
        if data:
            st.success("Data fetched successfully!")
            
            # Display response headers
            st.subheader("Response Information")
            st.info(f"Endpoint: {endpoint}\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Process and display the data
            display_data(data, selected_endpoint) 