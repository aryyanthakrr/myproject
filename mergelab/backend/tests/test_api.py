import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test that health endpoint returns correct structure."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert "gpu_available" in data
        assert "disk_space_gb" in data
        assert "disk_free_gb" in data
        assert "active_jobs" in data
        assert "models_cached" in data
        assert "uptime_seconds" in data
        
        assert data["status"] == "healthy"


class TestRootEndpoint:
    """Test root endpoint."""
    
    def test_root(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "MergeLab"
        assert "version" in data
        assert "intellectlabs" in data["built_by"]
        assert "Kepler" in data["built_by"]


class TestModelsEndpoint:
    """Test models list endpoint."""
    
    def test_list_models(self, client):
        """Test listing all models."""
        response = client.get("/api/models")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "models" in data
        assert "total" in data
        assert "categories" in data
        assert data["total"] > 0
    
    def test_filter_models_by_category(self, client):
        """Test filtering models by category."""
        response = client.get("/api/models?category=slm")
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned models should be SLM category
        for model in data["models"]:
            assert model["category"] == "slm"
    
    def test_filter_models_by_family(self, client):
        """Test filtering models by family."""
        response = client.get("/api/models?family=Qwen")
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned models should be Qwen family
        for model in data["models"]:
            assert "Qwen" in model["id"]
    
    def test_search_models(self, client):
        """Test searching models."""
        response = client.get("/api/models?search=llama")
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned models should contain 'llama' in id or name
        for model in data["models"]:
            assert "llama" in model["id"].lower() or "llama" in model["name"].lower()
    
    def test_get_families(self, client):
        """Test getting model families."""
        response = client.get("/api/models/families")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "families" in data
        assert "total" in data
        assert len(data["families"]) > 0
    
    def test_get_popular_merges(self, client):
        """Test getting popular merge combinations."""
        response = client.get("/api/models/popular")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "merges" in data
        assert len(data["merges"]) > 0


class TestMergeEndpoint:
    """Test merge job endpoints."""
    
    def test_create_merge_job_invalid_input(self, client):
        """Test creating merge job with invalid input."""
        # Missing required fields
        response = client.post("/api/merge", json={})
        
        assert response.status_code == 422  # Validation error
    
    def test_create_merge_job_invalid_model_format(self, client):
        """Test creating merge job with invalid model ID format."""
        response = client.post("/api/merge", json={
            "model_a": "invalid-model-id",
            "model_b": "also-invalid",
            "method": "slerp",
            "output_name": "TestMerge"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_create_merge_job_valid_structure(self, client):
        """Test creating merge job with valid structure."""
        response = client.post("/api/merge", json={
            "model_a": "Qwen/Qwen2.5-7B-Instruct",
            "model_b": "meta-llama/Llama-3.1-8B-Instruct",
            "method": "slerp",
            "ratio": 0.5,
            "output_format": "gguf-4bit",
            "output_name": "TestMerge"
        })
        
        # Should either succeed or fail due to missing HF token/network
        # but should not have validation errors
        assert response.status_code in [201, 500]
        
        if response.status_code == 201:
            data = response.json()
            assert "job_id" in data
            assert "status" in data


class TestAPIValidation:
    """Test API input validation."""
    
    def test_invalid_method(self, client):
        """Test that invalid merge method is rejected."""
        response = client.post("/api/merge", json={
            "model_a": "Qwen/Qwen2.5-7B-Instruct",
            "model_b": "meta-llama/Llama-3.1-8B-Instruct",
            "method": "invalid_method",
            "output_name": "TestMerge"
        })
        
        assert response.status_code == 422
    
    def test_invalid_ratio(self, client):
        """Test that ratio outside 0-1 is rejected."""
        response = client.post("/api/merge", json={
            "model_a": "Qwen/Qwen2.5-7B-Instruct",
            "model_b": "meta-llama/Llama-3.1-8B-Instruct",
            "method": "slerp",
            "ratio": 1.5,  # Invalid: > 1
            "output_name": "TestMerge"
        })
        
        assert response.status_code == 422
    
    def test_invalid_output_format(self, client):
        """Test that invalid output format is rejected."""
        response = client.post("/api/merge", json={
            "model_a": "Qwen/Qwen2.5-7B-Instruct",
            "model_b": "meta-llama/Llama-3.1-8B-Instruct",
            "method": "slerp",
            "output_format": "invalid-format",
            "output_name": "TestMerge"
        })
        
        assert response.status_code == 422
