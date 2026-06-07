"""Artist concept prompt enhancement for exoplanet image generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Mapping

from src.reporting.exoplanet_reporter import ExoplanetReport

_CANONICAL_PLANET = "K2-18 b"
_NEGATIVE_PROMPT_ITEMS = (
    "fantasy landscape",
    "alien cities",
    "spaceships",
    "humanoids",
    "exaggerated colors",
    "cartoon style",
    "impossible surface details",
    "unsupported biological claims",
)


@dataclass(frozen=True)
class EnhancedArtistConceptPrompt:
    """Structured enhanced prompt output for future image generation."""

    enhanced_artist_prompt: str
    visual_style: str
    scientific_constraints: list[str]
    negative_prompt: str


class ArtistConceptPromptEnhancer:
    """Create a richer scientifically cautious image-generation prompt."""

    def enhance(
        self,
        *,
        planet_name: str,
        detected_molecules: list[str],
        exoplanet_report: ExoplanetReport | Mapping[str, Any],
        original_artist_concept_prompt: str,
    ) -> EnhancedArtistConceptPrompt:
        """Enhance an existing K2-18 b artist concept prompt without generating images."""
        report = _report_to_mapping(exoplanet_report)
        molecule_context = _format_molecules(detected_molecules)
        visual_style = (
            "NASA/JWST-inspired artist concept, scientifically plausible, "
            "realistic astrophysics, cinematic lighting, high detail, "
            "educational scientific visualization"
        )
        scientific_constraints = [
            "Represent K2-18 b as a sub-Neptune exoplanet, not an Earth twin.",
            "Include methane and carbon dioxide as atmospheric components.",
            "Describe dimethyl sulfide (DMS) only as an uncertain candidate atmospheric feature.",
            "Preserve uncertainty around habitability and atmospheric interpretation.",
            "Do not claim confirmed life, confirmed oceans, or confirmed surface conditions.",
            "Show any liquid reservoirs or ocean-like regions as possible and hidden beneath clouds.",
        ]

        enhanced_prompt = (
            f"{original_artist_concept_prompt.strip()} Enhanced prompt: Create a "
            f"scientifically plausible NASA/JWST-inspired artist concept of "
            f"{_CANONICAL_PLANET}, a sub-Neptune exoplanet. Show a dense "
            "atmosphere with atmospheric haze, layered clouds, and red dwarf "
            "star illumination across the planet limb, set against a deep "
            "space background. Include atmospheric context for methane and "
            "carbon dioxide, while presenting dimethyl sulfide (DMS) as a "
            "possible, uncertain candidate atmospheric feature rather than a "
            "confirmed biosignature. Suggest potential liquid reservoirs or "
            "ocean-like regions hidden beneath clouds without showing definite "
            "surface oceans or claiming habitability. Use realistic "
            "astrophysics, cinematic lighting, high detail, and educational "
            "scientific visualization aesthetics. Detected molecule context: "
            f"{molecule_context}. Report context: planet summary - "
            f"{report.get('planet_summary', '')}; atmosphere - "
            f"{report.get('atmosphere_description', '')}; habitability notes - "
            f"{report.get('habitability_notes', '')}."
        )

        return EnhancedArtistConceptPrompt(
            enhanced_artist_prompt=_normalize_whitespace(enhanced_prompt),
            visual_style=visual_style,
            scientific_constraints=scientific_constraints,
            negative_prompt=", ".join(_NEGATIVE_PROMPT_ITEMS),
        )


def _report_to_mapping(
    exoplanet_report: ExoplanetReport | Mapping[str, Any],
) -> Mapping[str, Any]:
    if is_dataclass(exoplanet_report):
        return asdict(exoplanet_report)
    return exoplanet_report


def _format_molecules(detected_molecules: list[str]) -> str:
    cleaned = [str(item).strip() for item in detected_molecules if str(item).strip()]
    if not cleaned:
        return "methane, carbon dioxide, and uncertain candidate dimethyl sulfide"
    return ", ".join(cleaned)


def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())
