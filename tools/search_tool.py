def search_public_sources(topic: str) -> list[dict]:
    """Placeholder wrapper for real search integrations later in the roadmap."""
    return [
        {"source": "arXiv", "query": topic},
        {"source": "PubMed", "query": topic},
        {"source": "Semantic Scholar", "query": topic},
    ]
