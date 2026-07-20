import os
from pathlib import Path
from typing import Optional, Callable
from huggingface_hub import snapshot_download, hf_hub_download, HfApi
import logging

logger = logging.getLogger(__name__)


class ModelDownloader:
    """Download models from HuggingFace Hub with caching."""
    
    def __init__(self, storage_path: str = "./storage", hf_token: Optional[str] = None):
        self.storage_path = Path(storage_path)
        self.cache_dir = self.storage_path / "cache" / "models"
        self.hf_token = hf_token
        
        # Ensure directories exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize HF API if token provided
        self.api = HfApi(token=hf_token) if hf_token else None
    
    def _get_cache_path(self, model_id: str) -> Path:
        """Get cache path for a model ID."""
        # Replace slashes with underscores for directory name
        safe_name = model_id.replace("/", "_")
        return self.cache_dir / safe_name
    
    def _is_model_cached(self, model_id: str) -> bool:
        """Check if model is already cached."""
        cache_path = self._get_cache_path(model_id)
        return cache_path.exists() and any(cache_path.glob("*.safetensors"))
    
    def download_from_hf(
        self,
        model_id: str,
        revision: str = "main",
        allow_patterns: Optional[list] = None,
        ignore_patterns: Optional[list] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> str:
        """
        Download a model from HuggingFace Hub.
        
        Args:
            model_id: Model ID in format "owner/name"
            revision: Branch or tag to download
            allow_patterns: Patterns of files to download
            ignore_patterns: Patterns of files to ignore
            progress_callback: Optional callback for progress updates
            
        Returns:
            Local path to downloaded model
        """
        # Check cache first
        if self._is_model_cached(model_id):
            logger.info(f"Model {model_id} already cached, skipping download")
            if progress_callback:
                progress_callback("Using cached model...", 100)
            return str(self._get_cache_path(model_id))
        
        cache_path = self._get_cache_path(model_id)
        
        try:
            if progress_callback:
                progress_callback(f"Downloading {model_id}...", 0)
            
            # Default patterns for efficient download
            if allow_patterns is None:
                allow_patterns = [
                    "*.safetensors",
                    "*.bin",
                    "config.json",
                    "tokenizer.json",
                    "tokenizer_config.json",
                    "special_tokens_map.json",
                    "merges.txt",
                    "vocab.json",
                    "*.txt",
                    "*.json"
                ]
            
            if ignore_patterns is None:
                ignore_patterns = [
                    "*.pt",
                    "*.pth",
                    "*.msgpack",
                    "*.h5",
                    "*.pb",
                    "*.onnx",
                    "*.mlmodel",
                    "*.mlpackage",
                    "flax_model.msgpack"
                ]
            
            # Download using snapshot_download
            local_path = snapshot_download(
                repo_id=model_id,
                revision=revision,
                cache_dir=str(self.cache_dir),
                local_dir=str(cache_path),
                local_dir_use_symlinks=False,
                allow_patterns=allow_patterns,
                ignore_patterns=ignore_patterns,
                token=self.hf_token,
                resume_download=True
            )
            
            if progress_callback:
                progress_callback("Download complete!", 100)
            
            logger.info(f"Model downloaded successfully: {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Download error for {model_id}: {e}")
            raise
    
    def download_single_file(
        self,
        model_id: str,
        filename: str,
        revision: str = "main"
    ) -> str:
        """Download a single file from a model repository."""
        cache_path = self._get_cache_path(model_id)
        cache_path.mkdir(parents=True, exist_ok=True)
        
        file_path = hf_hub_download(
            repo_id=model_id,
            filename=filename,
            revision=revision,
            cache_dir=str(self.cache_dir),
            local_dir=str(cache_path),
            token=self.hf_token
        )
        
        return file_path
    
    def get_model_info(self, model_id: str) -> dict:
        """Get model information from HuggingFace."""
        try:
            info = self.api.model_info(model_id) if self.api else None
            
            if info:
                siblings = info.siblings or []
                total_size = sum(s.size for s in siblings if s.size)
                
                return {
                    "id": model_id,
                    "downloads": info.downloads or 0,
                    "likes": info.likes or 0,
                    "tags": info.tags or [],
                    "pipeline_tag": info.pipeline_tag,
                    "library_name": info.library_name,
                    "total_size_bytes": total_size,
                    "total_size_gb": total_size / (1024 ** 3)
                }
        except Exception as e:
            logger.warning(f"Could not fetch model info: {e}")
        
        return {
            "id": model_id,
            "downloads": 0,
            "likes": 0,
            "tags": [],
            "pipeline_tag": "text-generation",
            "library_name": "transformers",
            "total_size_bytes": 0,
            "total_size_gb": 0
        }
    
    def list_cached_models(self) -> list:
        """List all cached models."""
        cached = []
        for item in self.cache_dir.iterdir():
            if item.is_dir():
                # Convert back to model ID format
                model_id = item.name.replace("_", "/")
                cached.append({
                    "id": model_id,
                    "path": str(item),
                    "cached": True
                })
        return cached
    
    def clear_cache(self, model_id: Optional[str] = None) -> bool:
        """Clear model cache."""
        try:
            if model_id:
                cache_path = self._get_cache_path(model_id)
                if cache_path.exists():
                    import shutil
                    shutil.rmtree(cache_path)
                    logger.info(f"Cleared cache for {model_id}")
            else:
                import shutil
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                logger.info("Cleared all cache")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
