import unittest

from app import generate_report


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


if __name__ == "__main__":
    unittest.main()
