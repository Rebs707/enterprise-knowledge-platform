from app.workflows.knowledge_workflow import KnowledgeWorkflow


def test_knowledge_workflow():

    result = KnowledgeWorkflow().run("cloud engineering")

    assert result["document"]["status"] == "processed"
    assert result["search"]["status"] == "results retrieved"
    assert result["knowledge_graph"]["status"] == "knowledge graph generated"
    assert result["recommendation"]["status"] == "recommendations generated"
