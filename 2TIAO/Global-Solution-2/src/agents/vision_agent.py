"""Vision agent that classifies astronomical images using Gemini Vision."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

from src.services.gemini_service import GeminiResponse, GeminiService

_LOGGER = logging.getLogger(__name__)
_ALLOWED_CLASSIFICATIONS = {
    "Galaxy",
    "Nebula",
    "Star Cluster",
    "Star",
    "Planet",
    "Other",
}


@dataclass(frozen=True)
class VisionAnalysisResult:
    """Structured output for astronomical image classification."""

    classification: str
    confidence: float
    description: str
    astronomical_objects: List[str]
    scientific_tags: List[str]


def save_analysis_result(image_path: str, result: VisionAnalysisResult) -> Path:
    """Save a VisionAnalysisResult to data/analysis_results as JSON."""
    output_dir = _analysis_results_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    image_name = Path(image_path).stem
    output_path = output_dir / f"{image_name}_analysis.json"
    payload = {
        "classification": result.classification,
        "confidence": result.confidence,
        "description": result.description,
        "astronomical_objects": result.astronomical_objects,
        "scientific_tags": result.scientific_tags,
    }

    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def load_analysis_result(image_path: str) -> VisionAnalysisResult:
    """Load a VisionAnalysisResult from data/analysis_results JSON."""
    output_dir = _analysis_results_dir()
    image_name = Path(image_path).stem
    output_path = output_dir / f"{image_name}_analysis.json"
    raw_text = output_path.read_text(encoding="utf-8")
    payload = json.loads(raw_text)

    return VisionAnalysisResult(
        classification=str(payload.get("classification", "")),
        confidence=float(payload.get("confidence", 0.0)),
        description=str(payload.get("description", "")),
        astronomical_objects=[
            str(item) for item in payload.get("astronomical_objects", [])
        ],
        scientific_tags=[str(item) for item in payload.get("scientific_tags", [])],
    )


class VisionAgent:
    """Vision agent that calls Gemini Vision and validates results."""

    def __init__(
        self, gemini_service: GeminiService, logger: Optional[logging.Logger] = None
    ) -> None:
        self._gemini_service = gemini_service
        self._logger = logger or _LOGGER

    def analyze(self, image_path: str) -> VisionAnalysisResult:
        """Analyze an astronomical image and return structured classification."""
        prompt = self._build_prompt()
        response = self._gemini_service.analyze_image(prompt, image_path=image_path)
        if not response.ok:
            error = response.error.message if response.error else "Unknown error"
            self._logger.error("VisionAgent failed: %s", error)
            raise RuntimeError(error)

        payload = self._parse_response(response)
        result = self._validate_payload(payload)
        self._logger.info(
            "VisionAgent classification=%s confidence=%s",
            result.classification,
            result.confidence,
        )
        return result

    def _build_prompt(self) -> str:
        return (
            "You are an astronomy image classifier. "
            "Return ONLY a JSON object with the following schema and no extra text. "
            "Schema: {\"classification\": string, \"confidence\": number, "
            "\"description\": string, \"astronomical_objects\": string[], "
            "\"scientific_tags\": string[]} "
            "Allowed classification values: Galaxy, Nebula, Star Cluster, Star, Planet, Other. "
            "confidence must be a number between 0 and 1."
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
                self._logger.error("VisionAgent could not parse JSON output.")
                raise ValueError("Invalid JSON response from Gemini")
            self._logger.warning("VisionAgent trimming non-JSON response content.")
            return json.loads(raw_text[start : end + 1])

    def _validate_payload(self, payload: dict) -> VisionAnalysisResult:
        classification = payload.get("classification")
        if classification not in _ALLOWED_CLASSIFICATIONS:
            raise ValueError(f"Invalid classification: {classification}")

        confidence = float(payload.get("confidence", 0))
        if not 0 <= confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")

        description = str(payload.get("description", "")).strip()
        astronomical_objects = list(payload.get("astronomical_objects", []))
        scientific_tags = list(payload.get("scientific_tags", []))

        return VisionAnalysisResult(
            classification=classification,
            confidence=confidence,
            description=description,
            astronomical_objects=[str(item) for item in astronomical_objects],
            scientific_tags=[str(item) for item in scientific_tags],
        )


def _analysis_results_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / "data" / "analysis_results"
