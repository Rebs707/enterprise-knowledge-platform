# Enterprise Knowledge Platform — Current Architecture

The diagram below reflects the implemented local-first ingestion and keyword-retrieval path in this release. It does not depict planned cloud, vector-search, or LLM integrations.

```mermaid
flowchart TD
    U[Client] --> API[FastAPI]
    API --> UP[POST /documents]
    UP --> V[Validate filename, type, UTF-8 and 2 MiB limit]
    V --> X[Extract and normalize UTF-8 text]
    X --> C[Chunk text with configured overlap]
    C --> DB[(SQLite: document metadata, SHA-256 and chunks)]

    U --> Q[GET /search]
    Q --> TOK[Lowercase and tokenize unique query terms]
    TOK --> SA[Search Agent]
    SA --> KS[Count case-insensitive term occurrences per chunk]
    DB --> KS
    KS --> SORT[Sort by score descending, filename and chunk index]
    SORT --> R[Return limited ranked excerpts and document IDs]
    R --> U
```

## Implemented components

- FastAPI upload, metadata retrieval, health, and search endpoints
- Filename/type validation, UTF-8 decoding, normalization, and upload-size enforcement
- Overlapping text chunking
- SQLite persistence for document metadata, SHA-256 digests, and chunks
- Deterministic keyword occurrence scoring and bounded result ranking

## Retrieval semantics

Query text is lowercased and tokenized into unique alphanumeric terms of at least two characters. Each chunk receives a score equal to the total number of occurrences of those terms, counted case-insensitively. Matching chunks are ordered by descending score, then filename and chunk index, before the result limit is applied. This is lexical keyword matching; it is not semantic search or embedding-based retrieval.

## Not implemented in this release

PDF/DOCX extraction, embeddings, vector databases, Amazon S3, Amazon Bedrock, LLM answer generation, knowledge-graph construction, recommendations, authentication, and per-user authorization.
