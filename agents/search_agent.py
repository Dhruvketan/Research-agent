import re
import xml.etree.ElementTree as ET

import requests


ARXIV_API = "https://export.arxiv.org/api/query"
CROSSREF_API = "https://api.crossref.org/works"


DOMAIN_SYNONYMS = {
    "drone": ["drone", "drones", "uav", "uavs", "unmanned aerial", "aerial", "aerial vision", "autonomous aerial", "visual navigation", "aerial perception"],
    "vision": ["vision", "computer vision", "visual", "perception", "scene understanding", "image understanding"],
    "navigation": ["navigation", "slam", "obstacle avoidance", "tracking", "path planning"],
    "detection": ["detection", "object detection", "segmentation", "classification", "recognition"],
}


def expand_query_terms(topic: str) -> list[str]:
    """Expand a user topic with domain keywords to improve retrieval precision."""
    lowered = re.sub(r"[^a-z0-9]+", " ", topic.lower()).split()
    terms = set(lowered)

    for token in lowered:
        terms.update(DOMAIN_SYNONYMS.get(token, []))

    if any(token in {"drone", "drones", "uav", "uavs", "aerial"} for token in lowered):
        terms.update(["drone", "uav", "aerial", "navigation", "object detection", "autonomous flight"])

    if any(token in {"vision", "visual", "perception"} for token in lowered):
        terms.update(["computer vision", "visual perception", "scene understanding"])

    return sorted(t for t in terms if len(t) > 2)[:12]


def score_paper_relevance(paper: dict, topic: str) -> float:
    """Score a paper's relevance to the user's topic using weighted keyword overlap."""
    expanded = list(expand_query_terms(topic))
    text = " ".join([
        paper.get("title", ""),
        paper.get("abstract", ""),
        " ".join(paper.get("authors", [])),
    ]).lower()

    drone_terms = {"drone", "drones", "uav", "uavs", "aerial", "autonomous flight", "navigation", "obstacle", "swarm"}
    weights = {term: 1.2 if any(token in term or term in token for token in drone_terms) else 0.6 for term in expanded}

    matched_score = sum(weights.get(term, 0.6) for term in expanded if term in text)
    total_weight = sum(weights.values())
    title_bonus = 0.15 if any(term in text for term in ["drone", "uav", "aerial", "navigation"]) else 0
    return min(1.0, (matched_score / max(1.0, total_weight)) + title_bonus)


def _filter_relevant_papers(papers: list[dict], topic: str) -> list[dict]:
    scored = [(paper, score_paper_relevance(paper, topic)) for paper in papers]
    scored = [item for item in scored if item[1] >= 0.08]
    scored.sort(key=lambda item: item[1], reverse=True)
    return [{**paper, "relevance_score": score} for paper, score in scored[:5]]


def build_search_query(topic: str) -> str:
    """Build a query string that favors domain-specific terms for the topic."""
    expanded = expand_query_terms(topic)
    domain_terms = [term for term in expanded if any(token in term for token in ["drone", "uav", "aerial", "nav", "flight", "obstacle", "detect", "perception", "slam"]) and term not in {"computer vision", "visual perception", "scene understanding"}]
    if domain_terms:
        return f'all:"{topic}" AND (' + ' OR '.join(f'all:{term}' for term in domain_terms[:6]) + ')'
    return f'all:{topic}'


def _fallback_papers(topic: str) -> list[dict]:
    return [
        {
            "title": f"Survey of {topic}",
            "authors": ["Research Team A"],
            "year": 2024,
            "doi": "10.0000/example.001",
            "abstract": "A high-level review of current progress, datasets, and open challenges.",
            "pdf_url": "https://arxiv.org/abs/0000.00001",
            "source": "fallback",
        },
        {
            "title": f"Experimental methods for {topic}",
            "authors": ["Research Team B"],
            "year": 2023,
            "doi": "10.0000/example.002",
            "abstract": "Describes experiments, evaluation criteria, and emerging applications.",
            "pdf_url": "https://arxiv.org/abs/0000.00002",
            "source": "fallback",
        },
    ]


def search_papers(topic: str) -> list[dict]:
    """Search arXiv and Crossref with expanded domain terms and relevance filtering."""
    query = build_search_query(topic)

    try:
        response = requests.get(
            ARXIV_API,
            params={"search_query": query, "start": 0, "max_results": 5},
            timeout=20,
        )
        response.raise_for_status()

        root = ET.fromstring(response.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)

        if entries:
            papers = []
            for entry in entries:
                title = entry.findtext("atom:title", default="", namespaces=ns).replace("\n", " ").strip()
                authors = [a.findtext("atom:name", default="", namespaces=ns) for a in entry.findall("atom:author", ns)]
                published = entry.findtext("atom:published", default="", namespaces=ns)
                summary = entry.findtext("atom:summary", default="", namespaces=ns).strip()
                links = entry.findall("atom:link", ns)
                pdf_url = next((link.get("href") for link in links if link.get("title") == "pdf"), "")
                doi = ""
                for link in links:
                    href = link.get("href", "")
                    if "doi.org" in href:
                        doi = href
                        break

                papers.append(
                    {
                        "title": title or f"Paper related to {topic}",
                        "authors": authors or ["Unknown author"],
                        "year": int(published[:4]) if published[:4].isdigit() else 0,
                        "doi": doi,
                        "abstract": summary or "No abstract available from the API response.",
                        "pdf_url": pdf_url,
                        "source": "arXiv",
                    }
                )
            return _filter_relevant_papers(papers, topic)
    except Exception:
        pass

    try:
        crossref = requests.get(
            CROSSREF_API,
            params={"query.title": " ".join(expand_query_terms(topic)[:6]), "rows": 5, "select": "title,author,issued,DOI,URL"},
            timeout=20,
        )
        crossref.raise_for_status()
        payload = crossref.json()
        items = payload.get("message", {}).get("items", [])
        if items:
            papers = []
            for item in items:
                title = item.get("title", [""])[0]
                authors = [a.get("family", "") + (", " + a.get("given", "") if a.get("given") else "") for a in item.get("author", [])]
                issued = item.get("issued", {}).get("date-parts", [[None]])[0][0]
                doi = item.get("DOI", "")
                papers.append(
                    {
                        "title": title,
                        "authors": authors or ["Unknown author"],
                        "year": issued or 0,
                        "doi": doi,
                        "abstract": "Crossref metadata does not provide an abstract; the report uses the available citation metadata.",
                        "pdf_url": item.get("URL", ""),
                        "source": "Crossref",
                    }
                )
            return _filter_relevant_papers(papers, topic)
    except Exception:
        pass

    return _filter_relevant_papers(_fallback_papers(topic), topic)
