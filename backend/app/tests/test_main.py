"""Tests for the main FastAPI application."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.query.processor import QueryProcessor
from app.pipeline.data2 import DataPipeline
from app.pipeline.optimized_adapters import OptimizedQueryAdapter, OptimizedResultAdapter

client = TestClient(app)

def test_analyze_empty_query():
    """Test that empty queries are properly rejected"""
    response = client.post("/api/v1/analyze", json={"query": ""})
    assert response.status_code == 400
    data = response.json()
    assert data["success"] == False
    assert "error" in data
    assert "Empty query" in data["details"]

def test_analyze_invalid_query():
    """Test handling of invalid queries"""
    response = client.post("/api/v1/analyze", json={"query": "   "})
    assert response.status_code == 400
    data = response.json()
    assert data["success"] == False
    assert "error" in data
    assert "Empty query" in data["details"]

def test_analyze_valid_query():
    """Test successful analysis of a valid query"""
    query = "Show Ferrari's performance in 2023"
    response = client.post("/api/v1/analyze", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "data" in data
    assert "executed_code" in data
    assert "query_trace" in data
    assert "processing_time" in data
    assert "metadata" in data

def test_analyze_pipeline_error():
    """Test handling of pipeline processing errors"""
    # Query that should trigger pipeline error
    query = "Invalid query that will cause pipeline error"
    response = client.post("/api/v1/analyze", json={"query": query})
    assert response.status_code == 400
    data = response.json()
    assert data["success"] == False
    assert "error" in data
    assert "details" in data

def test_analyze_missing_data():
    """Test handling of queries that return no data"""
    # Query that should return no data
    query = "Show results for nonexistent team"
    response = client.post("/api/v1/analyze", json={"query": query})
    assert response.status_code == 400
    data = response.json()
    assert data["success"] == False
    assert "No data available for analysis" in data["details"]

def test_analyze_code_execution_error():
    """Test handling of code execution errors"""
    # Mock a query that will generate invalid code
    query = "Generate invalid analysis code"
    response = client.post("/api/v1/analyze", json={"query": query})
    assert response.status_code == 400
    data = response.json()
    assert data["success"] == False
    assert "Code execution failed" in data["details"] 