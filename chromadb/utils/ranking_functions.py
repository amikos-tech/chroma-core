from chromadb.api.types import RankingFunction


class BM25ServerSideRankingFunction(RankingFunction):
    def __init__(self, k1=1.2, b=0.75):
        self.k1 = k1
        self.b = b

    def rank(self, query, documents):
        # ... (implementation of the BM25 ranking function)
        return ranked_documents
