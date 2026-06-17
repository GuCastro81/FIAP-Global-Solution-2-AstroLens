"""Exoplanet atmosphere chart analysis agent using Gemini Vision."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.services.gemini_service import GeminiResponse, GeminiService

_LOGGER = logging.getLogger(__name__)
_SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
_REQUIRED_FIELDS = (
    "planet",
    "planet_type",
    "detected_molecules",
    "scientific_confidence",
    "summary",
)


@dataclass(frozen=True)
class ExoplanetAtmosphereResult:
    """Structured output for visible K2-18 b atmosphere chart labels."""

    planet: str
    planet_type: str
    detected_molecules: list[str]
    scientific_confidence: float
    summary: str


class ExoplanetSpectrumAgent:
    """Analyze the K2-18 b atmosphere composition chart with Gemini Vision."""

    def __init__(
        self, gemini_service: GeminiService, logger: Optional[logging.Logger] = None
    ) -> None:
        self._gemini_service = gemini_service
        self._logger = logger or _LOGGER

    def analyze(self, image_path: str | Path) -> ExoplanetAtmosphereResult:
        """Analyze a supported local chart image and return validated JSON fields."""
        path = _validate_image_path(image_path)
        prompt = self._build_prompt()
        response = self._gemini_service.analyze_image(prompt, image_path=str(path))
        if not response.ok:
            error = response.error.message if response.error else "Unknown error"
            self._logger.error("ExoplanetSpectrumAgent failed: %s", error)
            raise RuntimeError(error)

        payload = self._parse_response(response)
        result = self._validate_payload(payload)
        self._logger.info(
            "ExoplanetSpectrumAgent planet=%s molecules=%s confidence=%s",
            result.planet,
            len(result.detected_molecules),
            result.scientific_confidence,
        )
        return result

    def _build_prompt(self) -> str:
        return (
            "You are AstroLens ExoplanetSpectrumAgent. Analyze only the visible "
            "labels and annotations in the provided JWST atmospheric composition "
            "chart for K2-18 b. This is an educational interpretation of a "
            "published visualization, not a scientific measurement. Do not fit "
            "spectral peaks, perform calculations, infer unsupported chemistry, "
            "or use data from any other exoplanet. Return ONLY strict JSON with "
            "no markdown or extra text. Schema: {\"planet\": string, "
            "\"planet_type\": string, \"detected_molecules\": string[], "
            "\"scientific_confidence\": number, \"summary\": string}. "
            "Use molecule names visible or explicitly labeled in the chart. "
            "scientific_confidence must be between 0 and 1 and should reflect "
            "chart-label interpretation confidence, not discovery certainty."
        )

    def _parse_response(self, response: GeminiResponse) -> dict:
        if not response.data:
            raise ValueError("Gemini response has no data")

        raw_text = response.data.text.strip()
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            start = raw_text.find("{")
            end = raw_text.rfind("}")
            if start == -1 or end == -1 or end <= start:
                self._logger.error(
                    "ExoplanetSpectrumAgent could not parse JSON output."
                )
                raise ValueError("Invalid JSON response from Gemini")
            self._logger.warning(
                "ExoplanetSpectrumAgent trimming non-JSON response content."
            )
            try:
                return json.loads(raw_text[start : end + 1])
            except json.JSONDecodeError as exc:
                raise ValueError("Invalid JSON response from Gemini") from exc

    def _validate_payload(self, payload: dict) -> ExoplanetAtmosphereResult:
        missing_fields = [field for field in _REQUIRED_FIELDS if field not in payload]
        if missing_fields:
            raise ValueError(
                "Exoplanet atmosphere result is missing required fields: "
                f"{', '.join(missing_fields)}"
            )

        planet = normalize_planet_name(str(payload.get("planet", "")))
        planet_type = str(payload.get("planet_type", "")).strip()
        summary = str(payload.get("summary", "")).strip()
        molecules = payload.get("detected_molecules", [])

        if not planet:
            raise ValueError("Planet must not be empty")
        if planet != "K2-18 b":
            raise ValueError("Only K2-18 b analysis is supported")
        if not isinstance(molecules, list):
            raise ValueError("detected_molecules must be a list")

        confidence = float(payload.get("scientific_confidence", 0.0))
        if not 0 <= confidence <= 1:
            raise ValueError("scientific_confidence must be between 0 and 1")

        return ExoplanetAtmosphereResult(
            planet=planet,
            planet_type=planet_type,
            detected_molecules=[str(item).strip() for item in molecules if str(item).strip()],
            scientific_confidence=confidence,
            summary=summary,
        )


def _validate_image_path(image_path: str | Path) -> Path:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Exoplanet atmosphere image not found: {path}")
    if not path.is_file():
        raise ValueError(f"Exoplanet atmosphere image path is not a file: {path}")
    if path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(_SUPPORTED_EXTENSIONS))
        raise ValueError(
            f"Unsupported exoplanet atmosphere image format '{path.suffix}'. "
            f"Supported formats: {supported}."
        )

    try:
        header = path.read_bytes()[:16]
    except OSError as exc:
        raise ValueError(f"Could not load exoplanet atmosphere image: {path}") from exc

    if not _has_supported_image_signature(header, path.suffix.lower()):
        raise ValueError(
            "Could not load exoplanet atmosphere image as a supported JPG or PNG file: "
            f"{path}"
        )
    return path


def normalize_planet_name(name: str) -> str:
    """Normalize accepted K2-18 b spelling variants to the canonical display name."""
    normalized = re.sub(r"[\s_-]+", "", name.strip().lower())
    if normalized == "k218b":
        return "K2-18 b"
    return name.strip()


def _has_supported_image_signature(header: bytes, suffix: str) -> bool:
    if suffix in {".jpg", ".jpeg"}:
        return header.startswith(b"\xff\xd8\xff")
    if suffix == ".png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    return False
