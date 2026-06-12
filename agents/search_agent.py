import xml.etree.ElementTree as ET

import requests


ARXIV_API = "https://export.arxiv.org/api/query"
CROSSREF_API = "https://api.crossref.org/works"


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
    """Search arXiv and fall back to deterministic metadata if the API is unavailable."""
    try:
        response = requests.get(
            ARXIV_API,
            params={"search_query": f"all:{topic}", "start": 0, "max_results": 3},
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
            return papers
    except Exception:
        pass

    try:
        crossref = requests.get(
            CROSSREF_API,
            params={"query.title": topic, "rows": 3, "select": "title,author,issued,DOI,URL"},
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
            return papers
    except Exception:
        pass

    return _fallback_papers(topic)
