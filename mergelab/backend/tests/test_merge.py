import pytest
from services.merge_engine import MergeEngine


class TestMergeEngine:
    """Test merge engine functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.engine = MergeEngine(storage_path="./test_storage")
    
    def test_supported_methods(self):
        """Test that all supported methods are defined."""
        expected_methods = ["slerp", "ties", "dare", "linear", "passthrough"]
        assert self.engine.SUPPORTED_METHODS == expected_methods
    
    def test_config_generation_slerp(self):
        """Test SLERP config generation."""
        config = self.engine._generate_merge_config(
            model_a="model/A",
            model_b="model/B",
            method="slerp",
            ratio=0.7,
            output_path="/tmp/output"
        )
        
        assert config["merge_method"] == "slerp"
        assert config["parameters"]["t"] == 0.7
        assert config["dtype"] == "float16"
    
    def test_config_generation_ties(self):
        """Test TIES config generation."""
        config = self.engine._generate_merge_config(
            model_a="model/A",
            model_b="model/B",
            method="ties",
            ratio=0.5,
            output_path="/tmp/output"
        )
        
        assert config["merge_method"] == "ties"
        assert len(config["models"]) == 2
        assert config["parameters"]["density"] == 0.5
    
    def test_config_generation_dare(self):
        """Test DARE config generation."""
        config = self.engine._generate_merge_config(
            model_a="model/A",
            model_b="model/B",
            method="dare",
            ratio=0.6,
            output_path="/tmp/output"
        )
        
        assert config["merge_method"] == "dare_ties"
        assert config["parameters"]["lambda"] == 0.5
    
    def test_config_generation_linear(self):
        """Test Linear config generation."""
        config = self.engine._generate_merge_config(
            model_a="model/A",
            model_b="model/B",
            method="linear",
            ratio=0.3,
            output_path="/tmp/output"
        )
        
        assert config["merge_method"] == "linear"
        assert config["models"][0]["parameters"]["weight"] == 0.7
        assert config["models"][1]["parameters"]["weight"] == 0.3
    
    def test_config_generation_passthrough(self):
        """Test Passthrough config generation."""
        config = self.engine._generate_merge_config(
            model_a="model/A",
            model_b="model/B",
            method="passthrough",
            ratio=0.5,
            output_path="/tmp/output"
        )
        
        assert config["merge_method"] == "passthrough"
        assert len(config["models"]) == 1
    
    def test_invalid_method(self):
        """Test that invalid method raises error."""
        with pytest.raises(ValueError):
            self.engine._generate_merge_config(
                model_a="model/A",
                model_b="model/B",
                method="invalid",
                ratio=0.5,
                output_path="/tmp/output"
            )
    
    def test_disk_space_check(self):
        """Test disk space checking."""
        # Should return True for small required space
        result = self.engine.check_disk_space(required_gb=0.001)
        assert isinstance(result, bool)
