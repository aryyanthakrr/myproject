import { useState, useCallback } from 'react';
import { nexusRuntime, type InferenceConfig, type InferenceResult, type ProgressCallback } from '../lib/runtime';

interface UseInferenceReturn {
  isGenerating: boolean;
  result: InferenceResult | null;
  progress: number;
  statusMessage: string;
  error: string | null;
  generate: (prompt: string, config?: Partial<InferenceConfig>) => Promise<void>;
  clearResult: () => void;
}

export function useInference(): UseInferenceReturn {
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<InferenceResult | null>(null);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState<string | null>(null);

  const generate = useCallback(async (
    prompt: string,
    config?: Partial<InferenceConfig>
  ) => {
    setIsGenerating(true);
    setError(null);
    setResult(null);
    setProgress(0);
    setStatusMessage('Processing...');

    const onProgress: ProgressCallback = (progressData) => {
      setProgress(progressData.percentage);
      setStatusMessage(progressData.message);
    };

    try {
      const inferenceConfig: InferenceConfig = {
        modelId: '',
        maxTokens: 512,
        temperature: 0.7,
        topP: 0.9,
        stream: false,
        ...config
      };

      const inferenceResult = await nexusRuntime.generate(prompt, inferenceConfig, onProgress);
      setResult(inferenceResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
    } finally {
      setIsGenerating(false);
    }
  }, []);

  const clearResult = useCallback(() => {
    setResult(null);
    setProgress(0);
    setStatusMessage('');
    setError(null);
  }, []);

  return {
    isGenerating,
    result,
    progress,
    statusMessage,
    error,
    generate,
    clearResult
  };
}
