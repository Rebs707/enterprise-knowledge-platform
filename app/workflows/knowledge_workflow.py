from app.agents.document_agent import DocumentAgent
from app.agents.search_agent import SearchAgent
from app.agents.knowledge_graph_agent import KnowledgeGraphAgent
from app.agents.recommendation_agent import RecommendationAgent


class KnowledgeWorkflow:

    def __init__(self):
        self.document = DocumentAgent()
        self.search = SearchAgent()
        self.graph = KnowledgeGraphAgent()
        self.recommendation = RecommendationAgent()

    def run(self, topic: str):

        return {
            "document": self.document.process(topic),
            "search": self.search.search(topic),
            "knowledge_graph": self.graph.build(topic),
            "recommendation": self.recommendation.recommend(topic)
        }
