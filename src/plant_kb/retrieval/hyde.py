def hyde_search(query, generate_hypothetical_document, retriever, top_k=8):
    """HYDE: hypothetical text is a retrieval aid only, never evidence for the final answer."""
    hypothetical = generate_hypothetical_document(query)
    return retriever.search(hypothetical.strip() if hypothetical and hypothetical.strip() else query, top_k=top_k)
