class CrossEncoderReranker:
    """Optional reranker; requires sentence-transformers and an approved model."""
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        try:
            from sentence_transformers import CrossEncoder
        except ImportError as exc:
            raise RuntimeError("Install optional dependency: pip install sentence-transformers") from exc
        self.model = CrossEncoder(model_name)
    def rerank(self, query, candidates, top_k=5):
        if not candidates: return []
        scores = self.model.predict([(query, c.get("chunk_text", "")) for c in candidates])
        ranked = []
        for candidate, score in zip(candidates, scores):
            row = dict(candidate); row["reranker_score"] = float(score); ranked.append(row)
        return sorted(ranked, key=lambda x: x["reranker_score"], reverse=True)[:top_k]
