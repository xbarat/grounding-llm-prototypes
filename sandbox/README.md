# GIRAFFE Sandbox

A Streamlit-based sandbox for testing and interacting with the GIRAFFE backend.

## Features

- Interactive query interface
- Real-time data visualization
- Platform switching (F1/TypeRacer)
- Query history tracking
- Example queries
- Metric visualization
- Raw data inspection

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the GIRAFFE backend is running on `http://localhost:8000`

3. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

## Usage

1. Select a platform (F1 or TypeRacer) from the sidebar
2. Enter platform-specific information (driver name or username)
3. Either:
   - Type a custom query in the text area
   - Click one of the example queries
4. View results in three tabs:
   - Visualization: Interactive charts
   - Raw Data: DataFrame view
   - Metrics: Key performance indicators

## Example Queries

### F1 Queries
- "Show me Max Verstappen's performance trend in the last 5 races"
- "Compare Hamilton and Verstappen's qualifying performances"
- "Show the points distribution for all drivers this season"

### TypeRacer Queries
- "Show my typing speed trend over the last 100 races"
- "Compare my accuracy and WPM correlation"
- "Show my daily average performance"

## Development

The sandbox is designed to be extensible. Key components:

1. **Data Fetching**: `fetch_data()` and `process_query()` functions handle API communication
2. **Visualization**: `display_visualization()` supports multiple chart types
3. **Metrics**: `display_metrics()` shows key statistics
4. **State Management**: Uses Streamlit's session state for persistence

## Troubleshooting

1. **Backend Connection Issues**
   - Ensure backend is running on port 8000
   - Check CORS settings in backend
   - Verify network connectivity

2. **Visualization Errors**
   - Check data format matches expected schema
   - Verify required columns exist
   - Ensure numeric data types

3. **Query Processing Issues**
   - Validate query syntax
   - Check platform selection
   - Verify required parameters 