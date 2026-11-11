from app.services.knowledge_store import KnowledgeStore


class SearchAgent:
    def __init__(self, store: KnowledgeStore | None = None):
        self.store = store or KnowledgeStore()

    def search(self, query: str, limit: int = 10):
        results = self.store.search(query, limit=limit)
        return {
            "query": query,
            "result_count": len(results),
            "results": results,
        }
