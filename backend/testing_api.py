import requests
import json
from typing import Dict, Any
import time

BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "barat_paim"

class TypeRacerAPITester:
    def __init__(self, base_url: str, username: str):
        self.base_url = base_url
        self.username = username
        self.player_id = f"tr:{username}"

    def _print_response(self, endpoint: str, response: Dict[str, Any]) -> None:
        """Pretty print the API response"""
        print(f"\n=== Testing {endpoint} ===")
        print(json.dumps(response, indent=2))
        print("=" * 50)

    def test_connect_user(self) -> Dict[str, Any]:
        """Test /connect_user endpoint"""
        endpoint = "/connect_user"
        response = requests.post(
            f"{self.base_url}{endpoint}",
            json={"username": self.username}
        )
        self._print_response(endpoint, response.json())
        return response.json()

    def test_fetch_data(self) -> Dict[str, Any]:
        """Test /fetch_data endpoint"""
        endpoint = "/fetch_data"
        response = requests.post(
            f"{self.base_url}{endpoint}",
            json={
                "player_id": self.player_id,
                "universe": "play",
                "n": 10
            }
        )
        self._print_response(endpoint, response.json())
        return response.json()

    def test_load_data(self) -> Dict[str, Any]:
        """Test /load_data endpoint"""
        endpoint = "/load_data"
        response = requests.get(f"{self.base_url}{endpoint}")
        self._print_response(endpoint, response.json())
        return response.json()

    def test_generate_code(self) -> Dict[str, Any]:
        """Test /generate_code endpoint"""
        endpoint = "/generate_code"
        questions = [
            "What is my average typing speed?",
            "Show my speed trend over time",
            "What is my fastest race?"
        ]
        
        results = []
        for question in questions:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json={"question": question}
            )
            results.append(response.json())
            self._print_response(f"{endpoint} - {question}", response.json())
            time.sleep(1)  # Rate limiting
        return results

    def test_execute_code(self) -> Dict[str, Any]:
        """Test /execute_code endpoint"""
        endpoint = "/execute_code"
        test_code = """
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Calculate average speed
result = df['speed'].mean()
"""
        response = requests.post(
            f"{self.base_url}{endpoint}",
            json={"code": test_code}
        )
        self._print_response(endpoint, response.json())
        return response.json()

    def test_player_dashboard(self) -> Dict[str, Any]:
        """Test /player_dashboard endpoint"""
        endpoint = f"/player_dashboard/{self.player_id}"
        response = requests.get(f"{self.base_url}{endpoint}")
        self._print_response(endpoint, response.json())
        return response.json()

    def test_query_guidance(self) -> Dict[str, Any]:
        """Test /query_guidance endpoint with various filters"""
        endpoint = "/query_guidance"
        results = []

        # Test 1: Get all questions (no filters)
        response = requests.get(f"{self.base_url}{endpoint}")
        self._print_response(f"{endpoint} - All Questions", response.json())
        results.append(response.json())

        # Test 2: Filter by level
        response = requests.get(f"{self.base_url}{endpoint}?level=Basic")
        self._print_response(f"{endpoint} - Basic Level", response.json())
        results.append(response.json())

        # Test 3: Filter by category
        response = requests.get(f"{self.base_url}{endpoint}?category=Performance%20Trends")
        self._print_response(f"{endpoint} - Performance Trends", response.json())
        results.append(response.json())

        # Test 4: Filter by both level and category
        response = requests.get(f"{self.base_url}{endpoint}?level=Basic&category=Summary%20Statistics")
        self._print_response(f"{endpoint} - Basic Summary Statistics", response.json())
        results.append(response.json())

        return results

    def run_all_tests(self) -> None:
        """Run all API tests in sequence"""
        try:
            print("\nStarting API Tests...")
            
            # Test user connection and data fetching
            user_data = self.test_connect_user()
            if user_data.get("status") == "success":
                self.test_fetch_data()
            
            # Test data loading and analysis
            self.test_load_data()
            
            # Test code generation and execution
            self.test_generate_code()
            self.test_execute_code()
            
            # Test dashboard and guidance
            self.test_player_dashboard()
            self.test_query_guidance()
            
            print("\nAll tests completed!")
            
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to the API. Make sure the server is running.")
        except Exception as e:
            print(f"Error during testing: {str(e)}")

def main():
    tester = TypeRacerAPITester(BASE_URL, USERNAME)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
