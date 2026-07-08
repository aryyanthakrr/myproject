import { WebLLMInterface } from './webllm';
import { TransformersInterface } from './transformers';

export interface ModelInfo {
  id: string;
  name: string;
  format: 'gguf' | 'safetensors' | 'onnx' | 'pytorch';
  size: number;
  quantization?: string;
  description: string;
}

export interface InferenceConfig {
  modelId: string;
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  stopSequences?: string[];
  stream?: boolean;
}

export interface InferenceResult {
  text: string;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  timings: {
    loadTime: number;
    inferenceTime: number;
    tokensPerSecond: number;
  };
}

export interface ProgressCallback {
  (progress: {
    phase: 'loading' | 'downloading' | 'processing' | 'generating';
    percentage: number;
    message: string;
  }): void;
}

export class NexusRuntime {
  private webllm: WebLLMInterface;
  private transformers: TransformersInterface;
  private currentModel: string | null = null;
  private isLoaded: boolean = false;

  constructor() {
    this.webllm = new WebLLMInterface();
    this.transformers = new TransformersInterface();
  }

  async initialize(): Promise<void> {
    console.log('Nexus Runtime initializing...');
    this.isLoaded = true;
  }

  async loadModel(
    modelId: string,
    onProgress?: ProgressCallback
  ): Promise<void> {
    if (!this.isLoaded) {
      await this.initialize();
    }

    onProgress?.({
      phase: 'loading',
      percentage: 0,
      message: `Loading model: ${modelId}`
    });

    try {
      if (modelId.includes('gguf') || modelId.includes('llama')) {
        await this.webllm.loadModel(modelId, onProgress);
      } else {
        await this.transformers.loadModel(modelId, onProgress);
      }
      
      this.currentModel = modelId;
      
      onProgress?.({
        phase: 'loading',
        percentage: 100,
        message: 'Model loaded successfully'
      });
    } catch (error) {
      console.error('Failed to load model:', error);
      throw error;
    }
  }

  async generate(
    prompt: string,
    config: InferenceConfig,
    onProgress?: ProgressCallback
  ): Promise<InferenceResult> {
    if (!this.currentModel) {
      throw new Error('No model loaded. Call loadModel() first.');
    }

    const startTime = performance.now();

    onProgress?.({
      phase: 'processing',
      percentage: 0,
      message: 'Processing prompt...'
    });

    let result: InferenceResult;

    try {
      if (this.webllm.isModelLoaded(this.currentModel)) {
        result = await this.webllm.generate(prompt, config, onProgress);
      } else {
        result = await this.transformers.generate(prompt, config, onProgress);
      }

      const endTime = performance.now();
      result.timings.inferenceTime = endTime - startTime;
      
      return result;
    } catch (error) {
      console.error('Generation failed:', error);
      throw error;
    }
  }

  async unloadModel(): Promise<void> {
    if (this.currentModel) {
      if (this.webllm.isModelLoaded(this.currentModel)) {
        await this.webllm.unloadModel();
      } else {
        await this.transformers.unloadModel();
      }
      this.currentModel = null;
    }
  }

  getSupportedFormats(): string[] {
    return ['gguf', 'safetensors', 'onnx', 'pytorch'];
  }

  getStatus(): {
    isReady: boolean;
    currentModel: string | null;
    memoryUsage?: number;
  } {
    return {
      isReady: this.isLoaded,
      currentModel: this.currentModel,
      memoryUsage: typeof performance !== 'undefined' && 
                   (performance as any).memory 
        ? (performance as any).memory.usedJSHeapSize 
        : undefined
    };
  }
}

export const nexusRuntime = new NexusRuntime();
