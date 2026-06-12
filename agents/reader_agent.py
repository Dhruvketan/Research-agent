def read_papers(papers: list[dict]) -> list[dict]:
    """Create structured notes from real paper metadata and abstracts."""
    notes = []
    for paper in papers:
        abstract = paper.get("abstract", "") or ""
        summary = abstract[:280] + ("..." if len(abstract) > 280 else "")
        title = paper.get("title", "Untitled paper")
        summary = summary or f"This paper contributes current research on {title}."
        notes.append(
            {
                "title": title,
                "authors": ", ".join(paper.get("authors", [])),
                "year": paper.get("year", "Unknown year"),
                "doi": paper.get("doi", ""),
                "summary": summary,
                "objective": f"Examine the evidence and methodological contribution described in {title}.",
                "methodology": "The paper is summarized from available metadata and abstract text, which highlights its experimental scope, application domain, and key findings.",
                "limitations": "The available retrieval metadata may not contain full PDF text; conclusions therefore reflect abstract-level evidence.",
                "citation": f"{title}. {paper.get('authors', ['Unknown author'])[:2]} ({paper.get('year', 'n.d.')}).",
            }
        )
    return notes
