# HRAgent — HR 智能问答系统

[English](./README_EN.md) | 中文

基于 LangChain Agent + RAG 的员工手册与 HR 政策智能问答系统。

## 技术栈

| 组件 | 技术 |
|------|------|
| LLM | DeepSeek (deepseek-chat) |
| Agent 框架 | LangChain |
| Embedding | BAAI/bge-small-zh-v1.5 |
| 向量数据库 | Milvus |
| 关系数据库 | PostgreSQL |
| 后端 API | FastAPI |
| 前端 | Next.js + Shadcn/ui + TailwindCSS |
| 部署 | Docker Compose |

## 功能特性

- 📄 **文档管理**：支持上传 PDF / Markdown / TXT 格式的 HR 文档
- 🔍 **RAG 检索**：基于 BGE 中文 Embedding + Milvus 向量检索，精准匹配相关文档段落
- 🤖 **智能问答**：DeepSeek LLM 根据检索到的文档内容，专业回答 HR 政策问题
- 💬 **流式对话**：SSE 流式输出，实时显示回答内容
- 📝 **会话管理**：支持多会话创建、切换、删除，保存对话历史
- 🎨 **现代化 UI**：暗色主题，Markdown 渲染，响应式设计

## 服务器配置要求

|  | 最低配置 | 推荐配置 |
|------|---------|---------|
| **CPU** | 2 核 | 4 核 |
| **内存** | 8 GB | 16 GB |
| **磁盘** | 30 GB SSD | 50 GB SSD |
| **系统** | Linux (Ubuntu 20.04+) | — |
| **依赖** | Docker + Docker Compose | — |
| **网络** | 需要互联网访问（拉取镜像 + DeepSeek API 调用） | — |

> ⚠️ **内存说明**：Milvus 向量数据库约需 2.5 GB，BGE Embedding 模型加载约需 1.5 GB，合计最低需要 **6-7 GB** 可用内存。4 GB 及以下配置无法正常运行。

<details>
<summary>各服务内存占用明细</summary>

| 服务 | 内存占用 |
|------|---------|
| Milvus Standalone | ~2 GB |
| etcd | ~256 MB |
| MinIO | ~256 MB |
| PostgreSQL | ~256 MB |
| FastAPI + BGE Embedding | ~2-3 GB |
| Next.js 前端 | ~256 MB |

</details>

## 快速启动

### 1. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 DeepSeek API Key：

```
DEEPSEEK_API_KEY=your-actual-api-key
```

### 2. 启动服务

```bash
docker-compose up -d
```

等待所有容器启动完成（首次启动需要下载 Embedding 模型，可能需要几分钟）：

```bash
docker-compose ps
```

### 3. 导入示例数据

```bash
docker-compose exec backend python /app/scripts/init_data.py
```

### 4. 访问系统

- **前端界面**：http://localhost:3000
- **API 文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | 发送消息（同步） |
| POST | `/api/chat/stream` | 发送消息（SSE 流式） |
| GET | `/api/chat/sessions` | 获取会话列表 |
| GET | `/api/chat/sessions/{id}/messages` | 获取会话历史 |
| DELETE | `/api/chat/sessions/{id}` | 删除会话 |
| POST | `/api/documents/upload` | 上传文档 |
| GET | `/api/documents` | 文档列表 |
| DELETE | `/api/documents/{id}` | 删除文档 |

## 项目结构

```
HRAgent/
├── backend/            # FastAPI 后端
│   └── app/
│       ├── api/        # API 路由
│       ├── models/     # 数据库模型
│       ├── schemas/    # Pydantic 模型
│       ├── services/   # 业务逻辑（Agent, RAG, Embedding, Milvus）
│       └── utils/      # 工具（PDF 解析）
├── frontend/           # Next.js 前端
│   ├── app/            # 页面
│   ├── components/     # Shadcn/ui 组件
│   └── lib/            # API 客户端
├── data/sample/        # 示例 HR 文档
├── scripts/            # 数据初始化脚本
└── docker-compose.yml
```

## 停止服务

```bash
docker-compose down        # 停止容器
docker-compose down -v     # 停止并删除数据卷
```
