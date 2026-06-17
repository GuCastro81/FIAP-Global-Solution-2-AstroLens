"""Research agent that loads knowledge base context for a classification."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from src.agents.vision_agent import VisionAnalysisResult

_LOGGER = logging.getLogger(__name__)

_CLASSIFICATION_TO_FILE = {
    "Galaxy": "galaxy.md",
    "Nebula": "nebula.md",
    "Star": "star.md",
    "Star Cluster": "star_cluster.md",
    "Planet": "planet.md",
}


@dataclass(frozen=True)
class ResearchResult:
    """Structured output for research context lookup."""

    topic: str
    definition: str
    scientific_importance: str
    space_exploration_relevance: str
    earth_impact: str
    source: str
    related_tags: List[str]


class ResearchAgent:
    """Research agent that maps classification to knowledge base context."""

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self._logger = logger or _LOGGER

    def research(self, analysis: VisionAnalysisResult) -> ResearchResult:
        """Load knowledge base context for the classification."""
        classification = analysis.classification
        if classification not in _CLASSIFICATION_TO_FILE:
            raise ValueError(f"Unsupported classification: {classification}")

        file_name = _CLASSIFICATION_TO_FILE[classification]
        kb_path = _knowledge_base_dir() / file_name
        if not kb_path.exists():
            raise FileNotFoundError(f"Knowledge base file not found: {kb_path}")

        markdown = kb_path.read_text(encoding="utf-8")
        parsed = _parse_markdown_knowledge(markdown)
        related_tags = list(analysis.scientific_tags)
        self._logger.info("ResearchAgent loaded %s", file_name)

        return ResearchResult(
            topic=parsed["topic"] or classification,
            definition=parsed["definition"],
            scientific_importance=parsed["scientific_importance"],
            space_exploration_relevance=parsed["space_exploration_relevance"],
            earth_impact=parsed["earth_impact"],
            source=file_name,
            related_tags=related_tags,
        )


def _knowledge_base_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / "data" / "knowledge_base"


_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_SECTION_ALIASES = {
    "definition": "definition",
    "scientific_importance": "scientific_importance",
    "relevance_for_space_exploration": "space_exploration_relevance",
    "space_exploration_relevance": "space_exploration_relevance",
    "impact_on_earth": "earth_impact",
    "earth_impact": "earth_impact",
}
_OUTPUT_FIELDS = (
    "definition",
    "scientific_importance",
    "space_exploration_relevance",
    "earth_impact",
)


def _parse_markdown_knowledge(markdown: str) -> Dict[str, str]:
    """Parse topic and known sections from markdown headings."""
    topic = ""
    current_key: Optional[str] = None
    sections = {field: [] for field in _OUTPUT_FIELDS}

    for raw_line in markdown.splitlines():
        heading_match = _HEADING_PATTERN.match(raw_line)
        if heading_match:
            level = len(heading_match.group(1))
            heading = heading_match.group(2).strip()
            normalized_heading = _normalize_heading(heading)

            if level == 1 and not topic:
                topic = heading
                current_key = None
                continue

            current_key = _SECTION_ALIASES.get(normalized_heading)
            continue

        if current_key:
            sections[current_key].append(raw_line)

    parsed = {"topic": topic}
    for field, lines in sections.items():
        parsed[field] = "\n".join(lines).strip()
    return parsed


def _normalize_heading(heading: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", heading.lower())).strip("_")
