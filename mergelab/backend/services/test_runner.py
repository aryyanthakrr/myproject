from pathlib import Path
from typing import Optional, List, Dict
import time
import logging

logger = logging.getLogger(__name__)


class TestRunner:
    """Test merged models with chat and benchmarking."""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Load a model for inference.
        
        Args:
            model_path: Path to the model (GGUF or transformers format)
            
        Returns:
            True if loaded successfully
        """
        model_path = model_path or self.model_path
        
        if not model_path:
            raise ValueError("No model path provided")
        
        path = Path(model_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {path}")
        
        try:
            # Check if GGUF format
            if path.suffix == '.gguf':
                return self._load_gguf(str(path))
            else:
                return self._load_transformers(str(path))
        except Exception as e:
            logger.error(f"Model load error: {e}")
            raise
    
    def _load_gguf(self, model_path: str) -> bool:
        """Load GGUF model using llama-cpp-python."""
        try:
            from llama_cpp import Llama
            
            self.model = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_batch=512,
                n_threads=4,
                verbose=False
            )
            
            logger.info(f"GGUF model loaded: {model_path}")
            return True
            
        except ImportError:
            logger.warning("llama-cpp-python not installed, trying transformers...")
            return self._load_transformers(model_path)
    
    def _load_transformers(self, model_path: str) -> bool:
        """Load model using transformers."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            logger.info("Loading model with transformers...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )
            
            logger.info(f"Transformers model loaded: {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Transformers load error: {e}")
            raise
    
    def chat(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7
    ) -> Dict:
        """
        Chat with the loaded model.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Dictionary with response and metadata
        """
        if self.model is None:
            raise RuntimeError("No model loaded. Call load_model() first.")
        
        start_time = time.time()
        
        try:
            if hasattr(self.model, 'create_completion'):
                # GGUF model (llama-cpp)
                response = self.model.create_completion(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=["User:", "Human:", "Assistant:"]
                )
                
                text = response['choices'][0]['text']
                tokens_generated = len(self.model.tokenize(text.encode()))
                
            else:
                # Transformers model
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
                
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=temperature > 0,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
                text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                # Remove prompt from response
                text = text[len(prompt):].strip()
                tokens_generated = len(outputs[0]) - len(inputs['input_ids'][0])
            
            latency_ms = int((time.time() - start_time) * 1000)
            tokens_per_second = tokens_generated / (latency_ms / 1000) if latency_ms > 0 else 0
            
            return {
                "response": text,
                "latency_ms": latency_ms,
                "tokens_generated": tokens_generated,
                "tokens_per_second": round(tokens_per_second, 2)
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise
    
    def benchmark(self, prompts: List[str], max_tokens: int = 100) -> Dict:
        """
        Benchmark model with multiple prompts.
        
        Args:
            prompts: List of prompts to test
            max_tokens: Maximum tokens per generation
            
        Returns:
            Benchmark statistics
        """
        if not prompts:
            raise ValueError("No prompts provided")
        
        results = []
        total_tokens = 0
        total_time = 0
        
        for i, prompt in enumerate(prompts):
            logger.info(f"Benchmark prompt {i+1}/{len(prompts)}")
            
            try:
                result = self.chat(prompt, max_tokens=max_tokens, temperature=0.7)
                results.append(result)
                total_tokens += result['tokens_generated']
                total_time += result['latency_ms']
            except Exception as e:
                logger.warning(f"Benchmark failed for prompt {i+1}: {e}")
                results.append({"error": str(e)})
        
        successful = [r for r in results if 'error' not in r]
        
        if not successful:
            return {
                "success": False,
                "error": "All benchmarks failed"
            }
        
        avg_latency = sum(r['latency_ms'] for r in successful) / len(successful)
        avg_tokens = sum(r['tokens_generated'] for r in successful) / len(successful)
        
        return {
            "success": True,
            "prompts_tested": len(prompts),
            "successful_runs": len(successful),
            "failed_runs": len(prompts) - len(successful),
            "avg_latency_ms": round(avg_latency, 2),
            "avg_tokens": round(avg_tokens, 2),
            "avg_tokens_per_second": round(avg_tokens / (avg_latency / 1000), 2),
            "total_tokens": total_tokens,
            "total_time_ms": total_time
        }
    
    def calculate_quality_score(self, responses: List[str]) -> float:
        """
        Calculate a simple quality score based on response coherence.
        
        This is a basic implementation. In production, you might use
        more sophisticated metrics like BLEU, ROUGE, or learned metrics.
        
        Args:
            responses: List of model responses
            
        Returns:
            Quality score (0-100)
        """
        if not responses:
            return 0.0
        
        scores = []
        
        for response in responses:
            score = 50.0  # Base score
            
            # Length bonus (not too short, not too long)
            length = len(response.split())
            if 20 <= length <= 200:
                score += 20
            elif 10 <= length < 20 or 200 < length <= 300:
                score += 10
            
            # Coherence indicators
            if any(word in response.lower() for word in ['the', 'a', 'is', 'are', 'was', 'were']):
                score += 10
            
            # Penalize repetition
            words = response.lower().split()
            if len(words) > 0:
                unique_ratio = len(set(words)) / len(words)
                score += unique_ratio * 20
            
            scores.append(min(100, max(0, score)))
        
        return sum(scores) / len(scores)
    
    def unload(self):
        """Unload the model to free memory."""
        if self.model is not None:
            del self.model
            self.model = None
            
            import gc
            gc.collect()
            
            try:
                import torch
                torch.cuda.empty_cache()
            except:
                pass
            
            logger.info("Model unloaded")
