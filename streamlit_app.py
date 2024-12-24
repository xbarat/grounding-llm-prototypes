import streamlit as st
import httpx
import pandas as pd
from datetime import datetime
import asyncio
from typing import Dict, Any, Optional

# Constants
BASE_URL = "http://ergast.com/api/f1"

# Configure page
st.set_page_config(
    page_title="F1 Driver Performance Explorer",
    page_icon="🏎️",
    layout="wide"
)

# Title and description
st.title("🏎️ F1 Driver Performance Analysis")
st.markdown("""
This app allows you to explore Formula 1 driver performance data.
Select a driver and analyze their performance across different metrics.
""")

# Sidebar for driver selection
st.sidebar.header("Driver Selection")

async def fetch_driver_list() -> Optional[Dict[str, Any]]:
    """Fetch list of current F1 drivers."""
    url = f"{BASE_URL}/current/driverStandings.json"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching driver list: {str(e)}")
            return None

async def fetch_driver_results(driver_id: str, year: str = "current") -> Optional[Dict[str, Any]]:
    """Fetch results for a specific driver."""
    url = f"{BASE_URL}/{year}/drivers/{driver_id}/results.json"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching driver results: {str(e)}")
            return None

def process_driver_results(data: Dict[str, Any]) -> pd.DataFrame:
    """Process driver results into a DataFrame."""
    if not data or "MRData" not in data:
        return pd.DataFrame()

    races = data["MRData"]["RaceTable"]["Races"]
    results = []
    
    for race in races:
        race_result = race["Results"][0]  # Each race has one result for the selected driver
        result = {
            "Race": race["raceName"],
            "Round": int(race["round"]),
            "Grid": int(race_result["grid"]),
            "Position": int(race_result["position"]),
            "Points": float(race_result["points"]),
            "Status": race_result["status"]
        }
        if "Time" in race_result:
            result["FinishTime"] = race_result["Time"].get("time", "")
        if "FastestLap" in race_result:
            result["FastestLap"] = race_result["FastestLap"].get("Time", {}).get("time", "")
            result["FastestLapRank"] = int(race_result["FastestLap"].get("rank", 0))
        
        results.append(result)
    
    return pd.DataFrame(results)

def display_performance_metrics(df: pd.DataFrame):
    """Display key performance metrics."""
    if df.empty:
        st.warning("No data available for the selected driver.")
        return

    # Create three columns for metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Average Finish Position",
            f"P{df['Position'].mean():.1f}",
            f"{df['Grid'].mean() - df['Position'].mean():.1f}"
        )

    with col2:
        st.metric(
            "Total Points",
            f"{df['Points'].sum():.0f}",
            f"Avg: {df['Points'].mean():.1f}"
        )

    with col3:
        podiums = len(df[df['Position'] <= 3])
        st.metric(
            "Podium Finishes",
            f"{podiums}",
            f"{(podiums/len(df))*100:.1f}%"
        )

    # Performance Trends
    st.subheader("Performance Trends")
    
    # Position trend
    st.line_chart(df.set_index('Round')[['Position', 'Grid']])
    
    # Points progression
    st.subheader("Points Progression")
    df['Cumulative Points'] = df['Points'].cumsum()
    st.line_chart(df.set_index('Round')['Cumulative Points'])
    
    # Detailed Results Table
    st.subheader("Race Results")
    st.dataframe(
        df[['Race', 'Grid', 'Position', 'Points', 'Status', 'FastestLap']],
        hide_index=True
    )

# Main app logic
async def main():
    # Fetch current drivers
    drivers_data = await fetch_driver_list()
    
    if drivers_data and "MRData" in drivers_data:
        standings = drivers_data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
        driver_options = {
            f"{d['Driver']['givenName']} {d['Driver']['familyName']}": d['Driver']['driverId']
            for d in standings
        }
        
        selected_name = st.sidebar.selectbox(
            "Select Driver",
            list(driver_options.keys())
        )
        
        selected_driver = driver_options[selected_name]
        
        # Year selection
        year = st.sidebar.selectbox(
            "Select Year",
            ["current", "2023", "2022", "2021", "2020"]
        )
        
        if st.sidebar.button("Analyze Performance"):
            with st.spinner("Fetching driver data..."):
                results = await fetch_driver_results(selected_driver, year)
                if results:
                    df = process_driver_results(results)
                    display_performance_metrics(df)

if __name__ == "__main__":
    asyncio.run(main()) 