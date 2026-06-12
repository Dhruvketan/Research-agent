import unittest

from app import generate_report
from agents.intent_agent import classify_query_type, understand_intent
from agents.search_agent import build_expanded_queries, expand_query_terms, filter_relevant_papers, score_paper_relevance, validate_source_metadata


class ResearchAgentTests(unittest.TestCase):
    def test_generate_report_returns_expected_sections(self):
        report = generate_report("Applications of Gaussian Boson Sampling in Biological Systems")

        self.assertIn("Background", report)
        self.assertIn("Status", report)
        self.assertIn("References", report)
        self.assertTrue(
            "Insufficient literature found." in report or "Current research highlights" in report,
            report,
        )

    def test_query_expansion_adds_domain_keywords(self):
        terms = expand_query_terms("Computer vision in drones")

        self.assertIn("drone", terms)
        self.assertIn("uav", terms)
        self.assertIn("aerial", terms)
        self.assertIn("navigation", terms)

    def test_relevance_scoring_prefers_drones_content(self):
        paper = {
            "title": "Drone-based visual navigation for autonomous UAVs",
            "abstract": "Aerial perception and obstacle avoidance for drones using deep learning.",
        }
        score = score_paper_relevance(paper, "Computer vision in drones")

        self.assertGreaterEqual(score, 0.35)

    def test_intent_understanding_generates_structured_research_intent(self):
        intent = understand_intent("Computer vision in drones")

        self.assertEqual(intent["query_type"], "application_research")
        self.assertIn("computer vision", intent["domains"])
        self.assertIn("drones", intent["domains"])
        self.assertGreaterEqual(len(intent["subtopics"]), 3)

    def test_expanded_queries_are_generated_for_multi_query_retrieval(self):
        queries = build_expanded_queries("Computer vision in drones")

        self.assertGreaterEqual(len(queries), 3)
        self.assertIn("computer vision drones", " ".join(queries).lower())

    def test_relevance_filter_rejects_irrelevant_papers(self):
        papers = [
            {
                "title": "Women in Computer Vision Workshop",
                "abstract": "A discussion on inclusion and computer vision community events.",
            },
            {
                "title": "Drone-based visual navigation for autonomous UAVs",
                "abstract": "Aerial perception and obstacle avoidance for drones using deep learning.",
            },
        ]

        filtered = filter_relevant_papers(papers, "Computer vision in drones")

        self.assertEqual(len(filtered), 1)
        self.assertIn("Drone-based visual navigation", filtered[0]["title"])

    def test_query_expansion_preserves_multi_word_concepts(self):
        terms = expand_query_terms("Gaussian boson sampling in biological systems")

        self.assertIn("gaussian boson sampling", terms)
        self.assertIn("biological systems", terms)

    def test_source_validation_rejects_placeholder_metadata(self):
        papers = [
            {"title": "Survey of Gaussian boson sampling", "source": "fallback", "doi": "10.0000/example.001", "pdf_url": "https://arxiv.org/abs/0000.00001"},
            {"title": "Real quantum sampling study", "source": "arXiv", "doi": "https://doi.org/10.1000/test", "pdf_url": "https://arxiv.org/abs/2401.00001"},
        ]

        valid = validate_source_metadata(papers)

        self.assertEqual(len(valid), 1)
        self.assertEqual(valid[0]["title"], "Real quantum sampling study")


if __name__ == "__main__":
    unittest.main()
