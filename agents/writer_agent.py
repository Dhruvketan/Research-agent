def _domain_gap_items(topic: str) -> list[str]:
    lowered = topic.lower()
    if any(token in lowered for token in ["drone", "uav", "aerial", "flight"]):
        return [
            "Limited onboard compute and power budgets for real-time perception on small drones.",
            "Sparse annotated aerial datasets and poor generalization across environments and weather.",
            "Robustness issues in visual navigation, obstacle avoidance, and swarming under dynamic conditions.",
        ]
    return [
        "Need stronger domain-specific retrieval and citation grounding.",
        "Need better evidence synthesis and topic-specific gap analysis.",
    ]


def _domain_future_items(topic: str) -> list[str]:
    lowered = topic.lower()
    if any(token in lowered for token in ["drone", "uav", "aerial", "flight"]):
        return [
            "Deploy vision systems on edge hardware for real-time drone perception and navigation.",
            "Combine vision with multimodal sensing, swarm coordination, and language-guided autonomy.",
            "Build larger aerial datasets and benchmark models across weather, terrain, and mission types.",
        ]
    return [
        "Expand retrieval quality and PDF-based evidence extraction.",
        "Add multi-agent critique, benchmark evaluation, and domain-specific synthesis.",
    ]


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
    ])
    for item in _domain_gap_items(topic):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "## Future directions",
    ])
    for item in _domain_future_items(topic):
        lines.append(f"- {item}")

    lines.extend([
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
