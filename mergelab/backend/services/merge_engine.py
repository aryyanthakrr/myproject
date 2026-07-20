import os
import subprocess
import tempfile
import yaml
import shutil
from typing import Optional, Callable
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MergeEngine:
    """Engine for merging AI models using mergekit."""
    
    SUPPORTED_METHODS = ["slerp", "ties", "dare", "linear", "passthrough"]
    
    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = Path(storage_path)
        self.models_dir = self.storage_path / "models"
        self.output_dir = self.storage_path / "merged"
        self.cache_dir = self.storage_path / "cache"
        
        # Ensure directories exist
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_merge_config(
        self,
        model_a: str,
        model_b: str,
        method: str,
        ratio: float,
        output_path: str
    ) -> dict:
        """Generate mergekit YAML configuration dynamically."""
        
        if method == "slerp":
            config = {
                "slices": [
                    {"sources": [{"model": model_a}, {"model": model_b}]}
                ],
                "merge_method": "slerp",
                "base_model": model_a,
                "parameters": {
                    "t": ratio  # ratio determines blend point
                },
                "dtype": "float16",
                "output_path": output_path
            }
        
        elif method == "ties":
            config = {
                "models": [
                    {"model": model_a, "parameters": {"weight": 1 - ratio}},
                    {"model": model_b, "parameters": {"weight": ratio}}
                ],
                "merge_method": "ties",
                "base_model": model_a,
                "parameters": {
                    "density": 0.5,
                    "int8_quantize": False
                },
                "dtype": "float16",
                "output_path": output_path
            }
        
        elif method == "dare":
            config = {
                "models": [
                    {"model": model_a, "parameters": {"weight": 1 - ratio}},
                    {"model": model_b, "parameters": {"weight": ratio}}
                ],
                "merge_method": "dare_ties",
                "base_model": model_a,
                "parameters": {
                    "density": 0.5,
                    "lambda": 0.5
                },
                "dtype": "float16",
                "output_path": output_path
            }
        
        elif method == "linear":
            config = {
                "models": [
                    {"model": model_a, "parameters": {"weight": 1 - ratio}},
                    {"model": model_b, "parameters": {"weight": ratio}}
                ],
                "merge_method": "linear",
                "dtype": "float16",
                "output_path": output_path
            }
        
        elif method == "passthrough":
            config = {
                "models": [{"model": model_a}],
                "merge_method": "passthrough",
                "dtype": "float16",
                "output_path": output_path
            }
        
        else:
            raise ValueError(f"Unsupported merge method: {method}")
        
        return config
    
    def merge_models(
        self,
        model_a: str,
        model_b: str,
        method: str,
        ratio: float = 0.5,
        dtype: str = "float16",
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> str:
        """
        Merge two models using the specified method.
        
        Args:
            model_a: First model path or HF ID
            model_b: Second model path or HF ID
            method: Merge method (slerp, ties, dare, linear, passthrough)
            ratio: Mix ratio (0.0-1.0)
            dtype: Data type for output
            progress_callback: Optional callback for progress updates
            
        Returns:
            Path to merged model directory
        """
        if method not in self.SUPPORTED_METHODS:
            raise ValueError(f"Method must be one of: {self.SUPPORTED_METHODS}")
        
        # Generate unique output path
        timestamp = subprocess.check_output(["date", "+%Y%m%d_%H%M%S"]).decode().strip()
        output_name = f"merged_{timestamp}"
        output_path = str(self.output_dir / output_name)
        
        # Generate config
        config = self._generate_merge_config(model_a, model_b, method, ratio, output_path)
        config["dtype"] = dtype
        
        # Write config to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            config_path = f.name
        
        try:
            if progress_callback:
                progress_callback("Starting merge...", 10)
            
            # Run mergekit
            cmd = [
                "mergekit-yaml",
                config_path,
                "--lazy-unpickle",
                "--allow-crimes"  # Allow loading models that might have issues
            ]
            
            logger.info(f"Running merge command: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Stream output
            for line in process.stderr:
                logger.info(line.strip())
                if progress_callback and "layer" in line.lower():
                    progress_callback(f"Merging layers... {line.strip()}", 50)
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"Merge failed: {stderr}")
            
            if progress_callback:
                progress_callback("Merge completed!", 90)
            
            logger.info(f"Merge completed successfully. Output: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Merge error: {e}")
            raise
        finally:
            # Cleanup config file
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def get_ram_usage(self) -> int:
        """Get current RAM usage in MB."""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss // (1024 * 1024)
        except ImportError:
            return 0
    
    def check_disk_space(self, required_gb: float = 10.0) -> bool:
        """Check if sufficient disk space is available."""
        import shutil
        total, used, free = shutil.disk_usage(self.storage_path)
        free_gb = free / (1024 ** 3)
        return free_gb >= required_gb
