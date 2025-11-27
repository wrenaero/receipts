"""Unit tests for main API application."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


class TestMainAPI:
    """Tests for main API endpoints."""

    @pytest.mark.unit
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"

    @pytest.mark.unit
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

    @pytest.mark.unit
    def test_scan_test_endpoint(self):
        """Test scan test endpoint."""
        response = client.get("/api/v1/test")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "endpoints" in data

    @pytest.mark.unit
    def test_api_docs_available(self):
        """Test that API documentation is available."""
        response = client.get("/docs")

        assert response.status_code == 200

    @pytest.mark.unit
    def test_openapi_schema(self):
        """Test OpenAPI schema is available."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "Receipt Scanner API"
