from collections import defaultdict
def reciprocal_rank_fusion(result_lists, k=60, top_k=8):
    scores, items = defaultdict(float), {}
    for results in result_lists:
        for rank, item in enumerate(results, 1):
            key = item.get("chunk_id")
            if not key: continue
            scores[key] += 1.0 / (k + rank)
            items.setdefault(key, dict(item))
    output = []
    for key in sorted(scores, key=scores.get, reverse=True)[:top_k]:
        item = items[key]; item["rrf_score"] = scores[key]; item["retrieval_method"] = "rrf"
        output.append(item)
    return output
