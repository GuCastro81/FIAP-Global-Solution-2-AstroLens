"""Unit tests for optional ImageGenerationAgent."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.agents.image_generation_agent import (
    ImageGenerationAgent,
    ImageGenerationResult,
)
from src.services.gemini_service import GeminiError, GeminiResponse


class _StubGeminiService:
    def __init__(self, client: object) -> None:
        self._client = client

    def _get_client(self) -> object:
        return self._client


class _FakeClient:
    def __init__(self, response: object | None = None, error: Exception | None = None):
        self.models = _FakeModels(response=response, error=error)


class _FakeModels:
    def __init__(self, response: object | None, error: Exception | None):
        self._response = response
        self._error = error

    def generate_images(self, *, model: str, prompt: str, config: object) -> object:
        if self._error:
            raise self._error
        return self._response


class _FakeResponse:
    def __init__(self, image_bytes: bytes) -> None:
        self.generated_images = [_FakeGeneratedImage(image_bytes)]


class _FakeGeneratedImage:
    def __init__(self, image_bytes: bytes) -> None:
        self.image = _FakeImage(image_bytes)


class _FakeImage:
    def __init__(self, image_bytes: bytes) -> None:
        self.image_bytes = image_bytes


class TestImageGenerationAgent(unittest.TestCase):
    def test_successful_generation_saves_image_and_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            agent = ImageGenerationAgent(
                _StubGeminiService(_FakeClient(_FakeResponse(b"png-bytes"))),
                output_dir=temp_dir,
            )

            result = agent.generate(
                enhanced_artist_prompt="K2-18 b enhanced prompt",
                negative_prompt="spaceships",
                visual_style="NASA style",
            )

            self.assertIsInstance(result, ImageGenerationResult)
            self.assertEqual(result.status, "generated")
            self.assertEqual(result.model_used, "imagen-4.0-generate-001")
            self.assertIn("K2-18 b enhanced prompt", result.prompt_used)
            self.assertTrue(Path(result.image_path).exists())
            self.assertEqual(Path(result.image_path).read_bytes(), b"png-bytes")

    def test_missing_api_key_response_returns_unavailable(self) -> None:
        service_response = GeminiResponse(
            ok=False,
            model="imagen-4.0-generate-001",
            data=None,
            error=GeminiError(type="MissingAPIKey", message="API key missing"),
        )
        agent = ImageGenerationAgent(_StubGeminiService(service_response))

        result = agent.generate(
            enhanced_artist_prompt="K2-18 b prompt",
            negative_prompt="spaceships",
            visual_style="NASA style",
        )

        self.assertEqual(result.status, "unavailable")
        self.assertEqual(result.image_path, "")
        self.assertIn("current API configuration", result.message)
        self.assertIn("API key missing", result.message)

    def test_generate_images_error_returns_unavailable(self) -> None:
        agent = ImageGenerationAgent(
            _StubGeminiService(_FakeClient(error=RuntimeError("billing required")))
        )

        result = agent.generate(
            enhanced_artist_prompt="K2-18 b prompt",
            negative_prompt="spaceships",
            visual_style="NASA style",
        )

        self.assertEqual(result.status, "unavailable")
        self.assertEqual(result.image_path, "")
        self.assertIn("billing required", result.message)

    def test_empty_prompt_returns_unavailable(self) -> None:
        agent = ImageGenerationAgent(
            _StubGeminiService(_FakeClient(_FakeResponse(b"png-bytes")))
        )

        result = agent.generate(
            enhanced_artist_prompt="",
            negative_prompt="spaceships",
            visual_style="",
        )

        self.assertEqual(result.status, "unavailable")
        self.assertEqual(result.image_path, "")


if __name__ == "__main__":
    unittest.main()
