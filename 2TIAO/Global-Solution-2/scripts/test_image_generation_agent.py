"""CLI smoke test for optional ImageGenerationAgent."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Optional

from bootstrap import add_repo_root

add_repo_root()

from src.agents.image_generation_agent import ImageGenerationAgent
from src.reporting.artist_concept_prompt_enhancer import ArtistConceptPromptEnhancer
from src.reporting.exoplanet_reporter import ExoplanetReport
from src.services.gemini_service import GeminiService


def main(argv: Optional[list[str]] = None) -> int:
    del argv
    report = ExoplanetReport(
        planet_summary="K2-18 b is a sub-Neptune exoplanet studied with JWST.",
        atmosphere_description=(
            "The chart highlights methane and carbon dioxide, with dimethyl "
            "sulfide treated as an uncertain candidate atmospheric feature."
        ),
        habitability_notes=(
            "Potential habitability remains uncertain and does not confirm life."
        ),
        scientific_relevance=(
            "JWST observations help communicate exoplanet atmosphere science."
        ),
        artist_concept_prompt=(
            "A scientifically plausible artist concept of K2-18 b orbiting a "
            "red dwarf star, NASA-style space illustration."
        ),
    )
    enhanced_prompt = ArtistConceptPromptEnhancer().enhance(
        planet_name="K2-18 b",
        detected_molecules=["Methane", "Carbon Dioxide", "Dimethyl Sulfide"],
        exoplanet_report=report,
        original_artist_concept_prompt=report.artist_concept_prompt,
    )
    result = ImageGenerationAgent(GeminiService()).generate(
        enhanced_artist_prompt=enhanced_prompt.enhanced_artist_prompt,
        negative_prompt=enhanced_prompt.negative_prompt,
        visual_style=enhanced_prompt.visual_style,
    )
    print(json.dumps(asdict(result), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
