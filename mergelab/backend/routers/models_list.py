from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session

from database import get_db
from schemas import ModelInfo, ModelsListResponse

router = APIRouter(prefix="/api/models", tags=["Models"])


# Pre-loaded list of popular mergeable models
POPULAR_MODELS = [
    # Qwen2.5 family
    {"id": "Qwen/Qwen2.5-0.5B-Instruct", "name": "Qwen2.5-0.5B", "parameters": "0.5B", "size_gb": 0.3, "license": "Apache-2.0", "downloads": 150000, "family": "Qwen", "category": "slm"},
    {"id": "Qwen/Qwen2.5-1.5B-Instruct", "name": "Qwen2.5-1.5B", "parameters": "1.5B", "size_gb": 0.9, "license": "Apache-2.0", "downloads": 280000, "family": "Qwen", "category": "slm"},
    {"id": "Qwen/Qwen2.5-3B-Instruct", "name": "Qwen2.5-3B", "parameters": "3B", "size_gb": 1.8, "license": "Apache-2.0", "downloads": 420000, "family": "Qwen", "category": "slm"},
    {"id": "Qwen/Qwen2.5-7B-Instruct", "name": "Qwen2.5-7B", "parameters": "7B", "size_gb": 4.2, "license": "Apache-2.0", "downloads": 850000, "family": "Qwen", "category": "medium"},
    {"id": "Qwen/Qwen2.5-14B-Instruct", "name": "Qwen2.5-14B", "parameters": "14B", "size_gb": 8.5, "license": "Apache-2.0", "downloads": 320000, "family": "Qwen", "category": "medium"},
    {"id": "Qwen/Qwen2.5-32B-Instruct", "name": "Qwen2.5-32B", "parameters": "32B", "size_gb": 19.0, "license": "Apache-2.0", "downloads": 180000, "family": "Qwen", "category": "large"},
    {"id": "Qwen/Qwen2.5-72B-Instruct", "name": "Qwen2.5-72B", "parameters": "72B", "size_gb": 42.0, "license": "Apache-2.0", "downloads": 95000, "family": "Qwen", "category": "large"},
    
    # Llama-3.1 family
    {"id": "meta-llama/Llama-3.1-8B-Instruct", "name": "Llama-3.1-8B", "parameters": "8B", "size_gb": 4.8, "license": "Llama-3.1", "downloads": 1200000, "family": "Llama", "category": "medium"},
    {"id": "meta-llama/Llama-3.1-70B-Instruct", "name": "Llama-3.1-70B", "parameters": "70B", "size_gb": 40.0, "license": "Llama-3.1", "downloads": 450000, "family": "Llama", "category": "large"},
    
    # Mistral family
    {"id": "mistralai/Mistral-7B-Instruct-v0.3", "name": "Mistral-7B-v0.3", "parameters": "7B", "size_gb": 4.1, "license": "Apache-2.0", "downloads": 680000, "family": "Mistral", "category": "medium"},
    {"id": "mistralai/Mixtral-8x7B-Instruct-v0.1", "name": "Mixtral-8x7B", "parameters": "47B", "size_gb": 26.0, "license": "Apache-2.0", "downloads": 380000, "family": "Mistral", "category": "large"},
    
    # Phi family
    {"id": "microsoft/Phi-3-mini-4k-instruct", "name": "Phi-3-mini", "parameters": "3.8B", "size_gb": 2.2, "license": "MIT", "downloads": 520000, "family": "Phi", "category": "slm"},
    {"id": "microsoft/Phi-3-medium-4k-instruct", "name": "Phi-3-medium", "parameters": "14B", "size_gb": 8.0, "license": "MIT", "downloads": 180000, "family": "Phi", "category": "medium"},
    
    # Gemma family
    {"id": "google/gemma-2-2b-it", "name": "Gemma-2-2B", "parameters": "2B", "size_gb": 1.2, "license": "Gemma", "downloads": 320000, "family": "Gemma", "category": "slm"},
    {"id": "google/gemma-2-9b-it", "name": "Gemma-2-9B", "parameters": "9B", "size_gb": 5.5, "license": "Gemma", "downloads": 280000, "family": "Gemma", "category": "medium"},
    {"id": "google/gemma-2-27b-it", "name": "Gemma-2-27B", "parameters": "27B", "size_gb": 16.0, "license": "Gemma", "downloads": 120000, "family": "Gemma", "category": "large"},
    
    # Yi family
    {"id": "01-ai/Yi-1.5-6B-Chat", "name": "Yi-1.5-6B", "parameters": "6B", "size_gb": 3.5, "license": "Apache-2.0", "downloads": 150000, "family": "Yi", "category": "medium"},
    {"id": "01-ai/Yi-1.5-9B-Chat", "name": "Yi-1.5-9B", "parameters": "9B", "size_gb": 5.2, "license": "Apache-2.0", "downloads": 130000, "family": "Yi", "category": "medium"},
    {"id": "01-ai/Yi-1.5-34B-Chat", "name": "Yi-1.5-34B", "parameters": "34B", "size_gb": 20.0, "license": "Apache-2.0", "downloads": 85000, "family": "Yi", "category": "large"},
    
    # Additional popular models
    {"id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", "name": "TinyLlama-1.1B", "parameters": "1.1B", "size_gb": 0.7, "license": "Apache-2.0", "downloads": 420000, "family": "Llama", "category": "slm"},
    {"id": "stabilityai/stablelm-2-zephyr-1_6b", "name": "StableLM-2-1.6B", "parameters": "1.6B", "size_gb": 0.9, "license": "CC-BY-SA-4.0", "downloads": 95000, "family": "StableLM", "category": "slm"},
    {"id": "CohereForAI/c4ai-command-r-plus", "name": "Command R+", "parameters": "104B", "size_gb": 60.0, "license": "CC-BY-NC-4.0", "downloads": 75000, "family": "Cohere", "category": "large"},
]


@router.get("", response_model=ModelsListResponse)
async def list_models(
    category: Optional[str] = None,
    family: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "downloads",
    db: Session = Depends(get_db)
):
    """
    List available models for merging.
    
    - **category**: Filter by category (slm, medium, large)
    - **family**: Filter by model family (Qwen, Llama, Mistral, etc.)
    - **search**: Search by name or ID
    - **sort_by**: Sort field (downloads, size_gb, parameters)
    """
    models = POPULAR_MODELS.copy()
    
    # Apply filters
    if category:
        models = [m for m in models if m["category"] == category]
    
    if family:
        models = [m for m in models if m["family"].lower() == family.lower()]
    
    if search:
        search_lower = search.lower()
        models = [m for m in models if search_lower in m["id"].lower() or search_lower in m["name"].lower()]
    
    # Apply sorting
    reverse = True  # Default to descending
    if sort_by not in ["downloads", "size_gb"]:
        sort_by = "downloads"
    
    models.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
    
    # Calculate category counts
    categories = {
        "slm": len([m for m in models if m["category"] == "slm"]),
        "medium": len([m for m in models if m["category"] == "medium"]),
        "large": len([m for m in models if m["category"] == "large"])
    }
    
    return ModelsListResponse(
        models=[ModelInfo(**m, tags=[]) for m in models],
        total=len(models),
        categories=categories
    )


@router.get("/families")
async def list_families():
    """List all available model families."""
    families = {}
    
    for model in POPULAR_MODELS:
        family = model["family"]
        if family not in families:
            families[family] = []
        families[family].append({
            "id": model["id"],
            "name": model["name"],
            "parameters": model["parameters"]
        })
    
    return {"families": families, "total": len(families)}


@router.get("/popular")
async def get_popular_merges():
    """Get popular model merge combinations."""
    popular_merges = [
        {
            "name": "Qwen + Llama",
            "model_a": "Qwen/Qwen2.5-7B-Instruct",
            "model_b": "meta-llama/Llama-3.1-8B-Instruct",
            "description": "Combine Qwen's reasoning with Llama's instruction following"
        },
        {
            "name": "Mistral + Phi",
            "model_a": "mistralai/Mistral-7B-Instruct-v0.3",
            "model_b": "microsoft/Phi-3-mini-4k-instruct",
            "description": "Blend Mistral's efficiency with Phi's compact knowledge"
        },
        {
            "name": "Gemma + Yi",
            "model_a": "google/gemma-2-9b-it",
            "model_b": "01-ai/Yi-1.5-9B-Chat",
            "description": "Merge Google's Gemma with Alibaba's Yi capabilities"
        },
        {
            "name": "SLM Power Merge",
            "model_a": "Qwen/Qwen2.5-3B-Instruct",
            "model_b": "microsoft/Phi-3-mini-4k-instruct",
            "description": "Create a powerful small language model"
        }
    ]
    
    return {"merges": popular_merges}
