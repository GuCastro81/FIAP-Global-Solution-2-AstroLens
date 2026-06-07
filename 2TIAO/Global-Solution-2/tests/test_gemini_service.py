"""Tests for GeminiService behavior and error handling."""

import os
import tempfile
import unittest
from unittest.mock import patch

from src.services.gemini_service import GeminiService, load_env_file


class TestGeminiService(unittest.TestCase):
    def test_load_env_file_sets_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = os.path.join(temp_dir, ".env")
            with open(env_path, "w", encoding="utf-8") as handle:
                handle.write("GEMINI_API_KEY=test-key\n")

            with patch.dict(os.environ, {}, clear=True):
                load_env_file(env_path)
                self.assertEqual(os.getenv("GEMINI_API_KEY"), "test-key")

    def test_generate_text_requires_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_env = os.path.join(temp_dir, ".env")
            service = GeminiService(api_key=None, env_path=missing_env)
            response = service.generate_text("Hello")
            self.assertFalse(response.ok)
            self.assertIsNotNone(response.error)
            self.assertEqual(response.error.type, "MissingAPIKey")

    def test_generate_text_missing_dependency(self) -> None:
        with patch("src.services.gemini_service._GENAI_AVAILABLE", False):
            service = GeminiService(api_key="test-key")
            response = service.generate_text("Hello")
            self.assertFalse(response.ok)
            self.assertIsNotNone(response.error)
            self.assertEqual(response.error.type, "MissingDependency")

    def test_analyze_image_requires_api_key_before_building_image_part(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_env = os.path.join(temp_dir, ".env")
            with patch("src.services.gemini_service.types", None):
                service = GeminiService(api_key=None, env_path=missing_env)
                response = service.analyze_image(
                    "Analyze",
                    image_bytes=b"fake-image",
                    mime_type="image/jpeg",
                )

        self.assertFalse(response.ok)
        self.assertIsNotNone(response.error)
        self.assertEqual(response.error.type, "MissingAPIKey")

    def test_analyze_image_missing_dependency_does_not_crash(self) -> None:
        with patch("src.services.gemini_service._GENAI_AVAILABLE", False):
            with patch("src.services.gemini_service.types", None):
                service = GeminiService(api_key="test-key")
                response = service.analyze_image(
                    "Analyze",
                    image_bytes=b"fake-image",
                    mime_type="image/jpeg",
                )

        self.assertFalse(response.ok)
        self.assertIsNotNone(response.error)
        self.assertEqual(response.error.type, "MissingDependency")


if __name__ == "__main__":
    unittest.main()
