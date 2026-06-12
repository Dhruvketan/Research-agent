def plan_topic(topic: str) -> list[str]:
    """Create a task list for a research review workflow."""
    return [
        f"Understand the core concepts behind {topic}",
        "Identify the most influential papers and reviews",
        "Extract methods, findings, and limitations",
        "Compare evidence and note contradictory results",
        "Generate a structured literature review report",
    ]
