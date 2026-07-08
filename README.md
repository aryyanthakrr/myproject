# Nexus AI Runtime

<div align="center">

![Nexus AI Runtime](https://img.shields.io/badge/Nexus-AI%20Runtime-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue)
![React](https://img.shields.io/badge/React-18.2-blue)

**Enterprise-grade open-source AI runtime for local model inference**

</div>

---

## ✨ Features

- 🚀 **Lightning Fast** - Optimized inference engine with hardware acceleration
- 🔒 **Privacy First** - All inference runs locally on your machine
- 📦 **Multi-Format Support** - GGUF, Safetensors, ONNX, PyTorch
- 🎨 **Beautiful UI** - Clean, modern interface with smooth animations
- 🌙 **Dark Mode** - Easy on the eyes for extended use
- ⚡ **Real-time Progress** - Live feedback during model loading and generation
- 📊 **Performance Metrics** - Tokens/second, timing, and usage statistics

## 🏗️ Architecture

```
Nexus AI Runtime
├── Core Runtime (runtime.ts)
│   ├── WebLLM Interface (webllm.ts)
│   └── Transformers Interface (transformers.ts)
├── React Hooks
│   ├── useModelLoader
│   └── useInference
└── UI Components
    ├── ModelLoader
    └── ChatInterface
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd nexus-ai-runtime

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 💻 Usage

### Loading a Model

```typescript
import { nexusRuntime } from './lib/runtime';

// Load a model
await nexusRuntime.loadModel('Llama-3.2-1B-Instruct-q4f32_1-MLC', (progress) => {
  console.log(`${progress.phase}: ${progress.percentage}% - ${progress.message}`);
});

// Generate text
const result = await nexusRuntime.generate(
  'Explain quantum computing',
  {
    maxTokens: 512,
    temperature: 0.7,
    topP: 0.9
  }
);

console.log(result.text);
console.log(`Generated at ${result.timings.tokensPerSecond.toFixed(2)} tokens/s`);
```

### Using React Hooks

```tsx
import { useModelLoader } from './hooks/useModelLoader';
import { useInference } from './hooks/useInference';

function MyComponent() {
  const { isLoaded, loadModel } = useModelLoader();
  const { generate, result } = useInference();

  return (
    <div>
      {!isLoaded ? (
        <button onClick={() => loadModel('model-id')}>Load Model</button>
      ) : (
        <button onClick={() => generate('Your prompt here')}>
          Generate
        </button>
      )}
      {result && <div>{result.text}</div>}
    </div>
  );
}
```

## 🛠️ API Reference

### NexusRuntime

| Method | Description |
|--------|-------------|
| `initialize()` | Initialize the runtime |
| `loadModel(modelId, onProgress)` | Load a model by ID |
| `generate(prompt, config, onProgress)` | Generate text from a prompt |
| `unloadModel()` | Unload the current model |
| `getSupportedFormats()` | Get list of supported formats |
| `getStatus()` | Get runtime status |

### InferenceConfig

```typescript
interface InferenceConfig {
  modelId: string;
  maxTokens?: number;      // Default: 512
  temperature?: number;    // Default: 0.7
  topP?: number;          // Default: 0.9
  stopSequences?: string[];
  stream?: boolean;       // Default: false
}
```

### InferenceResult

```typescript
interface InferenceResult {
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
```

## 📦 Supported Model Formats

| Format | Backend | Example Models |
|--------|---------|----------------|
| GGUF | WebLLM | Llama 3, Phi-3, Mistral |
| Safetensors | Transformers | BERT, GPT-2 |
| ONNX | Transformers | Various ONNX models |
| PyTorch | Transformers | PyTorch native models |

## 🎨 Customization

### Theme Colors

Edit `src/index.css` to customize the color scheme:

```css
:root {
  --primary: 240 5.9% 10%;
  --background: 0 0% 100%;
  /* ... other variables */
}
```

### Adding New Models

Add your model to the `PREDEFINED_MODELS` array in `src/components/ModelLoader.tsx`:

```typescript
const PREDEFINED_MODELS = [
  {
    id: 'your-model-id',
    name: 'Your Model Name',
    description: 'Model description'
  },
  // ... more models
];
```

## 🔧 Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Format code
npm run format
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [WebLLM](https://github.com/mlc-ai/web-llm) - WebGPU-accelerated LLM inference
- [Transformers.js](https://github.com/xenova/transformers.js) - ML in the browser
- [Framer Motion](https://www.framer.com/motion/) - Smooth animations
- [Lucide Icons](https://lucide.dev/) - Beautiful icons

---

<div align="center">

**Built with ❤️ for the open-source community**

[Nexus AI Runtime](https://github.com/nexus-ai/runtime)

</div>