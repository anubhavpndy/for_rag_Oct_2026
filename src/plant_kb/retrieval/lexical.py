import re, json
from pathlib import Path
TOKEN = re.compile(r"[a-zA-Z0-9_./%-]+")

def tokenize(text):
    return [t.lower() for t in TOKEN.findall(text or "")]

def load_jsonl(path):
    with Path(path).open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

class LexicalRetriever:
    def __init__(self, chunks):
        self.chunks = chunks
        self.tokens = [tokenize(c.get("chunk_text", "")) for c in chunks]
        try:
            from rank_bm25 import BM25Okapi
            self.bm25 = BM25Okapi(self.tokens) if self.tokens else None
        except Exception:
            self.bm25 = None

    def search(self, query, top_k=5, department=None, unit_id=None):
        candidates = [(i, c) for i, c in enumerate(self.chunks)
            if (not department or c.get("department", "").lower() == department.lower())
            and (not unit_id or c.get("unit_id", "").lower() == unit_id.lower())]
        if not candidates: return []
        qtokens = tokenize(query)
        if self.bm25 is not None and len(candidates) == len(self.chunks):
            scores = self.bm25.get_scores(qtokens)
            order = sorted(range(len(self.chunks)), key=lambda i: float(scores[i]), reverse=True)[:top_k]
            return [{**self.chunks[i], "retrieval_score": float(scores[i]), "retrieval_method": "bm25"}
                    for i in order if scores[i] > 0]
        qset = set(qtokens); ranked = []
        for _, c in candidates:
            tokens = tokenize(c.get("chunk_text", ""))
            score = sum(t in qset for t in tokens) / max(1, len(qset))
            if query.lower() in c.get("chunk_text", "").lower(): score += 2
            if score > 0: ranked.append({**c, "retrieval_score": score, "retrieval_method": "token_overlap"})
        return sorted(ranked, key=lambda x: x["retrieval_score"], reverse=True)[:top_k]
