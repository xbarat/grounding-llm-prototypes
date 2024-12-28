"""
Data normalization module for standardizing API responses.
Provides functions to transform raw API data into a format matching our database schema.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from .pipeline_validator import validate_pipeline_stage

logger = logging.getLogger(__name__)

class DataNormalizer:
    """
    Handles normalization of data from different platforms into a unified schema.
    """

    @staticmethod
    def normalize_f1_driver(raw_driver: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize driver data from F1 API."""
        normalized = {
            "driver_id": raw_driver.get("driverId"),
            "code": raw_driver.get("code"),
            "number": int(raw_driver.get("permanentNumber", 0)) if raw_driver.get("permanentNumber") else None,
            "given_name": raw_driver.get("givenName"),
            "family_name": raw_driver.get("familyName"),
            "nationality": raw_driver.get("nationality")
        }
        return normalized

    @staticmethod
    def normalize_f1_constructor(raw_constructor: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize constructor/team data from F1 API."""
        normalized = {
            "constructor_id": raw_constructor.get("constructorId"),
            "name": raw_constructor.get("name"),
            "nationality": raw_constructor.get("nationality")
        }
        return normalized

    @staticmethod
    def normalize_f1_circuit(raw_circuit: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize circuit data from F1 API."""
        normalized = {
            "circuit_id": raw_circuit.get("circuitId"),
            "name": raw_circuit.get("circuitName"),
            "location": raw_circuit.get("Location", {}).get("locality"),
            "country": raw_circuit.get("Location", {}).get("country"),
            "lat": float(raw_circuit.get("Location", {}).get("lat", 0)),
            "lng": float(raw_circuit.get("Location", {}).get("long", 0))
        }
        return normalized

    @staticmethod
    def normalize_f1_race(raw_race: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize race data from F1 API."""
        try:
            date_str = f"{raw_race.get('date')} {raw_race.get('time', '00:00:00Z')}"
            race_date = datetime.strptime(date_str.strip("Z"), "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            race_date = None
            logger.warning(f"Failed to parse date for race: {raw_race.get('raceName')}")

        normalized = {
            "race_id": raw_race.get("raceId"),
            "season": int(raw_race.get("season", 0)),
            "round": int(raw_race.get("round", 0)),
            "circuit_id": raw_race.get("Circuit", {}).get("circuitId"),
            "name": raw_race.get("raceName"),
            "date": race_date,
            "time": raw_race.get("time")
        }
        return normalized

    @staticmethod
    def normalize_f1_race_result(raw_result: Dict[str, Any], race_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize race result data from F1 API."""
        fastest_lap = raw_result.get("FastestLap", {})
        normalized = {
            "race_id": race_data.get("race_id"),
            "driver_id": raw_result.get("Driver", {}).get("driverId"),
            "constructor_id": raw_result.get("Constructor", {}).get("constructorId"),
            "grid": int(raw_result.get("grid", 0)),
            "position": int(raw_result.get("position", 0)) if raw_result.get("position") else None,
            "position_text": raw_result.get("positionText"),
            "position_order": int(raw_result.get("positionOrder", 0)),
            "points": float(raw_result.get("points", 0)),
            "laps": int(raw_result.get("laps", 0)),
            "time": raw_result.get("Time", {}).get("time"),
            "milliseconds": int(raw_result.get("Time", {}).get("millis", 0)) if raw_result.get("Time", {}).get("millis") else None,
            "fastest_lap": fastest_lap.get("lap"),
            "fastest_lap_time": fastest_lap.get("Time", {}).get("time"),
            "status": raw_result.get("status")
        }
        return normalized

    @staticmethod
    def normalize_f1_qualifying_result(raw_qualifying: Dict[str, Any], race_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize qualifying result data from F1 API."""
        normalized = {
            "race_id": race_data.get("race_id"),
            "driver_id": raw_qualifying.get("Driver", {}).get("driverId"),
            "constructor_id": raw_qualifying.get("Constructor", {}).get("constructorId"),
            "position": int(raw_qualifying.get("position", 0)),
            "q1": raw_qualifying.get("Q1"),
            "q2": raw_qualifying.get("Q2"),
            "q3": raw_qualifying.get("Q3")
        }
        return normalized

    @staticmethod
    def normalize_f1_driver_standing(raw_standing: Dict[str, Any], race_id: str) -> Dict[str, Any]:
        """Normalize driver standing data from F1 API."""
        normalized = {
            "race_id": race_id,
            "driver_id": raw_standing.get("Driver", {}).get("driverId"),
            "points": float(raw_standing.get("points", 0)),
            "position": int(raw_standing.get("position", 0)),
            "wins": int(raw_standing.get("wins", 0))
        }
        return normalized

    @staticmethod
    def normalize_f1_constructor_standing(raw_standing: Dict[str, Any], race_id: str) -> Dict[str, Any]:
        """Normalize constructor standing data from F1 API."""
        normalized = {
            "race_id": race_id,
            "constructor_id": raw_standing.get("Constructor", {}).get("constructorId"),
            "points": float(raw_standing.get("points", 0)),
            "position": int(raw_standing.get("position", 0)),
            "wins": int(raw_standing.get("wins", 0))
        }
        return normalized

    @classmethod
    def normalize_f1_race_data(cls, raw_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Normalize complete race data including results, qualifying, and standings.
        Returns a dictionary with normalized data for each model type.
        """
        races = raw_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        normalized_data = {
            "races": [],
            "circuits": [],
            "drivers": [],
            "constructors": [],
            "race_results": [],
            "qualifying_results": [],
            "driver_standings": [],
            "constructor_standings": []
        }

        for race in races:
            # Normalize race and circuit data
            circuit_data = cls.normalize_f1_circuit(race.get("Circuit", {}))
            race_data = cls.normalize_f1_race(race)
            normalized_data["circuits"].append(circuit_data)
            normalized_data["races"].append(race_data)

            # Normalize results
            for result in race.get("Results", []):
                normalized_data["drivers"].append(cls.normalize_f1_driver(result.get("Driver", {})))
                normalized_data["constructors"].append(cls.normalize_f1_constructor(result.get("Constructor", {})))
                normalized_data["race_results"].append(cls.normalize_f1_race_result(result, race_data))

            # Normalize qualifying if available
            for qualifying in race.get("QualifyingResults", []):
                normalized_data["qualifying_results"].append(cls.normalize_f1_qualifying_result(qualifying, race_data))

        # Validate normalized data
        if not validate_pipeline_stage('normalization', normalized_data, platform='f1'):
            raise ValueError("Normalized F1 data failed validation")

        return normalized_data

    @staticmethod
    def normalize_typeracer_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize TypeRacer data into our schema."""
        normalized_data = {
            "wpm": float(raw_data.get("wpm", 0)),
            "accuracy": float(raw_data.get("accuracy", 0)),
            "session_id": raw_data.get("session_id"),
            "timestamp": datetime.fromtimestamp(raw_data.get("timestamp", 0)),
            "race_type": raw_data.get("race_type", "practice"),
            "text_length": int(raw_data.get("text_length", 0))
        }

        # Validate normalized data
        if not validate_pipeline_stage('normalization', normalized_data, platform='typeracer'):
            raise ValueError("Normalized TypeRacer data failed validation")

        return normalized_data

    @classmethod
    def normalize_f1_standings_data(cls, raw_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Normalize driver and constructor standings data.
        Returns a dictionary with normalized data for each model type.
        """
        standings_list = raw_data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        if not standings_list:
            return {
                "drivers": [],
                "constructors": [],
                "driver_standings": [],
                "constructor_standings": []
            }

        current_standings = standings_list[0]  # Get the most recent standings
        race_id = f"{current_standings.get('season')}_{current_standings.get('round')}"
        
        normalized_data = {
            "drivers": [],
            "constructors": [],
            "driver_standings": [],
            "constructor_standings": []
        }

        # Process driver standings
        for standing in current_standings.get("DriverStandings", []):
            driver_data = standing.get("Driver", {})
            constructor_data = standing.get("Constructors", [{}])[0]  # Get first constructor
            
            normalized_data["drivers"].append(cls.normalize_f1_driver(driver_data))
            normalized_data["constructors"].append(cls.normalize_f1_constructor(constructor_data))
            normalized_data["driver_standings"].append(cls.normalize_f1_driver_standing(standing, race_id))

        # Process constructor standings if available
        for standing in current_standings.get("ConstructorStandings", []):
            constructor_data = standing.get("Constructor", {})
            normalized_data["constructors"].append(cls.normalize_f1_constructor(constructor_data))
            normalized_data["constructor_standings"].append(cls.normalize_f1_constructor_standing(standing, race_id))

        # Remove duplicates while preserving order
        for key in normalized_data:
            seen = set()
            normalized_data[key] = [
                x for x in normalized_data[key] 
                if not (
                    tuple(sorted(x.items())) in seen 
                    or seen.add(tuple(sorted(x.items())))
                )
            ]

        # Validate normalized data
        if not validate_pipeline_stage('normalization', normalized_data, platform='f1'):
            raise ValueError("Normalized F1 standings data failed validation")

        return normalized_data

# Example usage:
# normalizer = DataNormalizer()
# normalized_data = normalizer.normalize_f1_race_data(raw_api_response)
# normalized_typeracer = normalizer.normalize_typeracer_data(raw_typeracer_data)