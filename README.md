<div align="center">

# 🤖 HRAgent

**An intelligent HR policy Q&A system powered by LangChain Agent + RAG**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-4f46e5)](https://deepseek.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

[简体中文](./README_ZH.md) | English

</div>

---

## ✨ Features

- 📄 **Document Management** — Upload PDF / Markdown / TXT HR documents
- 🔍 **RAG Retrieval** — BGE Chinese Embedding + Milvus vector search for precise document matching
- 🤖 **Intelligent Q&A** — DeepSeek LLM answers HR policy questions grounded in retrieved documents
- 💬 **Streaming Chat** — Real-time SSE streaming responses
- 📝 **Session Management** — Create, switch, and delete chat sessions with full history
- 🎨 **Modern UI** — Dark theme, Markdown rendering, responsive design

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | DeepSeek (`deepseek-chat`) |
| **Agent** | LangChain |
| **Embedding** | BAAI/bge-small-zh-v1.5 |
| **Vector DB** | Milvus Standalone |
| **Database** | PostgreSQL 16 |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | Next.js · Shadcn/ui · TailwindCSS |
| **Deployment** | Docker Compose (6 services) |

## 📋 System Requirements

|  | Minimum | Recommended |
|------|---------|-------------|
| **CPU** | 2 Cores | 4 Cores |
| **RAM** | 8 GB | 16 GB |
| **Disk** | 30 GB SSD | 50 GB SSD |
| **OS** | Linux (Ubuntu 20.04+) | — |
| **Dependencies** | Docker · Docker Compose | — |
| **Network** | Internet access (image pulls + DeepSeek API) | — |

> [!WARNING]
> Milvus requires ~2.5 GB and the BGE Embedding model ~1.5 GB. A minimum of **6–7 GB available RAM** is needed. Machines with 4 GB or less **cannot** run this project.

<details>
<summary>Per-service memory breakdown</summary>

| Service | Memory |
|---------|--------|
| Milvus Standalone | ~2 GB |
| etcd + MinIO | ~512 MB |
| PostgreSQL | ~256 MB |
| FastAPI + BGE Embedding | ~2–3 GB |
| Next.js Frontend | ~256 MB |

</details>

## 🚀 Quick Start

### 1. Configure

```bash
cp .env.example .env
```

Edit `.env` and set your DeepSeek API key:

```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
```

### 2. Launch

```bash
docker-compose up -d
```

> First launch downloads the BGE Embedding model (~90 MB). This may take a few minutes.

```bash
docker-compose ps   # Verify all 6 services are running
```

### 3. Import Sample Data

```bash
docker-compose exec backend python /app/scripts/init_data.py
```

### 4. Open the App

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send message (sync) |
| `POST` | `/api/chat/stream` | Send message (SSE stream) |
| `GET` | `/api/chat/sessions` | List sessions |
| `GET` | `/api/chat/sessions/{id}/messages` | Get session history |
| `DELETE` | `/api/chat/sessions/{id}` | Delete session |
| `POST` | `/api/documents/upload` | Upload document |
| `GET` | `/api/documents` | List documents |
| `DELETE` | `/api/documents/{id}` | Delete document |

## 📁 Project Structure

```
HRAgent/
├── backend/                # FastAPI Backend
│   └── app/
│       ├── api/            #   API routes (chat, documents)
│       ├── models/         #   SQLAlchemy models
│       ├── schemas/        #   Pydantic schemas
│       ├── services/       #   Agent · RAG · Embedding · Milvus
│       └── utils/          #   PDF parser
├── frontend/               # Next.js Frontend
│   ├── app/                #   Pages & layout
│   ├── components/ui/      #   Shadcn/ui components
│   └── lib/                #   API client
├── data/sample/            # Sample HR documents
├── scripts/                # Data init script
├── docker-compose.yml      # 6-service orchestration
└── .env.example            # Environment template
```

## 🛑 Stop Services

```bash
docker-compose down        # Stop containers
docker-compose down -v     # Stop + remove data volumes
```
