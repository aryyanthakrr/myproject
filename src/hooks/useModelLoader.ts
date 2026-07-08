import { useState, useCallback } from 'react';
import { nexusRuntime, type InferenceConfig, type ProgressCallback } from '../lib/runtime';

interface UseModelLoaderReturn {
  isLoading: boolean;
  isLoaded: boolean;
  progress: number;
  statusMessage: string;
  error: string | null;
  loadModel: (modelId: string) => Promise<void>;
  unloadModel: () => Promise<void>;
}

export function useModelLoader(): UseModelLoaderReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState<string | null>(null);

  const loadModel = useCallback(async (modelId: string) => {
    setIsLoading(true);
    setError(null);
    setProgress(0);
    setStatusMessage('Initializing...');

    const onProgress: ProgressCallback = (progressData) => {
      setProgress(progressData.percentage);
      setStatusMessage(progressData.message);
    };

    try {
      await nexusRuntime.loadModel(modelId, onProgress);
      setIsLoaded(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load model');
      setIsLoaded(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const unloadModel = useCallback(async () => {
    await nexusRuntime.unloadModel();
    setIsLoaded(false);
    setProgress(0);
    setStatusMessage('Model unloaded');
  }, []);

  return {
    isLoading,
    isLoaded,
    progress,
    statusMessage,
    error,
    loadModel,
    unloadModel
  };
}
