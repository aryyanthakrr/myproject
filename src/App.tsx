import { useState } from 'react';
import { motion } from 'framer-motion';
import { Moon, Sun, Cpu, Zap, Layers, Github } from 'lucide-react';
import { useModelLoader } from './hooks/useModelLoader';
import { useInference } from './hooks/useInference';
import { ModelLoader } from './components/ModelLoader';
import { ChatInterface } from './components/ChatInterface';

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const modelLoader = useModelLoader();
  const inference = useInference();

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${darkMode ? 'dark' : ''}`}>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        {/* Header */}
        <header className="sticky top-0 z-50 backdrop-blur-lg bg-white/80 dark:bg-gray-900/80 border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-3">
                <motion.div
                  initial={{ rotate: -180, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  transition={{ duration: 0.5 }}
                >
                  <Cpu className="w-8 h-8 text-blue-500" />
                </motion.div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                    Nexus AI Runtime
                  </h1>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    Enterprise Local Inference Engine
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="hidden md:flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center gap-1">
                    <Zap className="w-4 h-4" />
                    <span>Fast</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Layers className="w-4 h-4" />
                    <span>Multi-format</span>
                  </div>
                  <a
                    href="#"
                    className="flex items-center gap-1 hover:text-blue-500 transition-colors"
                  >
                    <Github className="w-4 h-4" />
                    <span>Open Source</span>
                  </a>
                </div>

                <button
                  onClick={toggleDarkMode}
                  className="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                >
                  {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Hero Section */}
          {!modelLoader.isLoaded && !modelLoader.isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center mb-12"
            >
              <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
                Run AI Models Locally
              </h2>
              <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                Enterprise-grade runtime supporting multiple formats (GGUF, Safetensors, ONNX, PyTorch) with blazing fast inference on your local machine.
              </p>
            </motion.div>
          )}

          {/* Model Loader */}
          <ModelLoader
            isLoading={modelLoader.isLoading}
            isLoaded={modelLoader.isLoaded}
            progress={modelLoader.progress}
            statusMessage={modelLoader.statusMessage}
            error={modelLoader.error}
            onLoadModel={modelLoader.loadModel}
            onUnloadModel={modelLoader.unloadModel}
          />

          {/* Chat Interface */}
          {modelLoader.isLoaded && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mt-8"
            >
              <ChatInterface
                isGenerating={inference.isGenerating}
                result={inference.result}
                progress={inference.progress}
                statusMessage={inference.statusMessage}
                error={inference.error}
                onGenerate={inference.generate}
                onClear={inference.clearResult}
              />
            </motion.div>
          )}

          {/* Features Grid */}
          {!modelLoader.isLoaded && !modelLoader.isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6"
            >
              {[
                {
                  icon: Zap,
                  title: 'Lightning Fast',
                  description: 'Optimized inference engine with hardware acceleration support for maximum performance.'
                },
                {
                  icon: Layers,
                  title: 'Multi-Format Support',
                  description: 'Run models in GGUF, Safetensors, ONNX, and PyTorch formats seamlessly.'
                },
                {
                  icon: Cpu,
                  title: 'Local Execution',
                  description: 'Complete privacy with all inference running locally on your machine.'
                }
              ].map((feature, index) => (
                <motion.div
                  key={feature.title}
                  whileHover={{ scale: 1.05 }}
                  className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg"
                >
                  <feature.icon className="w-12 h-12 text-blue-500 mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    {feature.description}
                  </p>
                </motion.div>
              ))}
            </motion.div>
          )}
        </main>

        {/* Footer */}
        <footer className="mt-16 border-t border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center text-gray-600 dark:text-gray-400">
              <p>Built with ❤️ for the open-source community</p>
              <p className="text-sm mt-2">Nexus AI Runtime © 2024</p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
