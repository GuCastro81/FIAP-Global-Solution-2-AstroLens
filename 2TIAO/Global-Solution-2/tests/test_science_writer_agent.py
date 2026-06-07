"""Unit tests for ScienceWriterAgent behavior."""

import json
import unittest

from src.agents.research_agent import ResearchResult
from src.agents.science_writer_agent import ScienceReport, ScienceWriterAgent
from src.agents.vision_agent import VisionAnalysisResult
from src.services.gemini_service import (
    GeminiError,
    GeminiGenerationData,
    GeminiResponse,
)


class FakeGeminiService:
    def __init__(self, response: GeminiResponse) -> None:
        self.response = response
        self.last_prompt = ""

    def generate_text(self, prompt: str) -> GeminiResponse:
        self.last_prompt = prompt
        return self.response


class TestScienceWriterAgent(unittest.TestCase):
    def test_write_generates_structured_report(self) -> None:
        service = FakeGeminiService(_success_response(_report_payload()))
        agent = ScienceWriterAgent(service)

        report = agent.write(_vision_result(), _research_result())

        self.assertIsInstance(report, ScienceReport)
        self.assertIn("spiral galaxy", report.scientific_summary)
        self.assertIn("radiation", report.space_exploration_importance)
        self.assertIn("image processing", report.earth_impact)
        self.assertIn("Milky Way", report.curiosities)
        self.assertIn("VisionAgent output", service.last_prompt)
        self.assertIn("ResearchAgent output", service.last_prompt)
        self.assertIn("Andromeda", service.last_prompt)
        self.assertIn("dark matter", service.last_prompt)

    def test_write_trims_non_json_response_text(self) -> None:
        raw_text = f"```json\n{json.dumps(_report_payload())}\n```"
        service = FakeGeminiService(_success_text(raw_text))
        agent = ScienceWriterAgent(service)

        report = agent.write(_vision_result(), _research_result())

        self.assertEqual(report.earth_impact, _report_payload()["earth_impact"])

    def test_write_limits_sections_to_250_words(self) -> None:
        payload = _report_payload()
        payload["curiosities"] = " ".join(f"word{i}" for i in range(300))
        service = FakeGeminiService(_success_response(payload))
        agent = ScienceWriterAgent(service)

        report = agent.write(_vision_result(), _research_result())

        self.assertEqual(len(report.curiosities.split()), 250)

    def test_write_raises_on_gemini_error(self) -> None:
        response = GeminiResponse(
            ok=False,
            model="gemini-test",
            data=None,
            error=GeminiError(type="MissingAPIKey", message="API key missing"),
        )
        service = FakeGeminiService(response)
        agent = ScienceWriterAgent(service)

        with self.assertRaises(RuntimeError):
            agent.write(_vision_result(), _research_result())


def _vision_result() -> VisionAnalysisResult:
    return VisionAnalysisResult(
        classification="Galaxy",
        confidence=0.98,
        description="Andromeda appears as a face-on spiral galaxy.",
        astronomical_objects=["Spiral Galaxy", "Stars"],
        scientific_tags=["Spiral galaxy", "Star formation"],
    )


def _research_result() -> ResearchResult:
    return ResearchResult(
        topic="Galaxy",
        definition="A galaxy is a gravitationally bound system of stars.",
        scientific_importance="Galaxy rotation curves provide evidence for dark matter.",
        space_exploration_relevance="Galactic structure informs radiation planning.",
        earth_impact="Galaxy research advances image processing.",
        source="galaxy.md",
        related_tags=["Spiral galaxy", "Dark matter"],
    )


def _report_payload() -> dict:
    return {
        "scientific_summary": "The image shows a spiral galaxy with active star formation.",
        "space_exploration_importance": "It helps explain radiation environments for missions.",
        "earth_impact": "Galaxy research improves image processing and sensors.",
        "curiosities": "The Milky Way is also a spiral galaxy.",
    }


def _success_response(payload: dict) -> GeminiResponse:
    return _success_text(json.dumps(payload))


def _success_text(text: str) -> GeminiResponse:
    return GeminiResponse(
        ok=True,
        model="gemini-test",
        data=GeminiGenerationData(
            text=text,
            usage=None,
            mode="text",
        ),
        error=None,
    )


if __name__ == "__main__":
    unittest.main()
