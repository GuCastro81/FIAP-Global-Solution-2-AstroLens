"""Unit tests for ArtistConceptPromptEnhancer."""

from __future__ import annotations

import unittest
from dataclasses import asdict

from src.reporting.artist_concept_prompt_enhancer import (
    ArtistConceptPromptEnhancer,
    EnhancedArtistConceptPrompt,
)
from src.reporting.exoplanet_reporter import ExoplanetReport


class TestArtistConceptPromptEnhancer(unittest.TestCase):
    def setUp(self) -> None:
        self.result = ArtistConceptPromptEnhancer().enhance(
            planet_name="K2-18 b",
            detected_molecules=["Methane", "Carbon Dioxide", "Dimethyl Sulfide"],
            exoplanet_report=_mock_report(),
            original_artist_concept_prompt=(
                "A scientifically plausible artist concept of K2-18 b."
            ),
        )

    def test_output_schema_is_valid(self) -> None:
        self.assertIsInstance(self.result, EnhancedArtistConceptPrompt)
        payload = asdict(self.result)

        self.assertEqual(
            set(payload),
            {
                "enhanced_artist_prompt",
                "visual_style",
                "scientific_constraints",
                "negative_prompt",
            },
        )
        self.assertIsInstance(payload["enhanced_artist_prompt"], str)
        self.assertIsInstance(payload["visual_style"], str)
        self.assertIsInstance(payload["scientific_constraints"], list)
        self.assertIsInstance(payload["negative_prompt"], str)

    def test_enhanced_prompt_contains_planet_identity(self) -> None:
        self.assertIn("K2-18 b", self.result.enhanced_artist_prompt)

    def test_enhanced_prompt_mentions_methane_and_carbon_dioxide(self) -> None:
        prompt = self.result.enhanced_artist_prompt.lower()

        self.assertIn("methane", prompt)
        self.assertIn("carbon dioxide", prompt)

    def test_dms_is_described_with_uncertainty(self) -> None:
        prompt = self.result.enhanced_artist_prompt.lower()

        self.assertIn("dimethyl sulfide", prompt)
        self.assertIn("dms", prompt)
        self.assertIn("uncertain", prompt)
        self.assertIn("candidate atmospheric feature", prompt)

    def test_prompt_does_not_claim_confirmed_life(self) -> None:
        prompt = self.result.enhanced_artist_prompt.lower()

        self.assertNotIn("confirmed life", prompt)
        self.assertNotIn("definitely has life", prompt)
        self.assertNotIn("life exists", prompt)

    def test_negative_prompt_contains_forbidden_visual_elements(self) -> None:
        negative_prompt = self.result.negative_prompt.lower()

        for forbidden in (
            "fantasy landscape",
            "alien cities",
            "spaceships",
            "humanoids",
            "exaggerated colors",
            "cartoon style",
            "impossible surface details",
            "unsupported biological claims",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertIn(forbidden, negative_prompt)


def _mock_report() -> ExoplanetReport:
    return ExoplanetReport(
        planet_summary="K2-18 b is a sub-Neptune exoplanet.",
        atmosphere_description=(
            "The atmosphere includes methane and carbon dioxide, with DMS "
            "treated as uncertain."
        ),
        habitability_notes=(
            "Habitability remains uncertain and should not be treated as confirmed."
        ),
        scientific_relevance=(
            "JWST data helps communicate exoplanet atmospheric science."
        ),
        artist_concept_prompt=(
            "A NASA-style artist concept of K2-18 b orbiting a red dwarf star."
        ),
    )


if __name__ == "__main__":
    unittest.main()
