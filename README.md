# Palm Mind RAG API

FastAPI backend with two REST APIs:
1. **Document Ingestion**: upload .pdf/.txt, extract text, chunk (fixed or recursive), embed, store in Qdrant, save metadata in SQLite.
2. **Conversational RAG**: custom RAG (no RetrievalQAChain), Redis chat memory, multi-turn queries, interview booking via LLM.

## Setup
```
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
Create a `.env` file:
```
OPENAI_API_KEY=your-key-here
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
CHAT_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIM=3072
REDIS_URL=redis://default:password@host:port
```
Works with any OpenAI-compatible provider (OpenAI, Gemini, Ollama) by changing the base URL and model names.

## Run
```
uvicorn app.main:app
```
Open http://127.0.0.1:8000/docs

## Endpoints
- `POST /api/v1/documents/upload`: multipart form with `file` and `chunking_strategy` (`fixed` | `recursive`)
- `POST /api/v1/chat`: `{"session_id": "abc", "message": "..."}`
- `GET /health`

## Design
- `api/`: HTTP layer, `services/`: business logic, `schemas/`: Pydantic models, `database/`: SQLAlchemy models, `core/`: settings.
- Vector DB: Qdrant (local on-disk or remote). Metadata and bookings: SQLite. Chat memory: Redis.