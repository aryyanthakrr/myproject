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

export interface MergeMethod {
  id: string;
  name: string;
  description: string;
  recommended: boolean;
}

export interface MergeConfig {
  model_a: string;
  model_b: string;
  method: string;
  ratio: number;
  output_format: string;
  output_name: string;
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

export const MERGE_METHODS: MergeMethod[] = [
  {
    id: 'slerp',
    name: 'SLERP',
    description: 'Smooth spherical interpolation. Best for similar models.',
    recommended: true,
  },
  {
    id: 'ties',
    name: 'TIES',
    description: 'Task arithmetic with interference elimination. Smart merge that removes conflicts.',
    recommended: false,
  },
  {
    id: 'dare',
    name: 'DARE',
    description: 'Drop And REscale. Advanced method best for different models.',
    recommended: false,
  },
  {
    id: 'linear',
    name: 'Linear',
    description: 'Simple weighted average. Reliable and predictable.',
    recommended: false,
  },
  {
    id: 'passthrough',
    name: 'Passthrough',
    description: 'Use only the first model. No actual merging.',
    recommended: false,
  },
];

export const OUTPUT_FORMATS = [
  { id: 'gguf-4bit', name: 'GGUF 4-bit (Recommended)', description: 'Best balance of quality and size' },
  { id: 'gguf-8bit', name: 'GGUF 8-bit', description: 'Higher quality, larger file' },
  { id: 'gguf-5bit', name: 'GGUF 5-bit', description: 'Good middle ground' },
  { id: 'gguf-2bit', name: 'GGUF 2-bit', description: 'Smallest size, some quality loss' },
  { id: 'gguf-f16', name: 'GGUF F16', description: 'Full precision, largest file' },
  { id: 'safetensors', name: 'Safetensors', description: 'Original format, no quantization' },
];
