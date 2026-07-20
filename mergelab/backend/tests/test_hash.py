import pytest
from services.hash_service import HashService
import tempfile
import os


class TestHashService:
    """Test hash service functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.hash_service = HashService()
        self.test_content = b"Hello, MergeLab! This is a test file."
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(self.test_content)
        self.temp_file.close()
    
    def teardown_method(self):
        """Cleanup after tests."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_calculate_sha256(self):
        """Test SHA-256 calculation."""
        sha256_hash = self.hash_service.calculate_sha256(self.temp_file.name)
        
        # Verify hash format (64 hex characters)
        assert len(sha256_hash) == 64
        assert all(c in '0123456789abcdef' for c in sha256_hash)
    
    def test_hash_consistency(self):
        """Test that same content produces same hash."""
        hash1 = self.hash_service.calculate_sha256(self.temp_file.name)
        hash2 = self.hash_service.calculate_sha256(self.temp_file.name)
        
        assert hash1 == hash2
    
    def test_verify_integrity_correct(self):
        """Test integrity verification with correct hash."""
        expected_hash = self.hash_service.calculate_sha256(self.temp_file.name)
        result = self.hash_service.verify_integrity(self.temp_file.name, expected_hash)
        
        assert result is True
    
    def test_verify_integrity_incorrect(self):
        """Test integrity verification with incorrect hash."""
        wrong_hash = "a" * 64  # Invalid hash
        result = self.hash_service.verify_integrity(self.temp_file.name, wrong_hash)
        
        assert result is False
    
    def test_generate_certificate(self):
        """Test certificate generation."""
        cert = self.hash_service.generate_integrity_certificate(self.temp_file.name)
        
        assert "file_name" in cert
        assert "file_size_bytes" in cert
        assert "hashes" in cert
        assert "sha256" in cert["hashes"]
        assert "md5" in cert["hashes"]
        assert "sha1" in cert["hashes"]
    
    def test_certificate_hash_matches(self):
        """Test that certificate hash matches direct calculation."""
        cert = self.hash_service.generate_integrity_certificate(self.temp_file.name)
        direct_hash = self.hash_service.calculate_sha256(self.temp_file.name)
        
        assert cert["hashes"]["sha256"] == direct_hash
    
    def test_format_size(self):
        """Test size formatting."""
        assert self.hash_service._format_size(100) == "100.00 B"
        assert self.hash_service._format_size(1024) == "1.00 KB"
        assert self.hash_service._format_size(1048576) == "1.00 MB"
        assert self.hash_service._format_size(1073741824) == "1.00 GB"
    
    def test_save_and_load_certificate(self):
        """Test saving and loading certificate."""
        # Save certificate
        cert_path = self.hash_service.save_certificate(self.temp_file.name)
        
        # Load certificate
        loaded_cert = self.hash_service.load_certificate(cert_path)
        
        assert loaded_cert["hashes"]["sha256"] == self.hash_service.calculate_sha256(self.temp_file.name)
        
        # Cleanup
        os.unlink(cert_path)
    
    def test_verify_with_certificate(self):
        """Test verification using certificate file."""
        cert_path = self.hash_service.save_certificate(self.temp_file.name)
        
        result = self.hash_service.verify_with_certificate(self.temp_file.name, cert_path)
        
        assert result is True
        
        # Cleanup
        os.unlink(cert_path)
    
    def test_file_not_found(self):
        """Test error handling for missing file."""
        with pytest.raises(FileNotFoundError):
            self.hash_service.calculate_sha256("/nonexistent/file.txt")
