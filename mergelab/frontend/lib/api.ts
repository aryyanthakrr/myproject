import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Models API
export const modelsApi = {
  list: (params?: { category?: string; family?: string; search?: string }) =>
    api.get('/api/models', { params }),
  
  families: () => api.get('/api/models/families'),
  
  popular: () => api.get('/api/models/popular'),
};

// Merge API
export const mergeApi = {
  create: (data: {
    model_a: string;
    model_b: string;
    method: string;
    ratio: number;
    output_format: string;
    output_name: string;
  }) => api.post('/api/merge', data),
  
  status: (jobId: string) => api.get(`/api/merge/${jobId}/status`),
  
  download: (jobId: string) => `${API_URL}/api/merge/${jobId}/download`,
  
  test: (jobId: string, prompt: string, maxTokens = 256, temperature = 0.7) =>
    api.post(`/api/merge/${jobId}/test`, { prompt, max_tokens: maxTokens, temperature }),
  
  deploy: (jobId: string, deployName?: string, expiresInDays = 7) =>
    api.post(`/api/merge/${jobId}/deploy`, { deploy_name: deployName, expires_in_days: expiresInDays }),
  
  pushToHF: (jobId: string, repoId: string, token: string, privateRepo = false) =>
    api.post(`/api/merge/${jobId}/push-hf`, { repo_id: repoId, token, private: privateRepo }),
};

// Health API
export const healthApi = {
  check: () => api.get('/api/health'),
};

// Types
export interface Model {
  id: string;
  name: string;
  parameters: string;
  size_gb: number;
  license: string;
  downloads: number;
  family: string;
  category: 'slm' | 'medium' | 'large';
  tags: string[];
}

export interface ModelsListResponse {
  models: Model[];
  total: number;
  categories: Record<string, number>;
}

export interface MergeJob {
  job_id: string;
  status: string;
  progress_percent: number;
  current_step: string;
  eta_seconds?: number;
  error_message?: string;
}

export interface MergeResult {
  job_id: string;
  status: string;
  output_name: string;
  file_size: number;
  file_size_human: string;
  sha256_hash: string;
  output_path: string;
  download_url: string;
  format: string;
  model_a: string;
  model_b: string;
  method: string;
  ratio: number;
}

export interface TestResponse {
  response: string;
  latency_ms: number;
  tokens_generated: number;
  tokens_per_second: number;
}

export interface DeployResponse {
  deploy_id: string;
  api_url: string;
  api_key: string;
  expires_at: string;
  status: string;
}

export interface HFPushResponse {
  success: boolean;
  hf_url: string;
  message: string;
}

export interface HealthStatus {
  status: string;
  version: string;
  gpu_available: boolean;
  disk_space_gb: number;
  disk_free_gb: number;
  active_jobs: number;
  models_cached: number;
  uptime_seconds: number;
}
