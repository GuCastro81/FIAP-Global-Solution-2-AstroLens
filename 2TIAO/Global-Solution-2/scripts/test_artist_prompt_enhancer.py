"""CLI smoke test for ArtistConceptPromptEnhancer."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Optional

from bootstrap import add_repo_root

add_repo_root()

from src.reporting.artist_concept_prompt_enhancer import ArtistConceptPromptEnhancer
from src.reporting.exoplanet_reporter import ExoplanetReport


def main(argv: Optional[list[str]] = None) -> int:
    del argv
    report = ExoplanetReport(
        planet_summary="K2-18 b is a sub-Neptune exoplanet studied with JWST.",
        atmosphere_description=(
            "The chart highlights methane and carbon dioxide, with dimethyl "
            "sulfide treated as an uncertain candidate atmospheric feature."
        ),
        habitability_notes=(
            "The visualization supports cautious discussion of potential "
            "habitability, but does not confirm life or oceans."
        ),
        scientific_relevance=(
            "K2-18 b is useful for explaining how JWST studies exoplanet atmospheres."
        ),
        artist_concept_prompt=(
            "A scientifically plausible artist concept of K2-18 b, a "
            "sub-Neptune exoplanet with methane and carbon dioxide, orbiting "
            "a red dwarf star, NASA-style space illustration."
        ),
    )

    enhanced = ArtistConceptPromptEnhancer().enhance(
        planet_name="K2-18 b",
        detected_molecules=["Methane", "Carbon Dioxide", "Dimethyl Sulfide"],
        exoplanet_report=report,
        original_artist_concept_prompt=report.artist_concept_prompt,
    )
    print(json.dumps(asdict(enhanced), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
