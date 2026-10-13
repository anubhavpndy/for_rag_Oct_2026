def route_query(query):
    q = (query or "").lower()
    if any(s in q for s in ("how many", "count of", "average", "maximum", "minimum")):
        return "structured_query_review"
    return "lexical"  # local baseline; later add hybrid/vector routing
