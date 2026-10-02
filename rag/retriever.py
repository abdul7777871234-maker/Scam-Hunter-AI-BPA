from __future__ import annotations

from rag.embeddings import Embedder
from rag.reranker import rerank


class Retriever:
    def __init__(self, kb, settings):
        self.kb = kb
        self.settings = settings
        self.embedder = None

    def search(self, query: str, k: int | None = None):
        if self.kb.store.count == 0:
            return []

        if self.embedder is None:
            self.embedder = Embedder(self.settings.embedding_model)

        vector = self.embedder.encode([query])

        results = self.kb.store.search(
            vector,
            k or self.settings.rag_top_k
        )

        return rerank(
            query,
            results,
            self.settings.rerank_top_k
        )
