# MergeLab API Documentation

## Base URL

```
Production: https://api.mergelab.intellectlabs.ai
Local: http://localhost:8000
```

## Authentication

Most endpoints are public. Protected endpoints require authentication via NextAuth.js session tokens.

---

## Endpoints

### Health Check

#### GET `/api/health`

Check system health and status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "gpu_available": true,
  "disk_space_gb": 500.0,
  "disk_free_gb": 350.5,
  "active_jobs": 2,
  "models_cached": 15,
  "uptime_seconds": 86400
}
```

---

### Models

#### GET `/api/models`

List available models for merging.

**Query Parameters:**
- `category` (optional): Filter by category (`slm`, `medium`, `large`)
- `family` (optional): Filter by family (`Qwen`, `Llama`, `Mistral`, etc.)
- `search` (optional): Search by name or ID
- `sort_by` (optional): Sort field (`downloads`, `size_gb`)

**Response:**
```json
{
  "models": [
    {
      "id": "Qwen/Qwen2.5-7B-Instruct",
      "name": "Qwen2.5-7B",
      "parameters": "7B",
      "size_gb": 4.2,
      "license": "Apache-2.0",
      "downloads": 850000,
      "family": "Qwen",
      "category": "medium",
      "tags": []
    }
  ],
  "total": 25,
  "categories": {
    "slm": 8,
    "medium": 10,
    "large": 7
  }
}
```

#### GET `/api/models/families`

List all available model families.

**Response:**
```json
{
  "families": {
    "Qwen": [
      {"id": "Qwen/Qwen2.5-7B-Instruct", "name": "Qwen2.5-7B", "parameters": "7B"}
    ],
    "Llama": [...]
  },
  "total": 8
}
```

#### GET `/api/models/popular`

Get popular merge combinations.

**Response:**
```json
{
  "merges": [
    {
      "name": "Qwen + Llama",
      "model_a": "Qwen/Qwen2.5-7B-Instruct",
      "model_b": "meta-llama/Llama-3.1-8B-Instruct",
      "description": "Combine Qwen's reasoning with Llama's instruction following"
    }
  ]
}
```

---

### Merge Jobs

#### POST `/api/merge`

Create a new merge job.

**Request Body:**
```json
{
  "model_a": "Qwen/Qwen2.5-7B-Instruct",
  "model_b": "meta-llama/Llama-3.1-8B-Instruct",
  "method": "slerp",
  "ratio": 0.5,
  "output_format": "gguf-4bit",
  "output_name": "MyMergedModel"
}
```

**Fields:**
- `model_a` (required): First model ID in format `owner/name`
- `model_b` (required): Second model ID in format `owner/name`
- `method` (required): Merge method (`slerp`, `ties`, `dare`, `linear`, `passthrough`)
- `ratio` (optional): Mix ratio 0.0-1.0 (default: 0.5)
- `output_format` (optional): Output format (`gguf-2bit`, `gguf-4bit`, `gguf-5bit`, `gguf-8bit`, `gguf-f16`, `safetensors`)
- `output_name` (required): Name for the merged model

**Response (201):**
```json
{
  "job_id": "abc12345",
  "status": "pending",
  "message": "Merge job created. Merging Qwen/Qwen2.5-7B-Instruct + meta-llama/Llama-3.1-8B-Instruct",
  "estimated_time_seconds": 300
}
```

#### GET `/api/merge/{job_id}/status`

Get status of a merge job.

**Response:**
```json
{
  "job_id": "abc12345",
  "status": "processing",
  "progress_percent": 45,
  "current_step": "Merging layers...",
  "eta_seconds": 120,
  "error_message": null,
  "created_at": "2026-01-15T10:30:00Z",
  "completed_at": null
}
```

**Status Values:**
- `pending`: Job queued
- `downloading`: Downloading models from HuggingFace
- `merging`: Running merge operation
- `quantizing`: Converting to GGUF format
- `verifying`: Calculating SHA-256 hash
- `completed`: Merge successful
- `failed`: Merge failed

#### GET `/api/merge/{job_id}/download`

Download the merged model file.

**Headers:**
- `X-SHA256`: SHA-256 hash of the file
- `X-File-Size`: File size in bytes
- `X-Model-Name`: Model name
- `Content-Disposition`: Attachment filename

**Response:** Binary file download

#### POST `/api/merge/{job_id}/test`

Test the merged model with a prompt.

**Request Body:**
```json
{
  "prompt": "Hello, how are you?",
  "max_tokens": 256,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
  "latency_ms": 230,
  "tokens_generated": 18,
  "tokens_per_second": 78.26
}
```

#### POST `/api/merge/{job_id}/deploy`

Deploy the merged model as an API endpoint.

**Request Body:**
```json
{
  "deploy_name": "my-model-api",
  "expires_in_days": 7
}
```

**Response:**
```json
{
  "deploy_id": "deploy_xyz789",
  "api_url": "https://api.mergelab.intellectlabs.ai/v1/deploy_xyz789",
  "api_key": "ml_abcdef123456",
  "expires_at": "2026-01-22T10:30:00Z",
  "status": "active"
}
```

#### POST `/api/merge/{job_id}/push-hf`

Push merged model to HuggingFace Hub.

**Request Body:**
```json
{
  "repo_id": "username/model-name",
  "token": "hf_xxx",
  "private": false
}
```

**Response:**
```json
{
  "success": true,
  "hf_url": "https://huggingface.co/username/model-name",
  "message": "Successfully pushed to https://huggingface.co/username/model-name"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Job not completed. Status: processing"
}
```

### 404 Not Found
```json
{
  "detail": "Job not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "model_a"],
      "msg": "Model ID must be in format \"owner/name\"",
      "type": "value_error"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Merge failed: Out of memory"
}
```

---

## Rate Limiting

- **Free tier**: 5 merges per hour
- **Pro tier**: Unlimited merges

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Merge Methods

### SLERP (Spherical Linear Interpolation)
Smooth blend between models. Best for similar architectures.

### TIES (Task Arithmetic with Interference Elimination)
Smart merge that removes conflicting weights. Good for different tasks.

### DARE (Drop And REscale)
Advanced method that drops and rescales weights. Best for very different models.

### Linear
Simple weighted average. Reliable and predictable.

### Passthrough
Uses only the first model. No actual merging occurs.

---

## Output Formats

| Format | Description | Size Reduction |
|--------|-------------|----------------|
| gguf-2bit | Q2_K quantization | ~85% |
| gguf-4bit | Q4_K_M quantization (recommended) | ~70% |
| gguf-5bit | Q5_K_M quantization | ~60% |
| gguf-8bit | Q8_0 quantization | ~40% |
| gguf-f16 | Full F16 precision | 0% |
| safetensors | Original format | 0% |

---

## SDK Examples

### JavaScript/TypeScript
```typescript
import { mergeApi } from '@/lib/api';

// Create merge job
const response = await mergeApi.create({
  model_a: 'Qwen/Qwen2.5-7B-Instruct',
  model_b: 'meta-llama/Llama-3.1-8B-Instruct',
  method: 'slerp',
  ratio: 0.5,
  output_format: 'gguf-4bit',
  output_name: 'MyModel'
});

const jobId = response.data.job_id;

// Poll for status
const status = await mergeApi.status(jobId);
console.log(status.data.progress_percent);
```

### Python
```python
import requests

API_URL = "http://localhost:8000"

# Create merge job
response = requests.post(f"{API_URL}/api/merge", json={
    "model_a": "Qwen/Qwen2.5-7B-Instruct",
    "model_b": "meta-llama/Llama-3.1-8B-Instruct",
    "method": "slerp",
    "ratio": 0.5,
    "output_format": "gguf-4bit",
    "output_name": "MyModel"
})

job_id = response.json()["job_id"]

# Check status
status = requests.get(f"{API_URL}/api/merge/{job_id}/status")
print(status.json()["progress_percent"])

# Download when complete
download = requests.get(f"{API_URL}/api/merge/{job_id}/download")
with open("merged.gguf", "wb") as f:
    f.write(download.content)
```

---

## Webhooks (Coming Soon)

Subscribe to job status updates via webhooks.

```json
{
  "event": "merge.completed",
  "job_id": "abc12345",
  "timestamp": "2026-01-15T10:35:00Z",
  "data": {
    "output_name": "MyModel",
    "file_size": 4200000000,
    "sha256": "abc123..."
  }
}
```

---

*Built by intellectlabs | Founded by Kepler*
