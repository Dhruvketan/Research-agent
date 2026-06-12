import unittest

from app import generate_report
from agents.search_agent import expand_query_terms, score_paper_relevance


class ResearchAgentTests(unittest.TestCase):
    def test_generate_report_returns_expected_sections(self):
        report = generate_report("Applications of Gaussian Boson Sampling in Biological Systems")

        self.assertIn("Background", report)
        self.assertIn("Key papers", report)
        self.assertIn("Major findings", report)
        self.assertIn("Research gaps", report)
        self.assertIn("Future directions", report)
        self.assertIn("References", report)
        self.assertIn("Current research highlights", report)
        self.assertIn("Cross-paper synthesis", report)
        self.assertIn("Evaluation metrics", report)

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


if __name__ == "__main__":
    unittest.main()
