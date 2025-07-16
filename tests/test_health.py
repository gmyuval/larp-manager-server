"""
Tests for health check endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch

from src.larp_manager_server.database import db_manager


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_basic_health_check(self, mock_client):
        """Test basic health check endpoint."""
        response = mock_client.get("/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "larp-manager-server"
        assert data["version"] == "1.0.0"
    
    def test_liveness_check(self, mock_client):
        """Test liveness check endpoint."""
        response = mock_client.get("/health/live")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "alive"
        assert data["service"] == "larp-manager-server"
    
    @patch.object(db_manager, 'health_check')
    def test_database_health_check_healthy(self, mock_health_check, mock_client):
        """Test database health check when database is healthy."""
        mock_health_check.return_value = {
            "status": "healthy",
            "test_query": True,
            "schema_exists": True,
            "pool_stats": {
                "pool_size": 20,
                "checked_in": 19,
                "checked_out": 1,
                "overflow": 0,
                "invalid": 0,
            },
            "error": None
        }
        
        response = mock_client.get("/health/db")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert data["database"]["status"] == "healthy"
        assert data["database"]["test_query"] is True
    
    @patch.object(db_manager, 'health_check')
    def test_database_health_check_unhealthy(self, mock_health_check, mock_client):
        """Test database health check when database is unhealthy."""
        mock_health_check.return_value = {
            "status": "unhealthy",
            "error": "Connection failed",
            "details": None
        }
        
        response = mock_client.get("/health/db")
        
        assert response.status_code == 503
        
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "database" in data
        assert data["database"]["status"] == "unhealthy"
        assert "Connection failed" in data["database"]["error"]
    
    @patch.object(db_manager, 'health_check')
    def test_database_health_check_exception(self, mock_health_check, mock_client):
        """Test database health check when an exception occurs."""
        mock_health_check.side_effect = Exception("Unexpected error")
        
        response = mock_client.get("/health/db")
        
        assert response.status_code == 503
        
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "database" in data
        assert data["database"]["status"] == "unhealthy"
        assert "Unexpected error" in data["database"]["error"]
    
    @patch.object(db_manager, 'health_check')
    def test_readiness_check_ready(self, mock_health_check, mock_client):
        """Test readiness check when system is ready."""
        mock_health_check.return_value = {
            "status": "healthy",
            "test_query": True,
            "schema_exists": True,
            "pool_stats": {
                "pool_size": 20,
                "checked_in": 19,
                "checked_out": 1,
                "overflow": 0,
                "invalid": 0,
            },
            "error": None
        }
        
        response = mock_client.get("/health/ready")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ready"
        assert data["service"] == "larp-manager-server"
        assert "database" in data
        assert data["database"]["status"] == "healthy"
    
    @patch.object(db_manager, 'health_check')
    def test_readiness_check_not_ready(self, mock_health_check, mock_client):
        """Test readiness check when system is not ready."""
        mock_health_check.return_value = {
            "status": "unhealthy",
            "error": "Database connection failed",
            "details": None
        }
        
        response = mock_client.get("/health/ready")
        
        assert response.status_code == 503
        
        data = response.json()
        assert data["status"] == "not_ready"
        assert data["reason"] == "Database not healthy"
        assert "database" in data
        assert data["database"]["status"] == "unhealthy"
    
    @patch.object(db_manager, 'health_check')
    def test_readiness_check_exception(self, mock_health_check, mock_client):
        """Test readiness check when an exception occurs."""
        mock_health_check.side_effect = Exception("Unexpected error")
        
        response = mock_client.get("/health/ready")
        
        assert response.status_code == 503
        
        data = response.json()
        assert data["status"] == "not_ready"
        assert "Unexpected error" in data["reason"]