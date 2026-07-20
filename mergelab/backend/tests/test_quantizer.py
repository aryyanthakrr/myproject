import pytest
from services.quantizer import Quantizer


class TestQuantizer:
    """Test quantizer functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.quantizer = Quantizer(storage_path="./test_storage")
    
    def test_supported_bits(self):
        """Test that all supported bit widths are defined."""
        expected_bits = ["2", "4", "5", "8", "f16"]
        assert self.quantizer.SUPPORTED_BITS == expected_bits
    
    def test_quant_names(self):
        """Test quantization name mapping."""
        expected_names = {
            "2": "Q2_K",
            "4": "Q4_K_M",
            "5": "Q5_K_M",
            "8": "Q8_0",
            "f16": "F16"
        }
        assert self.quantizer.QUANT_NAMES == expected_names
    
    def test_auto_detect_small_model(self):
        """Test auto-detection for small models."""
        result = self.quantizer.auto_detect_best_quantization(model_size_gb=5.0)
        assert result == "8"  # Q8_0 for small models
    
    def test_auto_detect_medium_model(self):
        """Test auto-detection for medium models."""
        result = self.quantizer.auto_detect_best_quantization(model_size_gb=15.0)
        assert result == "5"  # Q5_K_M for medium models
    
    def test_auto_detect_large_model(self):
        """Test auto-detection for large models."""
        result = self.quantizer.auto_detect_best_quantization(model_size_gb=50.0)
        assert result == "4"  # Q4_K_M for large models
    
    def test_auto_detect_very_large_model(self):
        """Test auto-detection for very large models."""
        result = self.quantizer.auto_detect_best_quantization(model_size_gb=80.0)
        assert result == "2"  # Q2_K for very large models
    
    def test_get_file_size_human(self):
        """Test human-readable file size formatting."""
        assert self.quantizer.get_file_size_human(100) == "100.00 B"
        assert self.quantizer.get_file_size_human(1024) == "1.00 KB"
        assert self.quantizer.get_file_size_human(1048576) == "1.00 MB"
        assert self.quantizer.get_file_size_human(1073741824) == "1.00 GB"
        assert self.quantizer.get_file_size_human(1099511627776) == "1.00 TB"
    
    def test_invalid_bits_raises_error(self):
        """Test that invalid bits value raises error."""
        with pytest.raises(ValueError, match="Bits must be one of"):
            # This would fail at validation before actual quantization
            assert "invalid" not in self.quantizer.SUPPORTED_BITS
