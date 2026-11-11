import pytest
from fastapi.testclient import TestClient

from app.api import knowledge as knowledge_api
from app.agents.search_agent import SearchAgent
from app.main import app
from app.services.knowledge_store import KnowledgeStore


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Run the real FastAPI routes against an isolated temporary database."""
    store = KnowledgeStore(tmp_path / "api-test.db")
    monkeypatch.setattr(knowledge_api, "store", store)
    monkeypatch.setattr(knowledge_api, "search_agent", SearchAgent(store=store))
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_upload_metadata_and_search_endpoints(client):
    upload = client.post(
        "/documents",
        files={"file": ("cloud-notes.md", b"# Cloud\nKubernetes runs container workloads.", "text/markdown")},
    )

    assert upload.status_code == 201
    uploaded_document = upload.json()
    assert uploaded_document["status"] == "indexed"
    assert uploaded_document["chunk_count"] == 1

    document_id = uploaded_document["document_id"]
    metadata = client.get(f"/documents/{document_id}")
    assert metadata.status_code == 200
    assert metadata.json()["filename"] == "cloud-notes.md"
    assert metadata.json()["chunk_count"] == 1

    search = client.get("/search", params={"q": "Kubernetes workloads"})
    assert search.status_code == 200
    payload = search.json()
    assert payload["result_count"] == 1
    assert payload["results"][0]["document_id"] == document_id
    assert payload["results"][0]["filename"] == "cloud-notes.md"


def test_search_endpoint_respects_result_limit(client):
    for filename, body in [
        ("one.txt", b"Terraform provisions cloud infrastructure."),
        ("two.txt", b"Terraform automates infrastructure changes."),
    ]:
        response = client.post(
            "/documents",
            files={"file": (filename, body, "text/plain")},
        )
        assert response.status_code == 201

    response = client.get("/search", params={"q": "Terraform", "limit": 1})

    assert response.status_code == 200
    assert response.json()["result_count"] == 1


def test_metadata_endpoint_returns_404_for_unknown_document(client):
    response = client.get("/documents/not-a-real-document-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."


def test_upload_endpoint_rejects_unsupported_file_type(client):
    response = client.post(
        "/documents",
        files={"file": ("guide.pdf", b"not a supported document", "application/pdf")},
    )

    assert response.status_code == 415


def test_upload_endpoint_rejects_invalid_utf8(client):
    response = client.post(
        "/documents",
        files={"file": ("guide.txt", b"\xff\xfe", "text/plain")},
    )

    assert response.status_code == 400


def test_upload_endpoint_rejects_oversized_document(client):
    response = client.post(
        "/documents",
        files={"file": ("large.txt", b"a" * (2 * 1024 * 1024 + 1), "text/plain")},
    )

    assert response.status_code == 413
