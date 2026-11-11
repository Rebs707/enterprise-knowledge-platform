import pytest

from app.agents.document_agent import DocumentAgent
from app.services.knowledge_store import KnowledgeStore
from app.services.text_processing import (
    InvalidDocumentError,
    UnsupportedDocumentError,
    chunk_text,
    extract_text,
)


def test_extracts_utf8_markdown():
    assert extract_text("guide.md", b"\xef\xbb\xbf# Cloud\r\nAWS") == "# Cloud\nAWS"


def test_rejects_unsupported_file_type():
    with pytest.raises(UnsupportedDocumentError):
        extract_text("guide.pdf", b"not a pdf")


def test_rejects_invalid_utf8():
    with pytest.raises(InvalidDocumentError):
        extract_text("guide.txt", b"\xff\xfe")


def test_rejects_empty_document():
    with pytest.raises(InvalidDocumentError):
        extract_text("empty.txt", b"  \n")


def test_chunks_long_text_with_overlap():
    text = "alpha " * 500
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(0 < len(chunk) <= 100 for chunk in chunks)
    assert chunks[0][-15:] in chunks[1]


def test_rejects_invalid_chunk_configuration():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=10, overlap=10)


def test_document_agent_prepares_chunks():
    result = DocumentAgent().process("notes.txt", b"Cloud engineering with Python.")
    assert result["status"] == "processed"
    assert result["chunks"] == ["Cloud engineering with Python."]


def test_store_persists_and_retrieves_matching_chunks(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.db")
    chunks = ["Kubernetes manages container workloads.", "Terraform provisions cloud infrastructure."]
    document = store.add_document(
        filename="platform.md",
        content_type="text/markdown",
        raw_content="\n".join(chunks).encode(),
        chunks=chunks,
    )

    results = store.search("terraform infrastructure")
    assert len(results) == 1
    assert results[0]["document_id"] == document["document_id"]
    assert results[0]["filename"] == "platform.md"
    assert "Terraform" in results[0]["excerpt"]


def test_store_returns_document_metadata(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.db")
    created = store.add_document(
        filename="runbook.txt",
        content_type="text/plain",
        raw_content=b"Incident response",
        chunks=["Incident response"],
    )
    retrieved = store.get_document(created["document_id"])
    assert retrieved["filename"] == "runbook.txt"
    assert retrieved["chunk_count"] == 1


def test_search_is_case_insensitive_and_empty_query_has_no_results(tmp_path):
    store = KnowledgeStore(tmp_path / "knowledge.db")
    store.add_document("guide.txt", "text/plain", b"AWS CLOUD", ["AWS CLOUD"])
    assert len(store.search("aws cloud")) == 1
    assert store.search("!!!") == []
