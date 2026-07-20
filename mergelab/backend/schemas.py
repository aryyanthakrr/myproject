from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, Dict, Any
from datetime import datetime
import re


class MergeRequest(BaseModel):
    """Request schema for merging models."""
    model_a: str = Field(..., description="First model ID (e.g., 'Qwen/Qwen2.5-7B-Instruct')")
    model_b: str = Field(..., description="Second model ID (e.g., 'meta-llama/Llama-3.1-8B-Instruct')")
    method: Literal["slerp", "ties", "dare", "linear", "passthrough"] = Field(
        default="slerp",
        description="Merge method to use"
    )
    ratio: float = Field(default=0.5, ge=0.0, le=1.0, description="Mix ratio (0.0 = 100% model_a, 1.0 = 100% model_b)")
    output_format: Literal["gguf-2bit", "gguf-4bit", "gguf-5bit", "gguf-8bit", "gguf-f16", "safetensors"] = Field(
        default="gguf-4bit",
        description="Output format for merged model"
    )
    output_name: str = Field(..., min_length=1, max_length=100, description="Name for the merged model")
    
    @validator('model_a', 'model_b')
    def validate_model_id(cls, v):
        """Validate model ID format."""
        if not re.match(r'^[\w\-\.]+/[\w\-\.]+$', v):
            raise ValueError('Model ID must be in format "owner/name"')
        return v
    
    @validator('output_name')
    def validate_output_name(cls, v):
        """Sanitize output name."""
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[^\w\-_]', '', v)
        if not sanitized:
            raise ValueError('Output name cannot be empty after sanitization')
        return sanitized


class MergeResponse(BaseModel):
    """Response schema for merge job creation."""
    job_id: str
    status: str
    message: str
    estimated_time_seconds: Optional[int] = None


class JobStatus(BaseModel):
    """Response schema for job status."""
    job_id: str
    status: str
    progress_percent: int
    current_step: str
    eta_seconds: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class JobResult(BaseModel):
    """Response schema for completed job."""
    job_id: str
    status: str
    output_name: str
    file_size: int
    file_size_human: str
    sha256_hash: str
    output_path: str
    download_url: str
    format: str
    model_a: str
    model_b: str
    method: str
    ratio: float
    created_at: datetime
    completed_at: datetime


class TestRequest(BaseModel):
    """Request schema for testing merged model."""
    prompt: str = Field(..., min_length=1, max_length=2000, description="Prompt to send to model")
    max_tokens: int = Field(default=256, ge=1, le=2048, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")


class TestResponse(BaseModel):
    """Response schema for model test."""
    response: str
    latency_ms: int
    tokens_generated: int
    tokens_per_second: float


class DeployRequest(BaseModel):
    """Request schema for deploying model."""
    deploy_name: Optional[str] = None
    expires_in_days: int = Field(default=7, ge=1, le=30, description="Deployment expiration in days")


class DeployResponse(BaseModel):
    """Response schema for deployment."""
    deploy_id: str
    api_url: str
    api_key: str
    expires_at: datetime
    status: str


class HFPushRequest(BaseModel):
    """Request schema for pushing to HuggingFace."""
    repo_id: str = Field(..., description="Target repository ID (e.g., 'username/model-name')")
    token: str = Field(..., description="HuggingFace API token")
    private: bool = Field(default=False, description="Whether to make repository private")


class HFPushResponse(BaseModel):
    """Response schema for HF push result."""
    success: bool
    hf_url: str
    message: str


class ModelInfo(BaseModel):
    """Schema for model information."""
    id: str
    name: str
    parameters: str
    size_gb: float
    license: str
    downloads: int
    family: str
    category: Literal["slm", "medium", "large"]  # slm: 1-3B, medium: 7-8B, large: 70B+
    tags: list = []


class ModelsListResponse(BaseModel):
    """Response schema for models list."""
    models: list[ModelInfo]
    total: int
    categories: Dict[str, int]


class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str
    version: str
    gpu_available: bool
    disk_space_gb: float
    disk_free_gb: float
    active_jobs: int
    models_cached: int
    uptime_seconds: int


class DownloadHeaders(BaseModel):
    """Schema for download response headers."""
    content_disposition: str
    content_type: str
    x_sha256: str
    x_file_size: str
    x_model_name: str
