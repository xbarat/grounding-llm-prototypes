"""
Data normalization module for standardizing API responses.
Provides functions to transform raw API data into a format matching our database schema.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataNormalizer:
    """
    Handles normalization of data from different platforms into a unified schema.
    """

    @staticmethod
    def normalize_f1_driver(raw_driver: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize driver data from F1 API."""
        return {
            "driver_id": raw_driver.get("driverId"),
            "code": raw_driver.get("code"),
            "number": int(raw_driver.get("permanentNumber", 0)) if raw_driver.get("permanentNumber") else None,
            "given_name": raw_driver.get("givenName"),
            "family_name": raw_driver.get("familyName"),
            "nationality": raw_driver.get("nationality")
        }

    @staticmethod
    def normalize_f1_constructor(raw_constructor: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize constructor/team data from F1 API."""
        return {
            "constructor_id": raw_constructor.get("constructorId"),
            "name": raw_constructor.get("name"),
            "nationality": raw_constructor.get("nationality")
        }

    @staticmethod
    def normalize_f1_circuit(raw_circuit: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize circuit data from F1 API."""
        return {
            "circuit_id": raw_circuit.get("circuitId"),
            "name": raw_circuit.get("circuitName"),
            "location": raw_circuit.get("Location", {}).get("locality"),
            "country": raw_circuit.get("Location", {}).get("country"),
            "lat": float(raw_circuit.get("Location", {}).get("lat", 0)),
            "lng": float(raw_circuit.get("Location", {}).get("long", 0))
        }

    @staticmethod
    def normalize_f1_race(raw_race: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize race data from F1 API."""
        try:
            date_str = f"{raw_race.get('date')} {raw_race.get('time', '00:00:00Z')}"
            race_date = datetime.strptime(date_str.strip("Z"), "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            race_date = None
            logger.warning(f"Failed to parse date for race: {raw_race.get('raceName')}")

        return {
            "race_id": raw_race.get("raceId"),
            "season": int(raw_race.get("season", 0)),
            "round": int(raw_race.get("round", 0)),
            "circuit_id": raw_race.get("Circuit", {}).get("circuitId"),
            "name": raw_race.get("raceName"),
            "date": race_date,
            "time": raw_race.get("time")
        }

    @staticmethod
    def normalize_f1_race_result(raw_result: Dict[str, Any], race_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize race result data from F1 API."""
        fastest_lap = raw_result.get("FastestLap", {})
        return {
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

    @staticmethod
    def normalize_f1_qualifying_result(raw_qualifying: Dict[str, Any], race_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize qualifying result data from F1 API."""
        return {
            "race_id": race_data.get("race_id"),
            "driver_id": raw_qualifying.get("Driver", {}).get("driverId"),
            "constructor_id": raw_qualifying.get("Constructor", {}).get("constructorId"),
            "position": int(raw_qualifying.get("position", 0)),
            "q1": raw_qualifying.get("Q1"),
            "q2": raw_qualifying.get("Q2"),
            "q3": raw_qualifying.get("Q3")
        }

    @staticmethod
    def normalize_f1_driver_standing(raw_standing: Dict[str, Any], race_id: str) -> Dict[str, Any]:
        """Normalize driver standing data from F1 API."""
        return {
            "race_id": race_id,
            "driver_id": raw_standing.get("Driver", {}).get("driverId"),
            "points": float(raw_standing.get("points", 0)),
            "position": int(raw_standing.get("position", 0)),
            "wins": int(raw_standing.get("wins", 0))
        }

    @staticmethod
    def normalize_f1_constructor_standing(raw_standing: Dict[str, Any], race_id: str) -> Dict[str, Any]:
        """Normalize constructor standing data from F1 API."""
        return {
            "race_id": race_id,
            "constructor_id": raw_standing.get("Constructor", {}).get("constructorId"),
            "points": float(raw_standing.get("points", 0)),
            "position": int(raw_standing.get("position", 0)),
            "wins": int(raw_standing.get("wins", 0))
        }

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

        return normalized_data

    @staticmethod
    def normalize_typeracer_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize TypeRacer data into our schema."""
        # Add TypeRacer normalization logic here when needed
        pass

# Example usage:
# normalizer = DataNormalizer()
# normalized_data = normalizer.normalize_f1_race_data(raw_api_response)
# normalized_typeracer = normalizer.normalize_typeracer_data(raw_typeracer_data)