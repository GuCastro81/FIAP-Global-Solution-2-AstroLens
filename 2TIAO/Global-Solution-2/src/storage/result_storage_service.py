"""Result storage service for agent outputs."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, Type, Union

from src.agents.exoplanet_spectrum_agent import ExoplanetAtmosphereResult
from src.agents.research_agent import ResearchResult
from src.agents.science_writer_agent import ScienceReport
from src.agents.vision_agent import VisionAnalysisResult
from src.reporting.exoplanet_reporter import ExoplanetReport

ResultType = Union[
    VisionAnalysisResult,
    ResearchResult,
    ScienceReport,
    ExoplanetAtmosphereResult,
    ExoplanetReport,
]
ResultClass = Union[
    Type[VisionAnalysisResult],
    Type[ResearchResult],
    Type[ScienceReport],
    Type[ExoplanetAtmosphereResult],
    Type[ExoplanetReport],
]

_RESULT_FILES: Dict[type, str] = {
    VisionAnalysisResult: "vision_result.json",
    ResearchResult: "research_result.json",
    ScienceReport: "science_report.json",
    ExoplanetAtmosphereResult: "exoplanet_atmosphere_result.json",
    ExoplanetReport: "exoplanet_report.json",
}
_RESULT_ALIASES: Dict[str, ResultClass] = {
    "vision": VisionAnalysisResult,
    "vision_result": VisionAnalysisResult,
    "research": ResearchResult,
    "research_result": ResearchResult,
    "science": ScienceReport,
    "science_report": ScienceReport,
    "exoplanet": ExoplanetAtmosphereResult,
    "exoplanet_atmosphere": ExoplanetAtmosphereResult,
    "exoplanet_atmosphere_result": ExoplanetAtmosphereResult,
    "exoplanet_report": ExoplanetReport,
}


class ResultStorageService:
    """Save and load structured outputs from AstroLens agents."""

    def __init__(self, base_dir: Path | str | None = None) -> None:
        self.base_dir = Path(base_dir) if base_dir else _default_results_dir()

    def save_result(self, image_path: Path | str, result: ResultType) -> Path:
        """Save an agent result under data/analysis_results/<image_name>/."""
        result_class = type(result)
        file_name = _RESULT_FILES.get(result_class)
        if file_name is None:
            raise ValueError(f"Unsupported result type: {result_class.__name__}")
        if not is_dataclass(result):
            raise ValueError("Result must be a dataclass instance.")

        output_dir = self._image_result_dir(image_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / file_name
        output_path.write_text(
            json.dumps(asdict(result), indent=2),
            encoding="utf-8",
        )
        return output_path

    def load_result(
        self, image_path: Path | str, result_type: ResultClass | str
    ) -> ResultType:
        """Load a previous agent result from data/analysis_results/<image_name>/."""
        result_class = _resolve_result_class(result_type)
        file_name = _RESULT_FILES[result_class]
        result_path = self._image_result_dir(image_path) / file_name
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        return _build_result(result_class, payload)

    def _image_result_dir(self, image_path: Path | str) -> Path:
        image_name = Path(image_path).stem
        if not image_name:
            raise ValueError("Image path must include a file name.")
        return self.base_dir / image_name


def _resolve_result_class(result_type: ResultClass | str) -> ResultClass:
    if isinstance(result_type, str):
        normalized = result_type.strip().lower()
        result_class = _RESULT_ALIASES.get(normalized)
        if result_class is None:
            raise ValueError(f"Unsupported result type: {result_type}")
        return result_class

    if result_type not in _RESULT_FILES:
        raise ValueError(f"Unsupported result type: {result_type.__name__}")
    return result_type


def _build_result(result_class: ResultClass, payload: Dict[str, Any]) -> ResultType:
    if result_class is VisionAnalysisResult:
        return VisionAnalysisResult(
            classification=str(payload.get("classification", "")),
            confidence=float(payload.get("confidence", 0.0)),
            description=str(payload.get("description", "")),
            astronomical_objects=[
                str(item) for item in payload.get("astronomical_objects", [])
            ],
            scientific_tags=[str(item) for item in payload.get("scientific_tags", [])],
        )

    if result_class is ResearchResult:
        return ResearchResult(
            topic=str(payload.get("topic", "")),
            definition=str(payload.get("definition", "")),
            scientific_importance=str(payload.get("scientific_importance", "")),
            space_exploration_relevance=str(
                payload.get("space_exploration_relevance", "")
            ),
            earth_impact=str(payload.get("earth_impact", "")),
            source=str(payload.get("source", "")),
            related_tags=[str(item) for item in payload.get("related_tags", [])],
        )

    if result_class is ScienceReport:
        return ScienceReport(
            scientific_summary=str(payload.get("scientific_summary", "")),
            space_exploration_importance=str(
                payload.get("space_exploration_importance", "")
            ),
            earth_impact=str(payload.get("earth_impact", "")),
            curiosities=str(payload.get("curiosities", "")),
        )

    if result_class is ExoplanetAtmosphereResult:
        return ExoplanetAtmosphereResult(
            planet=str(payload.get("planet", "")),
            planet_type=str(payload.get("planet_type", "")),
            detected_molecules=[
                str(item) for item in payload.get("detected_molecules", [])
            ],
            scientific_confidence=float(payload.get("scientific_confidence", 0.0)),
            summary=str(payload.get("summary", "")),
        )

    if result_class is ExoplanetReport:
        return ExoplanetReport(
            planet_summary=str(payload.get("planet_summary", "")),
            atmosphere_description=str(payload.get("atmosphere_description", "")),
            habitability_notes=str(payload.get("habitability_notes", "")),
            scientific_relevance=str(payload.get("scientific_relevance", "")),
            artist_concept_prompt=str(payload.get("artist_concept_prompt", "")),
        )

    raise ValueError(f"Unsupported result type: {result_class.__name__}")


def _default_results_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / "data" / "analysis_results"
