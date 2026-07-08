import type { InferenceConfig, InferenceResult, ProgressCallback } from './runtime';

export class TransformersInterface {
  private pipeline: any = null;
  private currentModelId: string | null = null;

  async loadModel(
    modelId: string,
    onProgress?: ProgressCallback
  ): Promise<void> {
    try {
      const { pipeline } = await import('@xenova/transformers');
      
      onProgress?.({
        phase: 'downloading',
        percentage: 10,
        message: 'Initializing Transformers pipeline...'
      });

      this.pipeline = await pipeline('text-generation', modelId, {
        progress_callback: (progress: any) => {
          if (progress.status === 'progress') {
            const percentage = Math.round((progress.loaded / progress.total) * 100);
            onProgress?.({
              phase: 'downloading',
              percentage,
              message: `Downloading: ${percentage}%`
            });
          } else if (progress.status === 'done') {
            onProgress?.({
              phase: 'loading',
              percentage: 100,
              message: 'Transformers model loaded successfully'
            });
          }
        }
      });

      this.currentModelId = modelId;
    } catch (error) {
      console.error('Transformers load error:', error);
      throw new Error(`Failed to load model with Transformers: ${error}`);
    }
  }

  async generate(
    prompt: string,
    config: InferenceConfig,
    onProgress?: ProgressCallback
  ): Promise<InferenceResult> {
    if (!this.pipeline) {
      throw new Error('Transformers pipeline not initialized');
    }

    const startTime = performance.now();

    onProgress?.({
      phase: 'generating',
      percentage: 0,
      message: 'Generating response...'
    });

    const output = await this.pipeline(prompt, {
      max_new_tokens: config.maxTokens || 512,
      temperature: config.temperature || 0.7,
      top_p: config.topP || 0.9,
      do_sample: true,
      return_full_text: false
    });

    const endTime = performance.now();
    const text = Array.isArray(output) ? output[0]?.generated_text || '' : output.generated_text || '';
    const tokenCount = text.split(/\s+/).length;

    const result: InferenceResult = {
      text,
      usage: {
        promptTokens: prompt.split(/\s+/).length,
        completionTokens: tokenCount,
        totalTokens: prompt.split(/\s+/).length + tokenCount
      },
      timings: {
        loadTime: 0,
        inferenceTime: endTime - startTime,
        tokensPerSecond: tokenCount / ((endTime - startTime) / 1000)
      }
    };

    onProgress?.({
      phase: 'generating',
      percentage: 100,
      message: 'Generation complete'
    });

    return result;
  }

  isModelLoaded(modelId: string): boolean {
    return this.pipeline !== null && this.currentModelId === modelId;
  }

  async unloadModel(): Promise<void> {
    if (this.pipeline) {
      this.pipeline = null;
      this.currentModelId = null;
    }
  }
}
