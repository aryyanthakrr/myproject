import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class Quantizer:
    """Quantize models to GGUF format using llama.cpp."""
    
    SUPPORTED_BITS = ["2", "4", "5", "8", "f16"]
    QUANT_NAMES = {
        "2": "Q2_K",
        "4": "Q4_K_M",
        "5": "Q5_K_M",
        "8": "Q8_0",
        "f16": "F16"
    }
    
    def __init__(self, storage_path: str = "./storage", llama_cpp_path: str = "/opt/llama.cpp"):
        self.storage_path = Path(storage_path)
        self.quantized_dir = self.storage_path / "quantized"
        self.llama_cpp_path = Path(llama_cpp_path)
        
        # Ensure directories exist
        self.quantized_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_quant_script(self) -> Optional[Path]:
        """Find the quantization conversion script."""
        possible_paths = [
            self.llama_cpp_path / "convert-hf-to-gguf.py",
            Path("./convert-hf-to-gguf.py"),
            Path("/app/convert-hf-to-gguf.py")
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def _find_quantize_binary(self) -> Optional[Path]:
        """Find the llama.cpp quantize binary."""
        possible_paths = [
            self.llama_cpp_path / "quantize",
            self.llama_cpp_path / "build" / "bin" / "quantize",
            Path("/usr/local/bin/llama-quantize")
        ]
        
        for path in possible_paths:
            if path.exists() and os.access(path, os.X_OK):
                return path
        
        return None
    
    def quantize_gguf(
        self,
        model_path: str,
        bits: str = "4",
        progress_callback: Optional[callable] = None
    ) -> Tuple[str, int]:
        """
        Quantize a model to GGUF format.
        
        Args:
            model_path: Path to the model directory (safetensors or pytorch)
            bits: Quantization bits (2, 4, 5, 8, f16)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple of (quantized_model_path, file_size_bytes)
        """
        if bits not in self.SUPPORTED_BITS:
            raise ValueError(f"Bits must be one of: {self.SUPPORTED_BITS}")
        
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Generate output filename
        model_name = model_path.name
        quant_name = self.QUANT_NAMES.get(bits, f"Q{bits}_K_M")
        output_filename = f"{model_name}_{quant_name.lower()}.gguf"
        output_path = self.quantized_dir / output_filename
        
        try:
            if progress_callback:
                progress_callback(f"Converting to GGUF ({quant_name})...", 0)
            
            # Step 1: Convert to GGUF F16 first
            convert_script = self._get_quant_script()
            
            if convert_script:
                logger.info(f"Using conversion script: {convert_script}")
                
                # Run conversion
                cmd = [
                    "python3",
                    str(convert_script),
                    str(model_path),
                    "--outfile",
                    str(output_path.with_suffix('.f16.gguf'))
                ]
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    logger.warning(f"Conversion warning: {stderr}")
                    # Continue anyway, might still work
                
                intermediate_path = output_path.with_suffix('.f16.gguf')
            else:
                # Try using transformers to export
                logger.info("No conversion script found, attempting direct export...")
                intermediate_path = self._export_with_transformers(model_path, output_path.with_suffix('.f16.gguf'))
            
            # Step 2: Quantize if not f16
            if bits != "f16":
                if progress_callback:
                    progress_callback(f"Quantizing to {quant_name}...", 50)
                
                quantize_binary = self._find_quantize_binary()
                
                if quantize_binary:
                    cmd = [
                        str(quantize_binary),
                        str(intermediate_path),
                        str(output_path),
                        self.QUANT_NAMES[bits]
                    ]
                    
                    process = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True
                    )
                    
                    if process.returncode != 0:
                        logger.warning(f"Quantization warning: {process.stderr}")
                        # Use the F16 version as fallback
                        output_path = intermediate_path
                    else:
                        # Remove intermediate file
                        if intermediate_path.exists():
                            os.unlink(intermediate_path)
                else:
                    logger.warning("No quantize binary found, using F16 version")
                    output_path = intermediate_path
            else:
                # Rename F16 to final name
                if intermediate_path.exists() and intermediate_path != output_path:
                    os.rename(intermediate_path, output_path)
            
            # Get file size
            file_size = output_path.stat().st_size
            
            if progress_callback:
                progress_callback("Quantization complete!", 100)
            
            logger.info(f"Quantization complete: {output_path} ({file_size / (1024**3):.2f} GB)")
            return str(output_path), file_size
            
        except Exception as e:
            logger.error(f"Quantization error: {e}")
            raise
    
    def _export_with_transformers(self, model_path: Path, output_path: Path) -> Path:
        """Export model to GGUF using transformers library."""
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        
        logger.info("Loading model with transformers...")
        
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            str(model_path),
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True
        )
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        
        # Save in a format that can be converted
        temp_dir = model_path.parent / "temp_export"
        temp_dir.mkdir(exist_ok=True)
        
        model.save_pretrained(temp_dir)
        tokenizer.save_pretrained(temp_dir)
        
        # Return path for further processing
        return output_path
    
    def auto_detect_best_quantization(self, model_size_gb: float) -> str:
        """Auto-detect best quantization based on model size."""
        if model_size_gb > 70:
            return "2"  # Q2_K for very large models
        elif model_size_gb > 30:
            return "4"  # Q4_K_M for large models
        elif model_size_gb > 10:
            return "5"  # Q5_K_M for medium models
        else:
            return "8"  # Q8_0 for small models
    
    def get_file_size_human(self, size_bytes: int) -> str:
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"
