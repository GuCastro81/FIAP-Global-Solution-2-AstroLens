"""Educational report generation for exoplanet atmosphere analysis."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from typing import Optional

from src.agents.exoplanet_spectrum_agent import ExoplanetAtmosphereResult
from src.services.gemini_service import GeminiResponse, GeminiService

_LOGGER = logging.getLogger(__name__)
_REPORT_FIELDS = (
    "planet_summary",
    "atmosphere_description",
    "habitability_notes",
    "scientific_relevance",
    "artist_concept_prompt",
)
_MAX_SECTION_WORDS = 150


@dataclass(frozen=True)
class ExoplanetReport:
    """Human-readable educational report for an exoplanet atmosphere chart."""

    planet_summary: str
    atmosphere_description: str
    habitability_notes: str
    scientific_relevance: str
    artist_concept_prompt: str


class ExoplanetReporter:
    """Generate educational K2-18 b atmosphere report sections with Gemini."""

    def __init__(
        self, gemini_service: GeminiService, logger: Optional[logging.Logger] = None
    ) -> None:
        self._gemini_service = gemini_service
        self._logger = logger or _LOGGER

    def generate(self, analysis: ExoplanetAtmosphereResult) -> ExoplanetReport:
        """Generate a structured report from validated atmosphere chart analysis."""
        prompt = self._build_prompt(analysis)
        response = self._gemini_service.generate_text(prompt)
        if not response.ok:
            error = response.error.message if response.error else "Unknown error"
            self._logger.error("ExoplanetReporter failed: %s", error)
            raise RuntimeError(error)

        payload = self._parse_response(response)
        report = self._validate_payload(payload)
        self._logger.info("ExoplanetReporter generated report for %s", analysis.planet)
        return report

    def _build_prompt(self, analysis: ExoplanetAtmosphereResult) -> str:
        return (
            "You are AstroLens ExoplanetReporter. Generate an educational, "
            "scientific-tone report from the validated K2-18 b chart analysis. "
            "Do not make unsupported scientific claims, do not describe the output "
            "as a real measurement, and explicitly mention uncertainty where "
            "appropriate. Return ONLY valid JSON with no markdown or extra text. "
            "Each section must be 150 words or fewer. Schema: "
            "{\"planet_summary\": string, \"atmosphere_description\": string, "
            "\"habitability_notes\": string, \"scientific_relevance\": string, "
            "\"artist_concept_prompt\": string}. The artist_concept_prompt must "
            "be a prompt only; do not generate or request an image. "
            "Validated ExoplanetSpectrumAgent output:\n"
            f"{json.dumps(asdict(analysis), indent=2)}"
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
                self._logger.error("ExoplanetReporter could not parse JSON output.")
                raise ValueError("Invalid JSON response from Gemini")
            self._logger.warning("ExoplanetReporter trimming non-JSON response content.")
            try:
                return json.loads(raw_text[start : end + 1])
            except json.JSONDecodeError as exc:
                raise ValueError("Invalid JSON response from Gemini") from exc

    def _validate_payload(self, payload: dict) -> ExoplanetReport:
        missing_fields = [field for field in _REPORT_FIELDS if field not in payload]
        if missing_fields:
            raise ValueError(
                "Exoplanet report is missing required fields: "
                f"{', '.join(missing_fields)}"
            )

        values = {
            field: _limit_words(str(payload.get(field, "")).strip())
            for field in _REPORT_FIELDS
        }
        return ExoplanetReport(**values)


def _limit_words(text: str, max_words: int = _MAX_SECTION_WORDS) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])
