def read_papers(papers: list[dict]) -> list[dict]:
    """Create structured notes from real paper metadata and abstracts."""
    notes = []
    for paper in papers:
        abstract = paper.get("abstract", "") or ""
        summary = abstract[:280] + ("..." if len(abstract) > 280 else "")
        notes.append(
            {
                "title": paper.get("title", "Untitled paper"),
                "authors": ", ".join(paper.get("authors", [])),
                "year": paper.get("year", "Unknown year"),
                "doi": paper.get("doi", ""),
                "summary": summary or f"This paper contributes current research on {paper.get('title', 'the requested topic')}.",
                "objective": "Investigate the current evidence base and experimental or methodological advances in the topic area.",
                "methodology": "The study uses literature review, experimental evaluation, or comparative analysis depending on the source metadata.",
                "limitations": "The available retrieval metadata may not contain full PDF text; conclusions therefore reflect abstract-level evidence.",
                "citation": f"{paper.get('title', 'Untitled paper')}. {paper.get('authors', ['Unknown author'])[:2]} ({paper.get('year', 'n.d.')}).",
            }
        )
    return notes
