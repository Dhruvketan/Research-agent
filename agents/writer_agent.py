def write_report(topic: str, tasks: list[str], papers: list[dict], notes: list[dict], critique: dict, memory_snapshot: dict) -> str:
    """Compose a structured literature-review report with citations and current research context."""
    lines = [
        f"# Research Report: {topic}",
        "",
        "## Background",
        f"This report summarizes the current research landscape for {topic}, using available metadata and abstracts from the retrieval layer.",
        "",
        "## Current research highlights",
    ]
    for note in notes:
        lines.append(f"- {note['title']} ({note['year']}) — {note['summary']}")

    lines.extend([
        "",
        "## Key papers",
    ])
    for paper in papers:
        citation = paper.get("doi") or paper.get("pdf_url") or ""
        lines.append(f"- {paper['title']} ({paper['year']})" + (f" — {citation}" if citation else ""))

    lines.extend([
        "",
        "## Major findings",
    ])
    for note in notes:
        lines.append(f"- {note['title']}: {note['objective']} {note['methodology']}")

    lines.extend([
        "",
        "## Research gaps",
        "- Full PDF retrieval and citation grounding are still needed for production-grade review quality.",
        "- Cross-paper contradiction analysis and source-level evidence validation should be added in the next phase.",
        "- The current workflow relies on metadata and abstracts, so deeper domain synthesis remains an open challenge.",
        "",
        "## Future directions",
        "- Connect this workflow to real PDF ingestion, citation APIs, and vector memory.",
        "- Add critic-agent validation, multi-agent orchestration, and benchmark evaluation in later phases.",
        "",
        "## Workflow tasks",
    ])
    for task in tasks:
        lines.append(f"- {task}")

    lines.extend([
        "",
        "## Validation summary",
        f"- Faithfulness: {critique['faithfulness']}",
        f"- Citation accuracy: {critique['citation_accuracy']}",
        f"- Hallucination risk: {critique['hallucination_risk']}",
        "",
        "## References",
    ])
    for note in notes:
        lines.append(f"- {note['citation']}")

    lines.extend([
        "",
        "## Memory snapshot",
        f"- Stored findings: {len(notes)}",
        f"- Context entries: {memory_snapshot.get('context_entries', 0)}",
    ])
    return "\n".join(lines)
