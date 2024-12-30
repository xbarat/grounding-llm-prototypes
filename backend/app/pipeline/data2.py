from typing import Dict, Any, Optional
import httpx
import asyncio
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
            # Convert position to numeric
            if 'position' in df.columns:
                df['position'] = pd.to_numeric(df['position'], errors='coerce')
            
            # Create driver name column
            if 'Driver.givenName' in df.columns and 'Driver.familyName' in df.columns:
                df['driver'] = df['Driver.givenName'] + ' ' + df['Driver.familyName']
            
            # Create race column
            if 'raceName' in df.columns:
                df['race'] = df['raceName']
            
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
            
            df = df[[col for col in columns.keys() if col in df.columns]]
            df = df.rename(columns=columns)
            
            return df
            
        except Exception as e:
            print(f"Error normalizing qualifying data: {str(e)}")
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
        
        # Circuit ID mapping
        self.circuit_ids = {
            "monaco": "monaco",
            "monza": "monza",
            "silverstone": "silverstone",
            "spa": "spa",
            "suzuka": "suzuka",
            "melbourne": "albert_park",
            "barcelona": "catalunya",
            "singapore": "marina_bay"
        }

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
            params["circuit"] = self.circuit_ids.get(
                self._normalize_param(circuit), 
                self._normalize_param(circuit)
            )
        
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
        """Convert JSON response to Pandas DataFrame based on the endpoint"""
        try:
            table_mapping = {
                "/api/f1/drivers": ("RaceTable", "Races"),
                "/api/f1/qualifying": ("RaceTable", "Races"),
                "/api/f1/races": ("RaceTable", "Races"),
                "/api/f1/constructors": ("ConstructorTable", "Constructors"),
                "/api/f1/circuits": ("CircuitTable", "Circuits"),
                "/api/f1/laps": ("RaceTable", "Races"),
                "/api/f1/pitstops": ("RaceTable", "Races"),
                "/api/f1/status": ("StatusTable", "Status"),
                "/api/f1/standings/drivers": ("StandingsTable", "StandingsLists"),
                "/api/f1/standings/constructors": ("StandingsTable", "StandingsLists")
            }
            
            if endpoint not in table_mapping:
                raise ValueError(f"Unsupported endpoint for DataFrame conversion: {endpoint}")
                
            table_key, data_key = table_mapping[endpoint]
            data = json_data.get('MRData', {}).get(table_key, {}).get(data_key, [])
            
            if not data:
                print(f"No data found for endpoint {endpoint}")
                print("Response structure:", json_data.get('MRData', {}).keys())
                return pd.DataFrame()
            
            # Extract races from the response for race-related endpoints
            if endpoint in ["/api/f1/drivers", "/api/f1/qualifying", "/api/f1/races", "/api/f1/laps", "/api/f1/pitstops"]:
                flattened_data = []
                for race in data:
                    race_info = {
                        'season': race.get('season'),
                        'round': race.get('round'),
                        'raceName': race.get('raceName'),
                        'Circuit.name': race.get('Circuit', {}).get('circuitName'),
                        'Circuit.location': race.get('Circuit', {}).get('Location', {}).get('locality')
                    }
                    
                    # Handle different result types
                    results_key = 'Results'
                    if endpoint == "/api/f1/qualifying":
                        results_key = 'QualifyingResults'
                    elif endpoint == "/api/f1/laps":
                        results_key = 'Laps'
                    elif endpoint == "/api/f1/pitstops":
                        results_key = 'PitStops'
                    
                    results = race.get(results_key, [])
                    if results:
                        for result in results:
                            result_info = race_info.copy()
                            
                            # Common fields for all result types
                            result_info.update({
                                'position': result.get('position'),
                                'Driver.familyName': result.get('Driver', {}).get('familyName'),
                                'Driver.givenName': result.get('Driver', {}).get('givenName'),
                                'Constructor.name': result.get('Constructor', {}).get('name')
                            })
                            
                            # Add result type specific fields
                            if endpoint == "/api/f1/qualifying":
                                result_info.update({
                                    'Q1': result.get('Q1', ''),
                                    'Q2': result.get('Q2', ''),
                                    'Q3': result.get('Q3', '')
                                })
                            elif endpoint == "/api/f1/laps":
                                result_info.update({
                                    'lap': result.get('number'),
                                    'time': result.get('time'),
                                    'avgSpeed': result.get('avgSpeed', {}).get('speed')
                                })
                            else:  # Regular race results
                                result_info.update({
                                    'points': result.get('points'),
                                    'status': result.get('status'),
                                    'laps': result.get('laps'),
                                    'grid': result.get('grid'),
                                    'fastestLap': result.get('FastestLap', {}).get('Time', {}).get('time')
                                })
                            
                            flattened_data.append(result_info)
                
                if not flattened_data:
                    print(f"No {results_key} found in races")
                    return pd.DataFrame()
                
                df = pd.DataFrame(flattened_data)
                
                # Convert position to numeric
                df['position'] = pd.to_numeric(df['position'], errors='coerce')
                
                return df
            
            # For non-race endpoints, directly normalize the data
            return pd.json_normalize(data)
            
        except Exception as e:
            print(f"Error converting JSON to DataFrame: {str(e)}")
            print("JSON data structure:", json_data.get('MRData', {}).keys())
            return pd.DataFrame()

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
            elif requirements.endpoint == "/api/f1/laps":
                transformer = DataTransformer()
                normalized_df = transformer.normalize_lap_times(combined_df)
            else:
                transformer = DataTransformer()
                normalized_df = transformer.normalize_driver_performance(combined_df)
            
            # Filter by circuit if specified
            if requirements.params.get("circuit"):
                circuit = requirements.params["circuit"]
                normalized_df = normalized_df[normalized_df['Circuit.name'].str.contains(circuit, case=False, na=False)]
            
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
                if not df.empty:
                        all_dataframes.append(df)
                    print(f"Successfully processed data from {url}")
                else:
                    print(f"No data in response from {url}")

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
