import type { InferenceConfig, InferenceResult, ProgressCallback } from './runtime';

export class WebLLMInterface {
  private engine: any = null;
  private currentModelId: string | null = null;

  async loadModel(
    modelId: string,
    onProgress?: ProgressCallback
  ): Promise<void> {
    try {
      const { CreateMLCEngine } = await import('@mlc-ai/web-llm');
      
      onProgress?.({
        phase: 'downloading',
        percentage: 10,
        message: 'Initializing WebLLM engine...'
      });

      this.engine = await CreateMLCEngine(modelId, {
        initProgressCallback: (progress: any) => {
          const percentage = Math.round(progress.progress * 100);
          onProgress?.({
            phase: 'downloading',
            percentage,
            message: progress.text || `Downloading: ${percentage}%`
          });
        }
      });

      this.currentModelId = modelId;
      
      onProgress?.({
        phase: 'loading',
        percentage: 100,
        message: 'WebLLM model loaded successfully'
      });
    } catch (error) {
      console.error('WebLLM load error:', error);
      throw new Error(`Failed to load model with WebLLM: ${error}`);
    }
  }

  async generate(
    prompt: string,
    config: InferenceConfig,
    onProgress?: ProgressCallback
  ): Promise<InferenceResult> {
    if (!this.engine) {
      throw new Error('WebLLM engine not initialized');
    }

    const startTime = performance.now();

    onProgress?.({
      phase: 'generating',
      percentage: 0,
      message: 'Generating response...'
    });

    const completion = await this.engine.chat.completions.create({
      messages: [
        { role: 'user', content: prompt }
      ],
      max_tokens: config.maxTokens || 512,
      temperature: config.temperature || 0.7,
      top_p: config.topP || 0.9,
      stream: false
    });

    const endTime = performance.now();
    const text = completion.choices[0].message.content || '';
    const usage = completion.usage;

    const result: InferenceResult = {
      text,
      usage: {
        promptTokens: usage?.prompt_tokens || 0,
        completionTokens: usage?.completion_tokens || 0,
        totalTokens: usage?.total_tokens || 0
      },
      timings: {
        loadTime: 0,
        inferenceTime: endTime - startTime,
        tokensPerSecond: (usage?.completion_tokens || 0) / ((endTime - startTime) / 1000)
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
    return this.engine !== null && this.currentModelId === modelId;
  }

  async unloadModel(): Promise<void> {
    if (this.engine) {
      this.engine = null;
      this.currentModelId = null;
    }
  }
}
