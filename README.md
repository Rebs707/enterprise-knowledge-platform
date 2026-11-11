# Enterprise Knowledge Platform

A local-first enterprise document intelligence platform. The current milestone implements validated, size-bounded document ingestion, text chunking, persistent metadata/chunk storage, and keyword retrieval behind a FastAPI service.

## Implemented in the current release

- Upload UTF-8 plain-text (`.txt`) and Markdown (`.md`) documents.
- Enforce a 2 MiB upload limit and reject unsupported formats or invalid UTF-8.
- Split content into overlapping chunks for retrieval.
- Persist document metadata, SHA-256 digests, and chunks in SQLite.
- Search indexed chunks using deterministic, case-insensitive keyword scoring.
- Retrieve document metadata by document ID.
- Run locally or in Docker; the Docker Compose configuration uses a named volume for SQLite data.
- Exercise the HTTP API through automated FastAPI integration tests.

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

The automated suite currently contains 18 tests:

- 10 document-processing, chunking, persistence, metadata and keyword-search tests.
- 1 workflow test using a temporary SQLite database.
- 7 HTTP-level API integration tests covering health, upload, metadata retrieval, search, result limits, unknown document IDs, unsupported file types, invalid UTF-8 and oversized uploads.

The API integration tests use FastAPI's test client with an isolated temporary database, so they do not write test documents into the default local data store.

GitHub Actions is configured to install the pinned dependencies and run the test suite on pushes and pull requests targeting `main`. A workflow run must complete successfully before its result can be described as CI-verified.

The API was also manually smoke-tested locally for health, document upload, metadata retrieval, keyword search, unknown-document handling, unsupported file type, invalid UTF-8, and oversized upload. Those manual checks are separate from the automated test suite.

## Retrieval behaviour

Search is deterministic keyword matching, not semantic retrieval:

1. The query is lowercased and tokenized into unique alphanumeric terms of at least two characters.
2. Each stored chunk is checked using case-insensitive substring occurrence counts for those terms.
3. A chunk's score is the sum of its matching term occurrence counts.
4. Matching chunks are sorted by descending score, then filename and chunk index. The requested result limit is bounded to 1–50.

This implementation does not use embeddings, semantic similarity, an LLM, or a learned ranking model.

## Docker

Build and run with Docker:

```bash
docker build -t enterprise-knowledge-platform .
docker run --rm -p 8000:8000 -v ekp-data:/app/data enterprise-knowledge-platform
```

Or use Docker Compose:

```bash
docker compose up --build
```

The Compose service mounts the named `ekp-data` volume at `/app/data`, preserving the default SQLite database across container recreation. Docker image and container runtime verification are not claimed by the local test results above.

## Architecture and current boundaries

The document ingestion path is: FastAPI upload -> document validation/text extraction -> overlapping chunking -> SQLite metadata and chunk persistence. The query path is: FastAPI search -> deterministic keyword occurrence scoring over stored chunks -> ranked excerpts with source document IDs.

This release does **not** implement PDF/DOCX parsing, embeddings, vector search, an LLM, Amazon Bedrock, S3, an external vector database, knowledge-graph construction, recommendation logic, authentication, or per-user document authorization. Those are future increments and must not be interpreted as existing capabilities.

## Technology

Python, FastAPI, SQLite, pytest, HTTPX, Docker, GitHub Actions.
