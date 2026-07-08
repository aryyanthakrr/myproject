import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface ModelLoaderProps {
  isLoading: boolean;
  isLoaded: boolean;
  progress: number;
  statusMessage: string;
  error: string | null;
  onLoadModel: (modelId: string) => void;
  onUnloadModel: () => void;
}

const PREDEFINED_MODELS = [
  { id: 'Llama-3.2-1B-Instruct-q4f32_1-MLC', name: 'Llama 3.2 1B Instruct', description: 'Fast & lightweight' },
  { id: 'Llama-3.1-8B-Instruct-q4f32_1-MLC', name: 'Llama 3.1 8B Instruct', description: 'Balanced performance' },
  { id: 'Phi-3.5-mini-instruct-q4f32_1-MLC', name: 'Phi-3.5 Mini', description: 'Microsoft\'s efficient model' },
];

export function ModelLoader({
  isLoading,
  isLoaded,
  progress,
  statusMessage,
  error,
  onLoadModel,
  onUnloadModel
}: ModelLoaderProps) {
  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
          Load AI Model
        </h2>

        {!isLoaded ? (
          <>
            <div className="space-y-4 mb-6">
              {PREDEFINED_MODELS.map((model) => (
                <motion.button
                  key={model.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => onLoadModel(model.id)}
                  disabled={isLoading}
                  className="w-full p-4 text-left border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="font-semibold text-gray-900 dark:text-white">
                    {model.name}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {model.description}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    {model.id}
                  </div>
                </motion.button>
              ))}
            </div>

            <AnimatePresence>
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="space-y-2"
                >
                  <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>{statusMessage}</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${progress}%` }}
                      className="h-full bg-blue-500"
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-2 text-red-600 dark:text-red-400 mt-4"
              >
                <AlertCircle className="w-5 h-5" />
                <span>{error}</span>
              </motion.div>
            )}
          </>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center justify-between"
          >
            <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
              <CheckCircle className="w-6 h-6" />
              <span className="font-semibold">Model loaded successfully</span>
            </div>
            <button
              onClick={onUnloadModel}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              Unload Model
            </button>
          </motion.div>
        )}
      </div>
    </div>
  );
}
