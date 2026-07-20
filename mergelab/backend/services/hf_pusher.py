from huggingface_hub import HfApi, create_repo, upload_folder, upload_file
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class HFPusher:
    """Push merged models to HuggingFace Hub."""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.api = HfApi(token=token)
    
    def _generate_model_card(self, model_info: dict) -> str:
        """Generate a README.md model card for the merged model."""
        
        card = f"""---
license: apache-2.0
tags:
  - merge
  - mergelab
  - {model_info.get('method', 'merged')}
  - text-generation
base_model:
  - {model_info.get('model_a', 'unknown')}
  - {model_info.get('model_b', 'unknown')}
language:
  - en
pipeline_tag: text-generation
---

# {model_info.get('name', 'Merged Model')}

This model was created using [MergeLab](https://github.com/intellectlabs/mergelab) by [intellectlabs](https://intellectlabs.ai).

## Model Details

- **Merge Method**: {model_info.get('method', 'Unknown')}
- **Mix Ratio**: {model_info.get('ratio', 0.5)}
- **Base Model A**: [{model_info.get('model_a', 'Unknown')}]({model_info.get('model_a_url', '#')})
- **Base Model B**: [{model_info.get('model_b', 'Unknown')}]({model_info.get('model_b_url', '#')})
- **Output Format**: {model_info.get('format', 'GGUF')}
- **File Size**: {model_info.get('file_size_human', 'Unknown')}

## Merge Configuration

This model was created by merging two base models using the {model_info.get('method', 'unknown')} method with a mix ratio of {model_info.get('ratio', 0.5)}.

### What is Model Merging?

Model merging combines the weights of two or more pretrained models to create a new model that inherits capabilities from all source models. This technique is useful for:

- Combining specialized knowledge from different models
- Creating balanced models with diverse capabilities
- Experimenting with model architectures

## Usage

### With Transformers

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "{model_info.get('repo_id', 'username/model-name')}"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)
```

### With llama.cpp (GGUF)

```bash
# Download the GGUF file
wget https://huggingface.co/{model_info.get('repo_id', 'username/model-name')}/resolve/main/model.gguf

# Run inference
./main -m model.gguf -p "Your prompt here"
```

## Files

- `model.gguf` - Quantized GGUF format (recommended for local inference)
- `config.json` - Model configuration
- `tokenizer.json` - Tokenizer files

## License

This model is released under the Apache 2.0 license. Please respect the licenses of the base models used in this merge.

## Created with MergeLab

Built by [intellectlabs](https://intellectlabs.ai) | Founded by Kepler

[![MergeLab](https://img.shields.io/badge/MergeLab-v1.0.0-8b5cf6)](https://github.com/intellectlabs/mergelab)
"""
        return card
    
    def push_to_hub(
        self,
        model_path: str,
        repo_id: str,
        token: Optional[str] = None,
        private: bool = False,
        model_info: Optional[dict] = None,
        progress_callback: Optional[callable] = None
    ) -> str:
        """
        Push a merged model to HuggingFace Hub.
        
        Args:
            model_path: Path to the model directory or file
            repo_id: Repository ID in format "username/model-name"
            token: HuggingFace API token
            private: Whether to make repository private
            model_info: Optional model information for the card
            progress_callback: Optional callback for progress updates
            
        Returns:
            URL to the model on HuggingFace
        """
        if token:
            self.token = token
            self.api = HfApi(token=token)
        
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        try:
            # Create repository
            if progress_callback:
                progress_callback("Creating repository...", 10)
            
            create_repo(
                repo_id=repo_id,
                token=self.token,
                exist_ok=True,
                private=private
            )
            
            logger.info(f"Repository created/verified: {repo_id}")
            
            # Generate and upload model card
            if progress_callback:
                progress_callback("Generating model card...", 30)
            
            if model_info is None:
                model_info = {}
            
            model_info['repo_id'] = repo_id
            model_card = self._generate_model_card(model_info)
            
            # Write model card to temporary file
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                card_path = Path(tmpdir) / "README.md"
                with open(card_path, 'w') as f:
                    f.write(model_card)
                
                if progress_callback:
                    progress_callback("Uploading model card...", 40)
                
                upload_file(
                    path_or_fileobj=str(card_path),
                    path_in_repo="README.md",
                    repo_id=repo_id,
                    token=self.token,
                    repo_type="model"
                )
            
            # Upload model files
            if progress_callback:
                progress_callback("Uploading model files...", 50)
            
            if model_path.is_file():
                # Single file (e.g., GGUF)
                upload_file(
                    path_or_fileobj=str(model_path),
                    path_in_repo=model_path.name,
                    repo_id=repo_id,
                    token=self.token,
                    repo_type="model"
                )
            else:
                # Directory
                upload_folder(
                    folder_path=str(model_path),
                    repo_id=repo_id,
                    token=self.token,
                    repo_type="model"
                )
            
            if progress_callback:
                progress_callback("Upload complete!", 100)
            
            hf_url = f"https://huggingface.co/{repo_id}"
            logger.info(f"Model pushed successfully: {hf_url}")
            
            return hf_url
            
        except Exception as e:
            logger.error(f"Push to Hub error: {e}")
            raise
    
    def delete_from_hub(self, repo_id: str, token: Optional[str] = None) -> bool:
        """Delete a repository from HuggingFace Hub."""
        if token:
            self.token = token
            self.api = HfApi(token=token)
        
        try:
            self.api.delete_repo(repo_id, token=self.token)
            logger.info(f"Repository deleted: {repo_id}")
            return True
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False
    
    def list_user_models(self, token: Optional[str] = None) -> list:
        """List all models owned by the user."""
        if token:
            self.token = token
            self.api = HfApi(token=token)
        
        try:
            models = self.api.list_models(author=self.api.whoami(token=self.token)["username"])
            return [{"id": m.id, "likes": m.likes, "downloads": m.downloads} for m in models]
        except Exception as e:
            logger.error(f"List models error: {e}")
            return []
