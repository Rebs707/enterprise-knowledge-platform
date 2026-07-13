from fastapi import APIRouter
from app.workflows.knowledge_workflow import KnowledgeWorkflow

router = APIRouter()

workflow = KnowledgeWorkflow()


@router.get("/knowledge/{topic}")
def knowledge(topic: str):
    return workflow.run(topic)
