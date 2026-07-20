import hashlib
import json
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class HashService:
    """Calculate and verify file hashes for integrity checking."""
    
    def __init__(self, algorithm: str = "sha256"):
        self.algorithm = algorithm
    
    def calculate_hash(self, file_path: str, chunk_size: int = 8192) -> str:
        """
        Calculate hash of a file.
        
        Args:
            file_path: Path to the file
            chunk_size: Size of chunks to read
            
        Returns:
            Hex digest of the hash
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if self.algorithm == "sha256":
            hasher = hashlib.sha256()
        elif self.algorithm == "md5":
            hasher = hashlib.md5()
        elif self.algorithm == "sha1":
            hasher = hashlib.sha1()
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def calculate_sha256(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        return self.calculate_hash(file_path, "sha256")
    
    def verify_integrity(self, file_path: str, expected_hash: str) -> bool:
        """
        Verify file integrity against expected hash.
        
        Args:
            file_path: Path to the file
            expected_hash: Expected hash value
            
        Returns:
            True if hash matches, False otherwise
        """
        try:
            actual_hash = self.calculate_sha256(file_path)
            return actual_hash.lower() == expected_hash.lower()
        except Exception as e:
            logger.error(f"Integrity verification error: {e}")
            return False
    
    def generate_integrity_certificate(self, file_path: str, metadata: Optional[Dict] = None) -> dict:
        """
        Generate an integrity certificate for a file.
        
        Args:
            file_path: Path to the file
            metadata: Optional additional metadata
            
        Returns:
            Certificate dictionary with all hashes and info
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Calculate multiple hashes for redundancy
        sha256_hash = self.calculate_hash(file_path, "sha256")
        md5_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
        sha1_hash = hashlib.sha1(open(file_path, 'rb').read()).hexdigest()
        
        # Get file info
        stat = file_path.stat()
        
        certificate = {
            "file_name": file_path.name,
            "file_path": str(file_path.absolute()),
            "file_size_bytes": stat.st_size,
            "file_size_human": self._format_size(stat.st_size),
            "hashes": {
                "sha256": sha256_hash,
                "md5": md5_hash,
                "sha1": sha1_hash
            },
            "algorithm_primary": "sha256",
            "generated_at": str(file_path.stat().st_mtime),
            "metadata": metadata or {}
        }
        
        return certificate
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"
    
    def save_certificate(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Generate and save integrity certificate to file.
        
        Args:
            file_path: Path to the file to certify
            output_path: Optional path for certificate file
            
        Returns:
            Path to saved certificate
        """
        certificate = self.generate_integrity_certificate(file_path)
        
        if output_path is None:
            output_path = str(Path(file_path).with_suffix('.cert.json'))
        
        with open(output_path, 'w') as f:
            json.dump(certificate, f, indent=2)
        
        logger.info(f"Certificate saved to: {output_path}")
        return output_path
    
    def load_certificate(self, cert_path: str) -> dict:
        """Load integrity certificate from file."""
        with open(cert_path, 'r') as f:
            return json.load(f)
    
    def verify_with_certificate(self, file_path: str, cert_path: str) -> bool:
        """
        Verify file against its certificate.
        
        Args:
            file_path: Path to the file
            cert_path: Path to the certificate
            
        Returns:
            True if verification passes
        """
        certificate = self.load_certificate(cert_path)
        expected_hash = certificate["hashes"]["sha256"]
        return self.verify_integrity(file_path, expected_hash)
