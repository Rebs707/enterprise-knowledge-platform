from app.services.knowledge_store import KnowledgeStore
from app.workflows.knowledge_workflow import KnowledgeWorkflow


def test_knowledge_workflow_returns_real_retrieval_results(tmp_path):
    store = KnowledgeStore(tmp_path / "workflow.db")
    store.add_document(
        filename="cloud-notes.md",
        content_type="text/markdown",
        raw_content=b"Cloud engineering with Kubernetes",
        chunks=["Cloud engineering with Kubernetes"],
    )

    result = KnowledgeWorkflow(store=store).run("Kubernetes")

    assert result["result_count"] == 1
    assert result["results"][0]["filename"] == "cloud-notes.md"
