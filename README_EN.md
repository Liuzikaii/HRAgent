# HRAgent — HR Intelligent Q&A System

[中文](./README.md) | English

An intelligent employee handbook and HR policy Q&A system powered by LangChain Agent + RAG.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | DeepSeek (deepseek-chat) |
| Agent Framework | LangChain |
| Embedding | BAAI/bge-small-zh-v1.5 |
| Vector Database | Milvus |
| Relational Database | PostgreSQL |
| Backend API | FastAPI |
| Frontend | Next.js + Shadcn/ui + TailwindCSS |
| Deployment | Docker Compose |

## Features

- 📄 **Document Management** — Upload PDF / Markdown / TXT HR documents
- 🔍 **RAG Retrieval** — BGE Chinese Embedding + Milvus vector search for precise document matching
- 🤖 **Intelligent Q&A** — DeepSeek LLM answers HR policy questions based on retrieved documents
- 💬 **Streaming Chat** — Real-time SSE streaming responses
- 📝 **Session Management** — Create, switch, and delete multiple chat sessions with history
- 🎨 **Modern UI** — Dark theme, Markdown rendering, responsive design

## System Requirements

|  | Minimum | Recommended |
|------|---------|-------------|
| **CPU** | 2 Cores | 4 Cores |
| **RAM** | 8 GB | 16 GB |
| **Disk** | 30 GB SSD | 50 GB SSD |
| **OS** | Linux (Ubuntu 20.04+) | — |
| **Dependencies** | Docker + Docker Compose | — |
| **Network** | Internet access required (pulling images + DeepSeek API calls) | — |

> ⚠️ **Memory Note**: Milvus requires ~2.5 GB and the BGE Embedding model requires ~1.5 GB to load. A minimum of **6–7 GB** available memory is needed. Machines with 4 GB or less cannot run this project.

<details>
<summary>Per-service memory breakdown</summary>

| Service | Memory Usage |
|---------|-------------|
| Milvus Standalone | ~2 GB |
| etcd | ~256 MB |
| MinIO | ~256 MB |
| PostgreSQL | ~256 MB |
| FastAPI + BGE Embedding | ~2–3 GB |
| Next.js Frontend | ~256 MB |

</details>

## Quick Start

### 1. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your DeepSeek API Key:

```
DEEPSEEK_API_KEY=your-actual-api-key
```

### 2. Start Services

```bash
docker-compose up -d
```

Wait for all containers to start (first launch downloads the Embedding model, which may take a few minutes):

```bash
docker-compose ps
```

### 3. Import Sample Data

```bash
docker-compose exec backend python /app/scripts/init_data.py
```

### 4. Access the System

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat` | Send a message (sync) |
| POST | `/api/chat/stream` | Send a message (SSE streaming) |
| GET | `/api/chat/sessions` | List chat sessions |
| GET | `/api/chat/sessions/{id}/messages` | Get session history |
| DELETE | `/api/chat/sessions/{id}` | Delete a session |
| POST | `/api/documents/upload` | Upload a document |
| GET | `/api/documents` | List documents |
| DELETE | `/api/documents/{id}` | Delete a document |

## Project Structure

```
HRAgent/
├── backend/            # FastAPI Backend
│   └── app/
│       ├── api/        # API Routes
│       ├── models/     # Database Models
│       ├── schemas/    # Pydantic Schemas
│       ├── services/   # Business Logic (Agent, RAG, Embedding, Milvus)
│       └── utils/      # Utilities (PDF Parsing)
├── frontend/           # Next.js Frontend
│   ├── app/            # Pages
│   ├── components/     # Shadcn/ui Components
│   └── lib/            # API Client
├── data/sample/        # Sample HR Documents
├── scripts/            # Data Initialization Scripts
└── docker-compose.yml
```

## Stop Services

```bash
docker-compose down        # Stop containers
docker-compose down -v     # Stop and remove data volumes
```
