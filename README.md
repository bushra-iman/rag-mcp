# 🎓 Student Assistant RAG API

A Flask-based **Retrieval-Augmented Generation (RAG)** backend that answers questions from uploaded documents using **GPT-4.1 mini**, with **web search** and **dynamic MCP tool integration**.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/bushra-iman/rag-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/bushra-iman/rag-mcp/actions)

---

## ✨ Features

- 📄 Upload **PDF / DOCX / TXT** documents and index them into a **FAISS vector store**
- 🧠 Answer questions with **GPT-4.1 mini** through a LangChain / LangGraph agent
- 🔎 Semantic search + exact-match lookup for `wmd-####` style IDs
- 🌐 **DuckDuckGo web search** fallback when documents don't have the answer
- 🔌 **Dynamic MCP integration** — register external MCP servers, discover their tools, and let the agent use them automatically
- 🧹 MCP tool-name **collision handling** (server-prefixed exposed names)
- 🔐 Optional **X-API-Key** authentication
- 💬 **Multi-tenant conversation memory** (SQLite + LangGraph checkpoints)
- 🎙️ **Voice queries** — FFmpeg preprocessing + OpenAI speech-to-text
- 🧪 pytest test suite + GitHub Actions CI

---

## 🏗️ Architecture

```
Client (Postman / App)
        │
        ▼
   Flask API  (port 5000)
   ├── /query, /ingest, /voice-query, /threads, /top5
   └── /api/mcp/*  (register external MCP servers)
        │
        ▼
   LangChain Agent (GPT-4.1 mini)
   ├── search_knowledge_base  ──► FAISS vector store
   ├── search_web_tool        ──► DuckDuckGo
   └── mcp_* (dynamic)        ──► external MCP servers
        │
        ▼
   LangGraph memory  ──► checkpoints.sqlite (per tenant/thread)
```

Also included:

- `mcp_server.py` — exposes the RAG tools as an **MCP server** (port 8000)
- `mock_oauth_server.py` — a mock OAuth2 token endpoint for testing MCP authentication (port 7000)

---

## 🚀 Quickstart

### 1. Clone & set up

```bash
git clone https://github.com/bushra-iman/rag-mcp.git
cd rag-mcp

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate  # macOS / Linux

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Then edit `.env` and set:

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key (required for RAG + speech-to-text) |
| `API_KEY` | Optional. If set, every endpoint except `/` and `/health` requires the `X-API-Key` header |
| `VECTOR_DB_PATH` | Path to the FAISS vector store (default `vector_store`) |

### 3. Run the API

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

### 4. Smoke test

```bash
curl http://localhost:5000/health
```

### 5. (Optional) Run the MCP server

```bash
python mcp_server.py
```

Exposes `search_uploaded_documents` and `search_web` as MCP tools at `http://localhost:8000/mcp`.

---

## 📚 API Reference

All requests and responses are JSON. If `API_KEY` is configured, send it as the `X-API-Key` header.

### Health & Info

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API info |
| `GET` | `/health` | Health check |

### RAG

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/query` | Ask a question |
| `POST` | `/ingest` | Upload documents (multipart `files`) |
| `POST` | `/voice-query` | Ask via audio (multipart `file` + `tenant_id`) |
| `GET` | `/threads?tenant_id=` | List conversation threads for a tenant |
| `GET` | `/top5?tenant_id=` | Most recent 5 conversations for a tenant |

### MCP management

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/mcp/servers` | Register an external MCP server |
| `GET` | `/api/mcp/servers` | List registered servers |
| `GET` | `/api/mcp/servers/<server_id>/tools` | List tools of one server |
| `POST` | `/api/mcp/servers/<server_id>/refresh` | Re-discover tools |
| `DELETE` | `/api/mcp/servers/<server_id>` | Remove a server |
| `GET` | `/api/mcp/tools` | List all local + MCP tools |

### Example: Ask a question

```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "question": "What is WMD-1234?",
    "tenant_id": "tenant-1",
    "thread_id": "default"
  }'
```

Response:

```json
{
  "answer": "WMD-1234 refers to ...",
  "sources": ["Student Knowledge Base", "MCP Tool: get_issue_details"],
  "tenant_id": "tenant-1",
  "thread_id": "default"
}
```

### Example: Upload documents

```bash
curl -X POST http://localhost:5000/ingest \
  -H "X-API-Key: your-api-key" \
  -F "files=@sample.pdf" \
  -F "files=@notes.docx"
```

### Example: Register an MCP server

```bash
curl -X POST http://localhost:5000/api/mcp/servers \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "name": "My MCP Server",
    "url": "http://localhost:8000/mcp",
    "authentication": {
      "type": "bearer",
      "token": "my-token"
    }
  }'
```

Supported `authentication` types:

- `bearer` — a static `token`
- `oauth2` — `client_credentials` grant with `token_endpoint`, `client_id`, `client_secret`

---

## 🔌 How MCP Integration Works

1. **Register** an external MCP server via `POST /api/mcp/servers`.
2. The client manager connects over **streamable HTTP**, initializes a session, and **discovers** every tool.
3. Tools are stored in a registry with **collision-safe names**: `mcp_<server>_<tool>` (a short server-id is appended if the name already exists).
4. Each MCP tool is converted into a **LangChain tool** (JSON schema → Pydantic model).
5. The agent picks MCP tools automatically when they fit the user's question.

---

## 🗂️ Project Structure

```
my_rag_api/
├── app.py                        # Flask entry point + app factory
├── config.py                     # Environment configuration
├── mcp_server.py                 # RAG tools exposed as an MCP server
├── mock_oauth_server.py          # Mock OAuth2 token endpoint for testing
├── routes/
│   ├── rag_routes.py             # /query, /ingest, /voice-query, /threads, /top5
│   └── mcp_routes.py             # /api/mcp/* endpoints
├── services/
│   ├── rag_engine.py             # Ingestion, retrieval, agent, ask_question
│   ├── agent_memory.py           # LangGraph SQLite checkpointer
│   ├── web_search.py             # DuckDuckGo wrapper
│   ├── audio_preprocessing.py    # FFmpeg audio pipeline
│   └── stt_service.py            # OpenAI speech-to-text
├── mcp_integration/
│   ├── client_manager.py         # Connect/discover/call external MCP servers
│   ├── tool_registry.py          # Collision-safe tool registry
│   ├── tool_adapter.py           # MCP tool → LangChain tool
│   └── authentication.py         # Bearer + OAuth2 headers
├── tests/                        # pytest suite
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── .github/workflows/ci.yml
```

---

## 🧪 Testing

```bash
pip install -r requirements-dev.txt
pytest
```

---

## 🛠️ Tech Stack

- **Python 3.12** · Flask · LangChain / LangGraph · OpenAI GPT-4.1 mini + Embeddings
- **FAISS** vector store · **SQLite** checkpoints · **DuckDuckGo** (`ddgs`)
- **MCP Python SDK** (streamable HTTP) · FFmpeg · pytest · GitHub Actions

---

## 📄 License

[MIT](LICENSE)