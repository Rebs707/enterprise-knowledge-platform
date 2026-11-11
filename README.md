# Enterprise Knowledge Platform

A local-first enterprise document intelligence platform. The current milestone implements secure, bounded document ingestion, text chunking, persistent metadata/chunk storage, and keyword retrieval behind a FastAPI service.

## Implemented in the current release

- Upload UTF-8 plain-text (`.txt`) and Markdown (`.md`) documents.
- Enforce a 2 MiB upload limit and reject unsupported formats or invalid UTF-8.
- Split content into overlapping chunks for retrieval.
- Persist document metadata, SHA-256 digests, and chunks in SQLite.
- Search indexed chunks using deterministic, case-insensitive keyword scoring.
- Retrieve document metadata by document ID.
- Run locally or in Docker.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/documents` | Upload and index a `.txt` or `.md` file (multipart field: `file`) |
| GET | `/documents/{document_id}` | Retrieve document metadata |
| GET | `/search?q={query}&limit=10` | Search indexed document chunks |
| GET | `/knowledge/{topic}` | Compatibility alias for keyword search |
| GET | `/health` | Application health |

Interactive API documentation is available at `/docs` when the service is running.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The SQLite database defaults to `data/knowledge.db`. Override its location with the `EKP_DB_PATH` environment variable.

## Run tests

```bash
pytest -q
```

## Docker

```bash
docker build -t enterprise-knowledge-platform .
docker run --rm -p 8000:8000 -v ekp-data:/app/data enterprise-knowledge-platform
```

## Architecture and current boundaries

The document ingestion path is: FastAPI upload -> document validation/text extraction -> overlapping chunking -> SQLite metadata and chunk persistence. The query path is: FastAPI search -> keyword scoring over stored chunks -> ranked excerpts with source document IDs.

This release does **not** implement PDF/DOCX parsing, embeddings, vector search, an LLM, Amazon Bedrock, S3, an external vector database, knowledge-graph construction, recommendation logic, authentication, or per-user document authorization. Those are future increments and must not be interpreted as existing capabilities.

## Technology

Python, FastAPI, SQLite, pytest, Docker.
