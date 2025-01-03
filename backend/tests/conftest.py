import pytest
from dotenv import load_dotenv
import os

def pytest_configure():
    """Load environment variables before running tests."""
    # Load from .env file
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_path) 