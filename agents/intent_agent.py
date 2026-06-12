import re


STOPWORDS = {
    "a", "an", "and", "for", "in", "of", "on", "the", "to", "with", "using", "into", "from", "vs", "versus"
}


def _normalize_tokens(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in STOPWORDS]


def classify_query_type(topic: str) -> str:
    """Classify a user query into a general research intent type."""
    lowered = topic.lower()
    tokens = [token for token in re.findall(r"[a-z0-9]+", lowered) if token not in STOPWORDS]

    if any(marker in lowered for marker in [" vs ", " versus ", " compared with ", " against "]):
        return "comparative_research"
    if len(set(tokens)) >= 2 and any(marker in lowered for marker in [" in ", " for ", " using ", " with ", " applied to "]):
        return "application_research"
    if any(marker in lowered for marker in [" and ", " interaction ", " relationship "]):
        return "relationship_research"
    if any(marker in lowered for marker in [" method ", " algorithm ", " sampling ", " model ", " framework "]):
        return "method_research"
    return "domain_research"


def infer_subtopics(topic: str) -> list[str]:
    """Generate a small, generic set of research subtopics from the user query."""
    tokens = set(_normalize_tokens(topic))
    subtopics = []

    if tokens & {"vision", "visual", "image", "perception", "scene"}:
        subtopics.extend(["object detection", "tracking", "visual navigation", "scene understanding"])
    if tokens & {"drone", "uav", "aerial", "robot", "autonomous", "flight"}:
        subtopics.extend(["navigation", "obstacle avoidance", "SLAM", "autonomous control"])
    if tokens & {"robot", "manufacturing", "factory", "industrial", "automation"}:
        subtopics.extend(["industrial robotics", "factory automation", "robot manipulation", "human-robot collaboration"])
    if tokens & {"biology", "biological", "drug", "medical", "genomic", "protein"}:
        subtopics.extend(["experimental validation", "biological mechanisms", "clinical translation"])
    if tokens & {"quantum", "graph", "sampling", "algorithm", "clustering"}:
        subtopics.extend(["algorithm design", "benchmarking", "scalability", "error analysis"])

    if not subtopics:
        subtopics.extend(["benchmarking", "evaluation", "real-world deployment", "comparative analysis"])

    unique = []
    for item in subtopics:
        if item not in unique:
            unique.append(item)
    return unique[:8]


def understand_intent(topic: str) -> dict:
    """Build a structured research intent object from a raw question."""
    lowered = topic.lower()
    phrases = []
    if "computer vision" in lowered:
        phrases.append("computer vision")
    if "drone" in lowered or "uav" in lowered:
        phrases.append("drones")

    tokens = [token for token in _normalize_tokens(topic) if token not in {"research"}]
    domains = []
    for phrase in phrases:
        if phrase not in domains:
            domains.append(phrase)
    for token in tokens:
        if token not in domains:
            domains.append(token)

    if len(domains) < 2:
        domains.extend([topic.strip().lower()])

    return {
        "query_type": classify_query_type(topic),
        "domains": domains[:6],
        "relationship": "application" if classify_query_type(topic) == "application_research" else "comparison" if classify_query_type(topic) == "comparative_research" else "interaction",
        "subtopics": infer_subtopics(topic),
        "raw_query": topic,
    }
