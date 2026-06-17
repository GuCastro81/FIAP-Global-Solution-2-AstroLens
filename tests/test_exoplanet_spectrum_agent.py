"""Unit tests for ExoplanetSpectrumAgent parsing and validation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.agents.exoplanet_spectrum_agent import (
    ExoplanetAtmosphereResult,
    ExoplanetSpectrumAgent,
    normalize_planet_name,
)
from src.services.gemini_service import GeminiGenerationData, GeminiResponse


class _StubGeminiService:
    def __init__(self, response: GeminiResponse) -> None:
        self._response = response

    def analyze_image(self, prompt: str, *, image_path: str) -> GeminiResponse:
        return self._response


class TestExoplanetSpectrumAgent(unittest.TestCase):
    def test_valid_payload(self) -> None:
        agent = ExoplanetSpectrumAgent(_StubGeminiService(_success_response(_payload())))

        with _temporary_jpeg() as image_path:
            result = agent.analyze(image_path)

        self.assertIsInstance(result, ExoplanetAtmosphereResult)
        self.assertEqual(result.planet, "K2-18 b")
        self.assertEqual(result.detected_molecules[0], "Methane")
        self.assertEqual(result.scientific_confidence, 0.89)

    def test_accepted_planet_name_variants_are_stored_canonically(self) -> None:
        variants = ["K2-18b", "K2 18 b", "K2-18 B", "k2-18 b"]

        for variant in variants:
            with self.subTest(variant=variant):
                agent = ExoplanetSpectrumAgent(
                    _StubGeminiService(_success_response(_payload(planet=variant)))
                )
                with _temporary_jpeg() as image_path:
                    result = agent.analyze(image_path)

                self.assertEqual(result.planet, "K2-18 b")

    def test_normalize_planet_name_accepts_common_k2_18_b_variants(self) -> None:
        variants = {
            "K2-18b": "K2-18 b",
            "K2 18 b": "K2-18 b",
            "K2-18 B": "K2-18 b",
            "k2-18 b": "K2-18 b",
        }

        for value, expected in variants.items():
            with self.subTest(value=value):
                self.assertEqual(normalize_planet_name(value), expected)

    def test_unrelated_planet_is_rejected(self) -> None:
        agent = ExoplanetSpectrumAgent(
            _StubGeminiService(_success_response(_payload(planet="TRAPPIST-1 e")))
        )

        with _temporary_jpeg() as image_path:
            with self.assertRaises(ValueError):
                agent.analyze(image_path)

    def test_trims_non_json_response_content(self) -> None:
        response = _success_response(f"```json\n{_payload()}\n```")
        agent = ExoplanetSpectrumAgent(_StubGeminiService(response))

        with _temporary_jpeg() as image_path:
            result = agent.analyze(image_path)

        self.assertEqual(result.planet_type, "Sub-Neptune")

    def test_malformed_response_raises_value_error(self) -> None:
        agent = ExoplanetSpectrumAgent(_StubGeminiService(_success_response("not json")))

        with _temporary_jpeg() as image_path:
            with self.assertRaises(ValueError):
                agent.analyze(image_path)

    def test_missing_required_field_raises_value_error(self) -> None:
        payload = (
            "{\"planet\": \"K2-18 b\", \"planet_type\": \"Sub-Neptune\", "
            "\"detected_molecules\": [], \"scientific_confidence\": 0.5}"
        )
        agent = ExoplanetSpectrumAgent(_StubGeminiService(_success_response(payload)))

        with _temporary_jpeg() as image_path:
            with self.assertRaises(ValueError):
                agent.analyze(image_path)

    def test_confidence_out_of_range_raises_value_error(self) -> None:
        payload = _payload(scientific_confidence=1.2)
        agent = ExoplanetSpectrumAgent(_StubGeminiService(_success_response(payload)))

        with _temporary_jpeg() as image_path:
            with self.assertRaises(ValueError):
                agent.analyze(image_path)

    def test_missing_file_raises_file_not_found_error(self) -> None:
        agent = ExoplanetSpectrumAgent(_StubGeminiService(_success_response(_payload())))

        with self.assertRaises(FileNotFoundError):
            agent.analyze("missing-atmosphere-composition.jpg")

    def test_unsupported_extension_raises_value_error(self) -> None:
        agent = ExoplanetSpectrumAgent(_StubGeminiService(_success_response(_payload())))

        with tempfile.NamedTemporaryFile(suffix=".gif") as handle:
            handle.write(b"GIF89a")
            handle.flush()
            with self.assertRaises(ValueError):
                agent.analyze(handle.name)

    def test_unloadable_image_signature_raises_value_error(self) -> None:
        agent = ExoplanetSpectrumAgent(_StubGeminiService(_success_response(_payload())))

        with tempfile.NamedTemporaryFile(suffix=".jpg") as handle:
            handle.write(b"not-a-real-jpeg")
            handle.flush()
            with self.assertRaises(ValueError):
                agent.analyze(handle.name)

    def test_gemini_error_response_raises_runtime_error(self) -> None:
        response = GeminiResponse(
            ok=False,
            model="gemini-2.5-flash",
            data=None,
            error=None,
        )
        agent = ExoplanetSpectrumAgent(_StubGeminiService(response))

        with _temporary_jpeg() as image_path:
            with self.assertRaises(RuntimeError):
                agent.analyze(image_path)


def _payload(planet: str = "K2-18 b", scientific_confidence: float = 0.89) -> str:
    return (
        f"{{\"planet\": \"{planet}\", "
        "\"planet_type\": \"Sub-Neptune\", "
        "\"detected_molecules\": [\"Methane\", \"Carbon Dioxide\", "
        "\"Dimethyl Sulfide\"], "
        f"\"scientific_confidence\": {scientific_confidence}, "
        "\"summary\": \"The chart labels methane and carbon dioxide evidence.\"}"
    )


def _success_response(text: str) -> GeminiResponse:
    return GeminiResponse(
        ok=True,
        model="gemini-2.5-flash",
        data=GeminiGenerationData(
            text=text,
            usage=None,
            mode="vision",
            image_mime_type="image/jpeg",
        ),
        error=None,
    )


class _temporary_jpeg:
    def __enter__(self) -> Path:
        self._handle = tempfile.NamedTemporaryFile(suffix=".jpg")
        self._handle.write(b"\xff\xd8\xff\xe0valid-test-jpeg")
        self._handle.flush()
        return Path(self._handle.name)

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._handle.close()


if __name__ == "__main__":
    unittest.main()
