def _extract_method(abstract: str) -> str:
    text = abstract.lower()
    if "end-to-end" in text or "neural" in text or "deep learning" in text:
        return "Uses end-to-end learning or neural perception/control methods."
    if "benchmark" in text or "dataset" in text:
        return "Uses benchmark datasets and evaluation protocols to compare methods."
    if "slam" in text or "tracking" in text:
        return "Uses perception and tracking pipelines for autonomous visual reasoning."
    return "Uses a domain-specific visual perception or control approach described in the paper abstract."


def _extract_results(abstract: str) -> str:
    text = abstract.lower()
    if "autonomous" in text or "flight" in text:
        return "Demonstrates autonomous or real-time perception/control performance relevant to drone tasks."
    if "benchmark" in text or "challenge" in text:
        return "Provides benchmarked results and comparative evaluation for the target task."
    return "Reports empirical or methodological findings that support the topic area."


def _extract_metrics(abstract: str) -> str:
    text = abstract.lower()
    metrics = []
    if "accuracy" in text:
        metrics.append("accuracy")
    if "fps" in text or "real-time" in text:
        metrics.append("real-time throughput")
    if "precision" in text or "recall" in text:
        metrics.append("precision/recall")
    if not metrics:
        metrics.append("benchmark performance")
    return "Metrics discussed include " + ", ".join(metrics) + "."


def read_papers(papers: list[dict]) -> list[dict]:
    """Create structured notes from real paper metadata and abstracts."""
    notes = []
    for paper in papers:
        abstract = paper.get("abstract", "") or ""
        summary = abstract[:280] + ("..." if len(abstract) > 280 else "")
        title = paper.get("title", "Untitled paper")
        summary = summary or f"This paper contributes current research on {title}."
        method = _extract_method(abstract)
        results = _extract_results(abstract)
        metrics = _extract_metrics(abstract)
        notes.append(
            {
                "title": title,
                "authors": ", ".join(paper.get("authors", [])),
                "year": paper.get("year", "Unknown year"),
                "doi": paper.get("doi", ""),
                "summary": summary,
                "objective": f"Examine the evidence and methodological contribution described in {title}.",
                "methodology": method,
                "results": results,
                "metrics": metrics,
                "limitations": "The available retrieval metadata may not contain full PDF text; conclusions therefore reflect abstract-level evidence.",
                "citation": f"{title}. {paper.get('authors', ['Unknown author'])[:2]} ({paper.get('year', 'n.d.')}).",
            }
        )
    return notes
