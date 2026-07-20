# MergeLab - One-Click AI Model Merging Platform

**Built by [intellectlabs](https://intellectlabs.ai) | Founded by Kepler**

MergeLab is a production-grade web application that allows users to merge two AI models with a single click. Select models, choose a merge method, and get a merged model ready to download or deploy.

## Features

- 🔀 **5 Merge Methods**: SLERP, TIES, DARE, Linear, Passthrough
- 📦 **GGUF Export**: Quantize to 2-bit, 4-bit, 5-bit, 8-bit, or f16
- 🌐 **HuggingFace Integration**: Push merged models directly to HF Hub
- 🧪 **Model Testing**: Chat with your merged model before downloading
- 🚀 **API Deployment**: Deploy merged models as REST APIs
- 🔐 **SHA-256 Verification**: Integrity certificates for all downloads
- 📊 **Dashboard**: Track merge history and manage storage

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 + TypeScript + Tailwind CSS |
| Backend | Python FastAPI |
| Merge Engine | mergekit |
| Quantization | llama.cpp (GGUF) |
| Database | SQLite |
| Auth | NextAuth.js (GitHub + Google) |
| Payment | Razorpay |
| Deploy | Vercel (frontend) + Railway (backend) |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)

### Local Development

```bash
# Clone the repository
cd mergelab

# Start backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Docker Deployment

```bash
docker-compose up --build
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Supported Models

MergeLab supports 50+ popular models including:

- **Qwen2.5**: 0.5B, 1.5B, 3B, 7B, 14B, 32B, 72B
- **Llama-3.1**: 8B, 70B
- **Mistral**: 7B
- **Phi-3/4**: 3.8B, 14B
- **Gemma-2**: 2B, 9B, 27B
- **Yi-1.5**: 6B, 9B, 34B

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/merge` | Create a new merge job |
| GET | `/api/merge/{job_id}/status` | Get merge progress |
| GET | `/api/merge/{job_id}/download` | Download merged model |
| POST | `/api/merge/{job_id}/test` | Test merged model |
| POST | `/api/merge/{job_id}/deploy` | Deploy as API |
| POST | `/api/merge/{job_id}/push-hf` | Push to HuggingFace |
| GET | `/api/models` | List available models |
| GET | `/api/health` | System health check |

## Configuration

### Environment Variables

**Backend (.env)**
```bash
HF_TOKEN=your_huggingface_token
DATABASE_URL=sqlite:///./mergelab.db
STORAGE_PATH=./storage
MAX_FILE_SIZE=50GB
RATE_LIMIT_FREE=5
RATE_LIMIT_PRO=unlimited
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
NEXTAUTH_SECRET=your_nextauth_secret
```

**Frontend (.env.local)**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_nextauth_secret
GITHUB_ID=your_github_oauth_id
GITHUB_SECRET=your_github_oauth_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

## License

MIT License - Built by intellectlabs © 2026

---

*Made with ❤️ by Kepler and the intellectlabs team*
