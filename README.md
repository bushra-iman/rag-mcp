# Student Assistant RAG API

## Overview

Student Assistant RAG API is a Flask-based Retrieval-Augmented Generation (RAG) backend.

It stores uploaded documents in a FAISS vector database and answers questions using GPT-4.1-mini.

The agent supports:

- Local RAG tools
- Web search
- External MCP servers
- Dynamic MCP tool discovery
- Multiple MCP servers
- Dynamic MCP tool execution
- MCP tool-name collision handling
- MCP server refresh and removal

---

## Technologies

- Python
- Flask
- LangChain
- OpenAI GPT-4.1-mini
- OpenAI Embeddings
- FAISS
- DuckDuckGo Search
- MCP Python SDK
- Streamable HTTP

---

# Installation

Create a virtual environment:

```bash
python -m venv venv