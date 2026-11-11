# Enterprise Knowledge Platform — Current Architecture

The diagram below reflects the implemented local-first ingestion and keyword-retrieval path in this release. It does not depict planned cloud, vector-search, or LLM integrations.

```mermaid
flowchart TD
    U[Client] --> API[FastAPI]
    API --> UP[POST /documents]
    UP --> V[Validate filename, type, UTF-8 and size]
    V --> X[Extract text]
    X --> C[Chunk with overlap]
    C --> DB[(SQLite: document metadata and chunks)]

    U --> Q[GET /search]
    Q --> SA[Search Agent]
    SA --> KS[Keyword scoring]
    KS --> DB
    DB --> R[Ranked excerpts and document references]
    R --> U
```

## Implemented components

- FastAPI upload and search endpoints
- Document validation and UTF-8 text extraction
- Overlapping text chunking
- SQLite persistence for metadata and chunks
- Deterministic keyword-based retrieval

## Not implemented in this release

PDF/DOCX extraction, embeddings, vector databases, Amazon S3, Amazon Bedrock, LLM answer generation, knowledge-graph construction, recommendations, authentication, and per-user authorization.
