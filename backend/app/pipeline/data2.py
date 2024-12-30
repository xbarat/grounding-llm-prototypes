from typing import Dict, Any, Optional
import httpx
import asyncio
import traceback
from dataclasses import dataclass
import pandas as pd
from functools import lru_cache
from app.query.processor import DataRequirements

@dataclass
class DataResponse:
    """Response from the data pipeline"""
    success: bool
    data: Optional[Dict[str, pd.DataFrame]] = None
    error: Optional[str] = None

class DataTransformer:
    """Transforms raw data into the required format for analysis"""

    def normalize_driver_performance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize driver performance data"""
        try:
            # Convert numeric columns
            numeric_columns = ['position', 'points', 'laps', 'grid']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Create driver name column
            if 'Driver.givenName' in df.columns and 'Driver.familyName' in df.columns:
                df['driver'] = df['Driver.givenName'] + ' ' + df['Driver.familyName']
            
            # Create race column
            if 'raceName' in df.columns:
                df['race'] = df['raceName']
            
            # Select and rename columns
            columns = {
                'race': 'race',
                'season': 'season',
                'round': 'round',
                'driver': 'driver',
                'position': 'position',
                'points': 'points',
                'laps': 'laps',
                'grid': 'grid',
                'status': 'status',
                'fastestLap': 'fastest_lap',
                'Constructor.name': 'constructor',
                'Circuit.name': 'circuit'
            }
            
            df = df[[col for col in columns.keys() if col in df.columns]]
            df = df.rename(columns=columns)
            
            return df
            
        except Exception as e:
            print(f"Error normalizing driver performance data: {str(e)}")
            return pd.DataFrame()

    def normalize_qualifying(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize qualifying data"""
        try:
            print("\nQualifying Data Debug:")
            print(f"Input DataFrame columns: {df.columns.tolist()}")
            print(f"Input DataFrame shape: {df.shape}")
            
            # Convert position to numeric
            if 'position' in df.columns:
                df['position'] = pd.to_numeric(df['position'], errors='coerce')
            
            # Create driver name column
            if 'Driver.givenName' in df.columns and 'Driver.familyName' in df.columns:
                df['driver'] = df['Driver.givenName'] + ' ' + df['Driver.familyName']
                print(f"Unique drivers: {df['driver'].unique().tolist()}")
            
            # Create race column
            if 'raceName' in df.columns:
                df['race'] = df['raceName']
                print(f"Unique races: {df['race'].unique().tolist()}")
            
            # Convert qualifying times to timedelta
            for col in ['Q1', 'Q2', 'Q3']:
                if col in df.columns:
                    # Convert empty strings to NaN
                    df[col] = df[col].replace('', pd.NA)
                    
                    # Convert times to seconds
                    def to_seconds(time_str):
                        if pd.isna(time_str):
                            return pd.NA
                        try:
                            minutes, seconds = time_str.split(':')
                            return float(minutes) * 60 + float(seconds)
                        except:
                            try:
                                return float(time_str)
                            except:
                                return pd.NA
                    
                    df[f'{col}_seconds'] = df[col].apply(to_seconds)
            
            # Select and rename columns
            columns = {
                'race': 'race',
                'season': 'season',
                'round': 'round',
                'driver': 'driver',
                'position': 'position',
                'Q1': 'Q1',
                'Q2': 'Q2',
                'Q3': 'Q3',
                'Q1_seconds': 'Q1_seconds',
                'Q2_seconds': 'Q2_seconds',
                'Q3_seconds': 'Q3_seconds',
                'Constructor.name': 'constructor',
                'Circuit.name': 'circuit'
            }
            
            available_cols = [col for col in columns.keys() if col in df.columns]
            print(f"Available columns for selection: {available_cols}")
            
            df = df[available_cols]
            df = df.rename(columns=columns)
            
            print(f"Output DataFrame shape: {df.shape}")
            print(f"Output DataFrame columns: {df.columns.tolist()}")
            
            return df
            
        except Exception as e:
            print(f"Error normalizing qualifying data: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return pd.DataFrame()

    def normalize_lap_times(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize lap time data"""
        try:
            # Convert numeric columns
            numeric_columns = ['lap', 'avgSpeed']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Create driver name column
            if 'Driver.givenName' in df.columns and 'Driver.familyName' in df.columns:
                df['driver'] = df['Driver.givenName'] + ' ' + df['Driver.familyName']
            
            # Create race column
            if 'raceName' in df.columns:
                df['race'] = df['raceName']
            
            # Convert lap times to seconds
            if 'time' in df.columns:
                def to_seconds(time_str):
                    if pd.isna(time_str):
                        return pd.NA
                    try:
                        minutes, seconds = time_str.split(':')
                        return float(minutes) * 60 + float(seconds)
                    except:
                        try:
                            return float(time_str)
                        except:
                            return pd.NA
                
                df['time_seconds'] = df['time'].apply(to_seconds)
            
            # Select and rename columns
            columns = {
                'race': 'race',
                'season': 'season',
                'round': 'round',
                'driver': 'driver',
                'lap': 'lap',
                'time': 'time',
                'time_seconds': 'time_seconds',
                'avgSpeed': 'avg_speed',
                'Constructor.name': 'constructor',
                'Circuit.name': 'circuit'
            }
            
            df = df[[col for col in columns.keys() if col in df.columns]]
            df = df.rename(columns=columns)
            
            return df
            
        except Exception as e:
            print(f"Error normalizing lap time data: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def filter_season(df: pd.DataFrame, season: str) -> pd.DataFrame:
        """Filter data for a specific season"""
        return df[df['season'] == str(season)]

    @staticmethod
    def calculate_driver_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate key statistics for a driver"""
        try:
            stats = {
                'wins': len(df[df['position'] == 1]),
                'podiums': len(df[df['position'] <= 3]),
                'points': df['points'].sum(),
                'avg_position': df['position'].mean(),
                'races': len(df),
                'dnfs': len(df[df['position'].isna()])
            }
            return stats
        except Exception as e:
            print(f"Error calculating stats: {str(e)}")
            return {}

class DataPipeline:
    """Handles data fetching and processing for F1 data"""

    def __init__(self, base_url: str = "http://ergast.com/api/f1", client: Optional[httpx.AsyncClient] = None):
        self.base_url = base_url.rstrip('/')
        self.client = client
        self.endpoint_templates = {
            "/api/f1/races": "{base_url}/{season}/results.json",
            "/api/f1/qualifying": "{base_url}/{season}/qualifying.json",
            "/api/f1/drivers": "{base_url}/{season}/drivers/{driver}/results.json",
            "/api/f1/constructors": "{base_url}/{season}/constructors/{constructor}/results.json",
            "/api/f1/laps": "{base_url}/{season}/{round}/laps.json",
            "/api/f1/pitstops": "{base_url}/{season}/{round}/pitstops.json",
            "/api/f1/status": "{base_url}/{season}/status.json",
            "/api/f1/circuits": "{base_url}/{season}/circuits.json",
            "/api/f1/standings/drivers": "{base_url}/{season}/{round}/driverStandings.json",
            "/api/f1/standings/constructors": "{base_url}/{season}/{round}/constructorStandings.json"
        }
        
        # Driver ID mapping
        self.driver_ids = {
            "lewis_hamilton": "hamilton",
            "max_verstappen": "max_verstappen",
            "charles_leclerc": "leclerc",
            "sergio_perez": "perez",
            "carlos_sainz": "sainz",
            "george_russell": "russell",
            "lando_norris": "norris",
            "fernando_alonso": "alonso",
            "oscar_piastri": "piastri",
            "valtteri_bottas": "bottas"
        }
        
        # Circuit ID and name mapping
        self.circuit_mappings = {
            "monaco": ["monaco", "monte carlo", "monte-carlo"],
            "monza": ["monza", "autodromo nazionale monza", "italian grand prix"],
            "silverstone": ["silverstone", "british grand prix"],
            "spa": ["spa", "spa-francorchamps", "belgian grand prix"],
            "suzuka": ["suzuka", "japanese grand prix"],
            "melbourne": ["melbourne", "albert park", "australian grand prix"],
            "barcelona": ["barcelona", "catalunya", "spanish grand prix"],
            "singapore": ["singapore", "marina bay"]
        }

    def _validate_response_data(self, json_data: dict, endpoint: str) -> tuple[bool, Optional[str]]:
        """Validate the JSON response data structure"""
        if not json_data or 'MRData' not in json_data:
            return False, "Missing MRData in response"
            
        mrdata = json_data['MRData']
        table_key = next((k for k in mrdata.keys() if k.endswith('Table')), None)
        
        if not table_key or table_key not in mrdata:
            return False, f"Missing table data in response. Available keys: {list(mrdata.keys())}"
            
        table_data = mrdata[table_key]
        if not isinstance(table_data, dict):
            return False, f"Invalid table data type: {type(table_data)}"
            
        races = table_data.get('Races', [])
        if not races:
            return False, "No race data found"
            
        return True, None

    def _normalize_circuit_name(self, circuit: str) -> str:
        """Normalize circuit name for consistent matching"""
        if not circuit:
            return ""
            
        circuit = circuit.lower().strip()
        for circuit_id, variants in self.circuit_mappings.items():
            if circuit in variants or any(variant in circuit for variant in variants):
                return circuit_id
        return circuit

    def _normalize_param(self, param, default="current"):
        """Normalize parameter values"""
        if isinstance(param, list):
            return param[0] if param else default
        return param if param is not None and param != "" else default

    def _build_url(self, requirements: DataRequirements) -> str:
        """Build URL dynamically using endpoint templates"""
        template = self.endpoint_templates.get(requirements.endpoint)
        if not template:
            raise ValueError(f"Unsupported endpoint: {requirements.endpoint}")
        
        params = {}
        
        # Season handling
        params["season"] = self._normalize_param(requirements.params.get("season"))
        
        # Round handling
        if requirements.endpoint == "/api/f1/qualifying" and requirements.params.get("circuit"):
            # For qualifying with circuit, we need to get all races first
            template = "{base_url}/{season}/qualifying.json"
        else:
            params["round"] = self._normalize_param(requirements.params.get("round"), "last")
        
        # Driver handling
        driver = requirements.params.get("driver")
        if driver:
            params["driver"] = self.driver_ids.get(
                self._normalize_param(driver), 
                self._normalize_param(driver)
            )
        
        # Circuit handling
        circuit = requirements.params.get("circuit")
        if circuit:
            normalized_circuit = self._normalize_circuit_name(self._normalize_param(circuit))
            params["circuit"] = normalized_circuit if normalized_circuit else self._normalize_param(circuit)
        
        # Constructor handling
        constructor = requirements.params.get("constructor")
        if constructor:
            params["constructor"] = self._normalize_param(constructor)
        
        # Build URL with valid parameters
        url = template.format(
            base_url=self.base_url,
            **{k: v for k, v in params.items() if v is not None}
        )
        
        return url

    def _json_to_dataframe(self, json_data: dict, endpoint: str) -> pd.DataFrame:
        """Convert JSON response to DataFrame with proper handling of different endpoints."""
        # Validate response data
        is_valid, error_msg = self._validate_response_data(json_data, endpoint)
        if not is_valid:
            print(f"Invalid response data: {error_msg}")
            return pd.DataFrame()

        mrdata = json_data['MRData']
        table_key = next((k for k in mrdata.keys() if k.endswith('Table')), None)
        table_data = mrdata[table_key]
        
        if not isinstance(table_data, dict):
            print(f"Table data is not a dictionary: {type(table_data)}")
            return pd.DataFrame()

        races = []
        if endpoint == '/api/f1/qualifying':
            races_data = table_data.get('Races', [])
            for race in races_data:
                qualifying_results = race.get('QualifyingResults', [])
                circuit = race.get('Circuit', {})
                for result in qualifying_results:
                    driver = result.get('Driver', {})
                    constructor = result.get('Constructor', {})
                    races.append({
                        'raceName': race.get('raceName', ''),
                        'season': race.get('season', ''),
                        'round': race.get('round', ''),
                        'Driver.givenName': driver.get('givenName', ''),
                        'Driver.familyName': driver.get('familyName', ''),
                        'position': result.get('position', ''),
                        'Q1': result.get('Q1', ''),
                        'Q2': result.get('Q2', ''),
                        'Q3': result.get('Q3', ''),
                        'Constructor.name': constructor.get('name', ''),
                        'Circuit.name': circuit.get('circuitName', '')
                    })
        elif endpoint == '/api/f1/laps':
            races_data = table_data.get('Races', [])
            for race in races_data:
                laps = race.get('Laps', [])
                for lap in laps:
                    for timing in lap.get('Timings', []):
                        races.append({
                            'raceName': race.get('raceName', ''),
                            'season': race.get('season', ''),
                            'round': race.get('round', ''),
                            'Driver.givenName': timing.get('driverId', ''),
                            'lap': lap.get('number', ''),
                            'time': timing.get('time', ''),
                            'avgSpeed': timing.get('avgSpeed', {}).get('speed', 0),
                            'Circuit.name': race.get('Circuit', {}).get('circuitName', '')
                        })
        else:
            races_data = table_data.get('Races', [])
            for race in races_data:
                results = race.get('Results', [])
                for result in results:
                    driver = result.get('Driver', {})
                    constructor = result.get('Constructor', {})
                    circuit = race.get('Circuit', {})
                    fastest_lap = result.get('FastestLap', {})
                    races.append({
                        'raceName': race.get('raceName', ''),
                        'season': race.get('season', ''),
                        'round': race.get('round', ''),
                        'Driver.givenName': driver.get('givenName', ''),
                        'Driver.familyName': driver.get('familyName', ''),
                        'position': result.get('position', ''),
                        'points': float(result.get('points', 0)),
                        'laps': result.get('laps', ''),
                        'grid': result.get('grid', ''),
                        'status': result.get('status', ''),
                        'fastestLap': fastest_lap.get('Time', {}).get('time', ''),
                        'Constructor.name': constructor.get('name', ''),
                        'Circuit.name': circuit.get('circuitName', '')
                    })

        df = pd.DataFrame(races)
        if df.empty:
            print(f"No data found for endpoint {endpoint}")
        return df

    async def _fetch_with_retry(self, client: httpx.AsyncClient, url: str, max_retries: int = 3) -> Optional[dict]:
        """Fetch data with retry logic"""
        for attempt in range(max_retries):
            try:
                print(f"\nAttempt {attempt + 1} for {url}")
                response = await client.get(url, timeout=30.0, follow_redirects=True)
                print(f"Status: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print("Successfully parsed JSON response")
                        return data
                    except Exception as e:
                        print(f"Error parsing JSON: {str(e)}")
                        print(f"Response text: {response.text[:200]}...")
                elif response.status_code == 429:  # Rate limit
                    print("Rate limited, backing off...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    print(f"Request failed with status {response.status_code}")
                    print(f"Response text: {response.text[:200]}...")
                    return None
            except Exception as e:
                print(f"Request error: {str(e)}")
                if attempt < max_retries - 1:
                    print("Retrying...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
        return None

    @lru_cache(maxsize=128)
    async def _fetch_with_cache(self, client: httpx.AsyncClient, url: str) -> Optional[dict]:
        return await self._fetch_with_retry(client, url)

    def _time_to_seconds(self, time_str: str) -> Optional[float]:
        """Convert time string to seconds."""
        if not time_str:
            return None
        try:
            # Handle different time formats (MM:SS.sss or H:MM:SS.sss)
            parts = time_str.split(':')
            if len(parts) == 2:  # MM:SS.sss
                minutes, seconds = parts
                return float(minutes) * 60 + float(seconds)
            elif len(parts) == 3:  # H:MM:SS.sss
                hours, minutes, seconds = parts
                return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
            return None
        except (ValueError, IndexError):
            return None

    def _validate_dataframe_columns(self, df: pd.DataFrame, endpoint: str) -> tuple[bool, Optional[str]]:
        """Validate DataFrame columns based on endpoint requirements"""
        if df.empty:
            return True, None  # Empty DataFrame validation is handled elsewhere
            
        required_columns = {
            "/api/f1/qualifying": ["race", "season", "driver", "position"],
            "/api/f1/drivers": ["race", "season", "driver", "position", "points"],
            "/api/f1/laps": ["race", "season", "driver", "lap", "time"],
            "/api/f1/constructors": ["race", "season", "constructor", "points"]
        }
        
        if endpoint not in required_columns:
            return True, None  # No specific requirements for this endpoint
            
        missing = [col for col in required_columns[endpoint] if col not in df.columns]
        if missing:
            return False, f"Missing required columns: {missing}"
            
        return True, None

    async def _retry_empty_results(self, url: str, endpoint: str, client: httpx.AsyncClient, max_retries: int = 2) -> pd.DataFrame:
        """Retry fetching and processing data for empty results"""
        for attempt in range(max_retries):
            try:
                result = await self._fetch_with_retry(client, url)
                if result:
                    df = self._json_to_dataframe(result, endpoint)
                    if not df.empty:
                        # Validate DataFrame columns
                        is_valid, error_msg = self._validate_dataframe_columns(df, endpoint)
                        if is_valid:
                            return df
                        print(f"DataFrame validation failed: {error_msg}")
                await asyncio.sleep(1)  # Wait before retry
            except Exception as e:
                print(f"Retry attempt {attempt + 1} failed: {str(e)}")
        return pd.DataFrame()

    async def _process_requests(self, requirements: DataRequirements, seasons: list, drivers: list, client: httpx.AsyncClient, all_dataframes: list):
        """Helper method to process all requests for given seasons and drivers"""
        urls = []
        for season in seasons:
            for driver in drivers:
                single_req = DataRequirements(
                    endpoint=requirements.endpoint,
                    params={**requirements.params, "season": season, "driver": driver}
                )
                url = self._build_url(single_req)
                print(f"\nProcessing request for {driver} in {season}")
                print(f"URL: {url}")
                urls.append(url)

        # Process URLs sequentially to avoid overwhelming the API
        for url in urls:
            result = await self._fetch_with_retry(client, url)
            if result:
                df = self._json_to_dataframe(result, requirements.endpoint)
                if df.empty:
                    print(f"Initial response empty, retrying for {url}")
                    df = await self._retry_empty_results(url, requirements.endpoint, client)
                
                if not df.empty:
                    all_dataframes.append(df)
                    print(f"Successfully processed data from {url}")
                else:
                    print(f"No data in response from {url}")

    async def process(self, requirements: DataRequirements) -> DataResponse:
        """Process data requirements and fetch data from the F1 API"""
        try:
            all_dataframes = []

            # Handle multiple seasons and drivers
            seasons = requirements.params.get("season", [])
            if not isinstance(seasons, list):
                seasons = [seasons]
            if not seasons or all(not s for s in seasons):
                seasons = ["current"]

            drivers = requirements.params.get("driver", [])
            if not isinstance(drivers, list):
                drivers = [drivers]

            # Create all combinations of seasons and drivers
            if self.client is None:
                timeout = httpx.Timeout(30.0)
                async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                    await self._process_requests(requirements, seasons, drivers, client, all_dataframes)
            else:
                await self._process_requests(requirements, seasons, drivers, self.client, all_dataframes)

            if not all_dataframes:
                return DataResponse(success=False, error="No data retrieved from any request")

            # Combine all DataFrames
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            
            # Normalize the data based on endpoint
            if requirements.endpoint == "/api/f1/qualifying":
                transformer = DataTransformer()
                normalized_df = transformer.normalize_qualifying(combined_df)
                
                # Filter by circuit if specified
                if requirements.params.get("circuit"):
                    circuit = requirements.params["circuit"]
                    normalized_circuit = self._normalize_circuit_name(circuit)
                    if 'circuit' in normalized_df.columns:
                        normalized_df = normalized_df[
                            normalized_df['circuit'].str.contains(
                                normalized_circuit if normalized_circuit else circuit, 
                                case=False, 
                                na=False
                            )
                        ]
                
                # Filter by driver if specified
                if requirements.params.get("driver"):
                    driver = requirements.params["driver"]
                    if 'driver' in normalized_df.columns:
                        normalized_df = normalized_df[
                            normalized_df['driver'].str.contains(
                                driver.replace('_', ' '), 
                                case=False, 
                                na=False
                            )
                        ]
            elif requirements.endpoint == "/api/f1/laps":
                transformer = DataTransformer()
                normalized_df = transformer.normalize_lap_times(combined_df)
            else:
                transformer = DataTransformer()
                normalized_df = transformer.normalize_driver_performance(combined_df)
            
            # Validate DataFrame after normalization
            is_valid, error_msg = self._validate_dataframe_columns(normalized_df, requirements.endpoint)
            if not is_valid:
                return DataResponse(success=False, error=error_msg)
            
            # Filter by circuit for non-qualifying endpoints
            if requirements.endpoint != "/api/f1/qualifying" and requirements.params.get("circuit"):
                circuit = requirements.params["circuit"]
                if 'circuit' in normalized_df.columns:
                    normalized_df = normalized_df[normalized_df['circuit'].str.contains(circuit, case=False, na=False)]
            
            return DataResponse(
                success=True,
                data={"results": normalized_df}
            )

        except Exception as e:
            print(f"\nError details: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return DataResponse(
                success=False,
                error=f"Error processing data: {str(e)}"
            )

# Example usage
async def main():
    pipeline = DataPipeline()
    requirements = DataRequirements(
        endpoint="/api/f1/drivers",
        params={
            "season": ["2019", "2020", "2021", "2022", "2023"],
            "driver": ["lewis_hamilton", "charles_leclerc"]
        }
    )
    response = await pipeline.process(requirements)
    if response.success and response.data is not None:
        df = response.data["results"]
        print("\nFirst few rows of normalized data:")
        print(df.head())
        
        print("\nDriver Statistics:")
        for driver in df['driver'].unique():
            driver_df = df[df['driver'] == driver]
            stats = DataTransformer.calculate_driver_stats(driver_df)
            print(f"\n{driver}:")
            for stat, value in stats.items():
                print(f"  {stat}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
