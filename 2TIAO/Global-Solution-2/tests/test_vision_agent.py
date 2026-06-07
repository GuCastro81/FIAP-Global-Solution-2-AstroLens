"""Unit tests for VisionAgent parsing and validation."""

import unittest

from src.agents.vision_agent import VisionAgent, VisionAnalysisResult
from src.services.gemini_service import GeminiGenerationData, GeminiResponse


class _StubGeminiService:
    def __init__(self, response: GeminiResponse) -> None:
        self._response = response

    def analyze_image(self, prompt: str, *, image_path: str) -> GeminiResponse:
        return self._response


class TestVisionAgent(unittest.TestCase):
    def test_valid_payload(self) -> None:
        response = GeminiResponse(
            ok=True,
            model="gemini-2.5-flash",
            data=GeminiGenerationData(
                text=(
                    "{\"classification\": \"Galaxy\", "
                    "\"confidence\": 0.93, "
                    "\"description\": \"Spiral galaxy\", "
                    "\"astronomical_objects\": [\"spiral galaxy\"], "
                    "\"scientific_tags\": [\"spiral\", \"galaxy\"]}"
                ),
                usage=None,
                mode="vision",
                image_mime_type="image/jpeg",
            ),
            error=None,
        )
        agent = VisionAgent(_StubGeminiService(response))
        result = agent.analyze("image.jpg")
        self.assertIsInstance(result, VisionAnalysisResult)
        self.assertEqual(result.classification, "Galaxy")

    def test_invalid_classification(self) -> None:
        response = GeminiResponse(
            ok=True,
            model="gemini-2.5-flash",
            data=GeminiGenerationData(
                text=(
                    "{\"classification\": \"Comet\", "
                    "\"confidence\": 0.5, "
                    "\"description\": \"Comet\", "
                    "\"astronomical_objects\": [], "
                    "\"scientific_tags\": []}"
                ),
                usage=None,
                mode="vision",
                image_mime_type="image/jpeg",
            ),
            error=None,
        )
        agent = VisionAgent(_StubGeminiService(response))
        with self.assertRaises(ValueError):
            agent.analyze("image.jpg")

    def test_error_response(self) -> None:
        response = GeminiResponse(
            ok=False,
            model="gemini-2.5-flash",
            data=None,
            error=None,
        )
        agent = VisionAgent(_StubGeminiService(response))
        with self.assertRaises(RuntimeError):
            agent.analyze("image.jpg")


if __name__ == "__main__":
    unittest.main()
