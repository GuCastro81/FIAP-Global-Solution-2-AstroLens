"""Science writer agent that turns vision and research data into reports."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from typing import Optional

from src.agents.research_agent import ResearchResult
from src.agents.vision_agent import VisionAnalysisResult
from src.services.gemini_service import GeminiResponse, GeminiService

_LOGGER = logging.getLogger(__name__)
_REPORT_FIELDS = (
    "scientific_summary",
    "space_exploration_importance",
    "earth_impact",
    "curiosities",
)
_MAX_SECTION_WORDS = 250


@dataclass(frozen=True)
class ScienceReport:
    """Structured science communication report."""

    scientific_summary: str
    space_exploration_importance: str
    earth_impact: str
    curiosities: str


class ScienceWriterAgent:
    """Generate concise science reports from vision and research outputs."""

    def __init__(
        self, gemini_service: GeminiService, logger: Optional[logging.Logger] = None
    ) -> None:
        self._gemini_service = gemini_service
        self._logger = logger or _LOGGER

    def write(
        self, vision_result: VisionAnalysisResult, research_result: ResearchResult
    ) -> ScienceReport:
        """Generate a structured science report."""
        prompt = self._build_prompt(vision_result, research_result)
        response = self._gemini_service.generate_text(prompt)
        if not response.ok:
            error = response.error.message if response.error else "Unknown error"
            self._logger.error("ScienceWriterAgent failed: %s", error)
            raise RuntimeError(error)

        payload = self._parse_response(response)
        report = self._validate_payload(payload)
        self._logger.info(
            "ScienceWriterAgent generated report for %s", research_result.topic
        )
        return report

    def _build_prompt(
        self, vision_result: VisionAnalysisResult, research_result: ResearchResult
    ) -> str:
        vision_payload = asdict(vision_result)
        research_payload = asdict(research_result)
        return (
            "You are a science writer for AstroLens AI. "
            "Use both the VisionAgent output and ResearchAgent output to write a concise, "
            "accurate astronomy report. Return ONLY valid JSON with no markdown or extra text. "
            "Each section must be 250 words or fewer. "
            "Schema: {\"scientific_summary\": string, "
            "\"space_exploration_importance\": string, \"earth_impact\": string, "
            "\"curiosities\": string}. "
            "VisionAgent output:\n"
            f"{json.dumps(vision_payload, indent=2)}\n\n"
            "ResearchAgent output:\n"
            f"{json.dumps(research_payload, indent=2)}"
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
                self._logger.error("ScienceWriterAgent could not parse JSON output.")
                raise ValueError("Invalid JSON response from Gemini")
            self._logger.warning(
                "ScienceWriterAgent trimming non-JSON response content."
            )
            return json.loads(raw_text[start : end + 1])

    def _validate_payload(self, payload: dict) -> ScienceReport:
        missing_fields = [field for field in _REPORT_FIELDS if field not in payload]
        if missing_fields:
            raise ValueError(
                f"Science report is missing required fields: {', '.join(missing_fields)}"
            )

        values = {
            field: _limit_words(str(payload.get(field, "")).strip())
            for field in _REPORT_FIELDS
        }
        return ScienceReport(**values)


def _limit_words(text: str, max_words: int = _MAX_SECTION_WORDS) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])
