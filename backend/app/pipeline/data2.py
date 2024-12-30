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
    """Handles data preprocessing and normalization for analytics"""

    @staticmethod
    def normalize_driver_performance(df: pd.DataFrame) -> pd.DataFrame:
        """Normalize driver performance data for analysis"""
        try:
            # Extract and rename key performance metrics
            normalized = df[[
                'raceName', 'season', 'round',
                'Results.Driver.familyName', 'Results.position',
                'Results.points', 'Results.laps'
            ]].copy()
            
            # Rename columns for clarity
            normalized.columns = [
                'race', 'season', 'round',
                'driver', 'position', 'points', 'laps'
            ]
            
            # Convert numeric columns
            normalized['position'] = pd.to_numeric(normalized['position'], errors='coerce')
            normalized['points'] = pd.to_numeric(normalized['points'], errors='coerce')
            normalized['laps'] = pd.to_numeric(normalized['laps'], errors='coerce')
            
            return normalized
        except Exception as e:
            print(f"Error normalizing data: {str(e)}")
            return df

    @staticmethod
    def normalize_qualifying(df: pd.DataFrame) -> pd.DataFrame:
        """Normalize qualifying data for analysis"""
        try:
            # Extract and rename key qualifying metrics
            normalized = df[[
                'raceName', 'Circuit.name', 'position',
                'Driver.familyName', 'Constructor.name',
                'Q1', 'Q2', 'Q3'
            ]].copy()
            
            # Rename columns for clarity
            normalized.columns = [
                'race', 'circuit', 'position',
                'driver', 'constructor',
                'Q1', 'Q2', 'Q3'
            ]
            
            # Convert position to numeric
            normalized['position'] = pd.to_numeric(normalized['position'], errors='coerce')
            
            # Convert qualifying times to timedelta
            for col in ['Q1', 'Q2', 'Q3']:
                # Convert empty strings to NaN
                normalized[col] = normalized[col].replace('', pd.NA)
                
                # Convert times to seconds
                def to_seconds(time_str):
                    if pd.isna(time_str):
                        return pd.NA
                    try:
                        minutes, seconds = time_str.split(':')
                        return float(minutes) * 60 + float(seconds)
                    except:
                        return pd.NA
                
                normalized[f'{col}_seconds'] = normalized[col].apply(to_seconds)
            
            return normalized
        except Exception as e:
            print(f"Error normalizing qualifying data: {str(e)}")
            return df

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
            "/api/f1/qualifying": "{base_url}/{season}/circuits/{circuit}/qualifying.json",
            "/api/f1/drivers": "{base_url}/{season}/drivers/{driver}/results.json",
            "/api/f1/constructors": "{base_url}/{season}/constructors/{constructor}/results.json"
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
            "fernando_alonso": "alonso"
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

    def _build_url(self, requirements: DataRequirements) -> str:
        """Build URL dynamically using endpoint templates"""
        template = self.endpoint_templates.get(requirements.endpoint)
        if not template:
            raise ValueError(f"Unsupported endpoint: {requirements.endpoint}")
            
        # Get driver ID if present
        driver = requirements.params.get("driver", "")
        if driver:
            driver = self.driver_ids.get(driver, driver)
            
        # Get circuit ID if present
        circuit = requirements.params.get("circuit", "")
        if circuit:
            circuit = self.circuit_ids.get(circuit, circuit)

        url = template.format(
            base_url=self.base_url,
            season=requirements.params.get("season", ""),
            round=requirements.params.get("round", ""),
            driver=driver,
            circuit=circuit,
            constructor=requirements.params.get("constructor", "")
        )
        return url

    def _json_to_dataframe(self, json_data: dict, endpoint: str) -> pd.DataFrame:
        """Convert JSON response to Pandas DataFrame based on the endpoint"""
        try:
            if endpoint == "/api/f1/drivers":
                # Extract races from the response
                races = json_data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
                if not races:
                    print("No races found in response")
                    print("Response structure:", json_data.keys())
                    return pd.DataFrame()
                
                # Flatten the nested race results
                flattened_data = []
                for race in races:
                    race_info = {
                        'season': race.get('season'),
                        'round': race.get('round'),
                        'raceName': race.get('raceName'),
                        'Circuit.name': race.get('Circuit', {}).get('circuitName'),
                        'Circuit.location': race.get('Circuit', {}).get('Location', {}).get('locality')
                    }
                    
                    # Get the result (should be only one per race)
                    results = race.get('Results', [])
                    if results:
                        result = results[0]  # Take the first result
                        race_info.update({
                            'Results.position': result.get('position'),
                            'Results.points': result.get('points'),
                            'Results.status': result.get('status'),
                            'Results.laps': result.get('laps'),
                            'Results.grid': result.get('grid'),
                            'Results.Driver.familyName': result.get('Driver', {}).get('familyName'),
                            'Results.Driver.givenName': result.get('Driver', {}).get('givenName'),
                            'Results.Constructor.name': result.get('Constructor', {}).get('name')
                        })
                        flattened_data.append(race_info)
                
                if not flattened_data:
                    print("No results found in races")
                    return pd.DataFrame()
                
                return pd.DataFrame(flattened_data)
            
            elif endpoint == "/api/f1/races":
                races = json_data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
                return pd.json_normalize(races)
            
            elif endpoint == "/api/f1/qualifying":
                races = json_data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
                if not races:
                    print("No qualifying data found")
                    print("Response structure:", json_data.keys())
                    return pd.DataFrame()
                
                qualifying_data = []
                for race in races:
                    race_info = {
                        'season': race.get('season'),
                        'round': race.get('round'),
                        'raceName': race.get('raceName'),
                        'Circuit.name': race.get('Circuit', {}).get('circuitName'),
                        'Circuit.location': race.get('Circuit', {}).get('Location', {}).get('locality')
                    }
                    
                    for quali in race.get('QualifyingResults', []):
                        quali_info = race_info.copy()
                        quali_info.update({
                            'position': quali.get('position'),
                            'Driver.number': quali.get('number'),
                            'Driver.code': quali.get('Driver', {}).get('code'),
                            'Driver.givenName': quali.get('Driver', {}).get('givenName'),
                            'Driver.familyName': quali.get('Driver', {}).get('familyName'),
                            'Constructor.name': quali.get('Constructor', {}).get('name'),
                            'Q1': quali.get('Q1', ''),
                            'Q2': quali.get('Q2', ''),
                            'Q3': quali.get('Q3', '')
                        })
                        qualifying_data.append(quali_info)
                
                if not qualifying_data:
                    print("No qualifying results found")
                    return pd.DataFrame()
                
                df = pd.DataFrame(qualifying_data)
                
                # Convert position to numeric
                df['position'] = pd.to_numeric(df['position'], errors='coerce')
                
                # Filter by driver if specified in the URL
                driver_filter = None
                if 'driver' in json_data.get('MRData', {}).get('RaceTable', {}).get('driverId', ''):
                    driver_filter = json_data['MRData']['RaceTable']['driverId']
                
                if driver_filter:
                    df = df[df['Driver.code'].str.lower() == driver_filter.lower()]
                
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Error converting JSON to DataFrame: {str(e)}")
            print("JSON data structure:", json_data.keys())
            return pd.DataFrame()

    @lru_cache(maxsize=128)
    async def _fetch_with_cache(self, client: httpx.AsyncClient, url: str) -> Optional[dict]:
        return await self._fetch_with_retry(client, url)

    async def process(self, requirements: DataRequirements) -> DataResponse:
        """
        Process data requirements and fetch data from the F1 API.
        Handles multiple drivers and seasons by making parallel requests.
        """
        try:
            all_dataframes = []

            # Handle multiple seasons and drivers
            seasons = requirements.params.get("season", [])
            if not isinstance(seasons, list):
                seasons = [seasons]

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
            
            # Normalize the data
            transformer = DataTransformer()
            normalized_df = transformer.normalize_driver_performance(combined_df)
            
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
