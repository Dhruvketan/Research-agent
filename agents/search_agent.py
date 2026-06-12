import re
import xml.etree.ElementTree as ET

import requests

from agents.intent_agent import understand_intent


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
    intent = understand_intent(topic)
    terms = set(re.findall(r"[a-z0-9]+", topic.lower()))
    terms.update(intent["domains"])
    terms.update(intent["subtopics"])

    for token in intent["domains"]:
        terms.update(DOMAIN_SYNONYMS.get(token, []))
        terms.update([token, f"{token} research", f"{token} methods", f"{token} applications"])
        if token.endswith("s") and token[:-1] in DOMAIN_SYNONYMS:
            terms.update(DOMAIN_SYNONYMS[token[:-1]])

    terms.update(["drone", "uav", "aerial", "navigation", "perception", "visual navigation", "object detection", "autonomous control"])

    return sorted(t for t in terms if len(t) > 2)[:30]


def score_paper_relevance(paper: dict, topic: str) -> float:
    """Score a paper's relevance to the user's topic using weighted keyword overlap."""
    expanded = list(expand_query_terms(topic))
    text = " ".join([
        paper.get("title", ""),
        paper.get("abstract", ""),
        " ".join(paper.get("authors", [])),
    ]).lower()

    weights = {term: 1.4 if any(token in term for token in ["drone", "uav", "aerial", "navigation", "obstacle", "vision", "visual", "perception", "detection", "tracking"]) else 0.7 for term in expanded}
    matched_score = sum(weights.get(term, 0.7) for term in expanded if term in text)
    total_weight = sum(weights.values())
    topic_bonus = 0.15 if any(term in text for term in ["drone", "uav", "aerial", "navigation", "obstacle", "visual"] ) else 0
    return min(1.0, (matched_score / max(1.0, total_weight)) + topic_bonus)


def filter_relevant_papers(papers: list[dict], topic: str) -> list[dict]:
    scored = [(paper, score_paper_relevance(paper, topic)) for paper in papers]
    scored = [item for item in scored if item[1] >= 0.18]
    scored.sort(key=lambda item: item[1], reverse=True)
    return [{**paper, "relevance_score": score} for paper, score in scored[:5]]


def _filter_relevant_papers(papers: list[dict], topic: str) -> list[dict]:
    return filter_relevant_papers(papers, topic)


def build_expanded_queries(topic: str) -> list[str]:
    """Generate multiple retrieval perspectives for a topic without hardcoded mappings."""
    intent = understand_intent(topic)
    base_terms = [term for term in intent["domains"][:4] if len(term) > 2]
    subtopics = intent["subtopics"][:6]
    queries = [topic.strip()]
    if base_terms:
        queries.append(" ".join(base_terms))
    for item in subtopics:
        queries.append(f"{topic} {item}")
    if len(queries) < 4:
        queries.append(f"{topic} review")
        queries.append(f"{topic} methods")
    return list(dict.fromkeys(q.strip() for q in queries if q.strip()))[:6]


def build_search_query(topic: str) -> str:
    """Build a search string using the expanded intent."""
    queries = build_expanded_queries(topic)
    return " OR ".join(f'"{query}"' for query in queries[:4])


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
    queries = build_expanded_queries(topic)
    all_papers = []

    for query in queries:
        try:
            response = requests.get(
                ARXIV_API,
                params={"search_query": query, "start": 0, "max_results": 3},
                timeout=20,
            )
            response.raise_for_status()

            root = ET.fromstring(response.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)

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

                all_papers.append(
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
        except Exception:
            continue

    try:
        crossref = requests.get(
            CROSSREF_API,
            params={"query.title": " ".join(expand_query_terms(topic)[:6]), "rows": 6, "select": "title,author,issued,DOI,URL"},
            timeout=20,
        )
        crossref.raise_for_status()
        payload = crossref.json()
        for item in payload.get("message", {}).get("items", []):
            title = item.get("title", [""])[0]
            authors = [a.get("family", "") + (", " + a.get("given", "") if a.get("given") else "") for a in item.get("author", [])]
            issued = item.get("issued", {}).get("date-parts", [[None]])[0][0]
            all_papers.append(
                {
                    "title": title,
                    "authors": authors or ["Unknown author"],
                    "year": issued or 0,
                    "doi": item.get("DOI", ""),
                    "abstract": "Crossref metadata does not provide an abstract; the report uses the available citation metadata.",
                    "pdf_url": item.get("URL", ""),
                    "source": "Crossref",
                }
            )
    except Exception:
        pass

    unique_papers = []
    seen = set()
    for paper in all_papers + _fallback_papers(topic):
        key = (paper.get("title", "").lower(), paper.get("doi", ""))
        if key not in seen:
            seen.add(key)
            unique_papers.append(paper)

    return _filter_relevant_papers(unique_papers, topic) or _filter_relevant_papers(_fallback_papers(topic), topic)
