from app.agents.search_agent import SearchAgent
from app.services.knowledge_store import KnowledgeStore


class KnowledgeWorkflow:
    """Coordinates the currently implemented document-retrieval capability."""

    def __init__(self, store: KnowledgeStore | None = None):
        self.search = SearchAgent(store=store)

    def run(self, topic: str):
        return self.search.search(topic)
