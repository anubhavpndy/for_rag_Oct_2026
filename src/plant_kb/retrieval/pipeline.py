from .fusion import reciprocal_rank_fusion
class HybridRetrievalPipeline:
    """Fuse lexical and semantic rankings with RRF; optionally rerank the candidates."""
    def __init__(self, lexical_retriever, semantic_retriever=None, reranker=None):
        self.lexical, self.semantic, self.reranker = lexical_retriever, semantic_retriever, reranker
    def search(self, query, top_k=5, use_reranker=False):
        lists = [self.lexical.search(query, top_k=20)]
        if self.semantic is not None:
            lists.append(self.semantic.search(query, top_k=20))
        fused = reciprocal_rank_fusion(lists, top_k=max(top_k, 10))
        if use_reranker and self.reranker is not None:
            return self.reranker.rerank(query, fused, top_k=top_k)
        return fused[:top_k]
