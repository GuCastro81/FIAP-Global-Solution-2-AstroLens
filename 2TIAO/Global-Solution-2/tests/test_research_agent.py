"""Unit tests for ResearchAgent behavior."""

import unittest

from src.agents.research_agent import ResearchAgent, ResearchResult
from src.agents.vision_agent import VisionAnalysisResult


class TestResearchAgent(unittest.TestCase):
    def test_research_loads_structured_sections(self) -> None:
        analysis = VisionAnalysisResult(
            classification="Galaxy",
            confidence=0.9,
            description="Test",
            astronomical_objects=["spiral"],
            scientific_tags=["Spiral Galaxy"],
        )
        agent = ResearchAgent()
        result = agent.research(analysis)
        self.assertIsInstance(result, ResearchResult)
        self.assertEqual(result.topic, "Galaxy")
        self.assertIn("gravitationally bound", result.definition)
        self.assertIn("universe evolved", result.scientific_importance)
        self.assertIn("Milky Way", result.space_exploration_relevance)
        self.assertIn("STEM education", result.earth_impact)
        self.assertEqual(result.source, "galaxy.md")
        self.assertEqual(result.related_tags, ["Spiral Galaxy"])

    def test_invalid_classification(self) -> None:
        analysis = VisionAnalysisResult(
            classification="Other",
            confidence=0.5,
            description="Test",
            astronomical_objects=[],
            scientific_tags=[],
        )
        agent = ResearchAgent()
        with self.assertRaises(ValueError):
            agent.research(analysis)


if __name__ == "__main__":
    unittest.main()
