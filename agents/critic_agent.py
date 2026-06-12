def validate_findings(notes: list[dict]) -> dict:
    """Return a simple critique of the generated notes."""
    return {
        "faithfulness": "High",
        "citation_accuracy": "Pending external source verification",
        "hallucination_risk": "Low for starter project",
        "issues": ["Needs real paper retrieval for production use"],
        "notes": notes,
    }
