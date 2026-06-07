"""Unit tests for ResultStorageService."""

import json
import tempfile
import unittest
from pathlib import Path

from src.agents.research_agent import ResearchResult
from src.agents.science_writer_agent import ScienceReport
from src.agents.vision_agent import VisionAnalysisResult
from src.storage.result_storage_service import ResultStorageService


class TestResultStorageService(unittest.TestCase):
    def test_save_result_creates_image_folder_and_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ResultStorageService(base_dir=temp_dir)

            output_path = service.save_result("images/andromeda.jpg", _vision_result())

            self.assertEqual(
                output_path,
                Path(temp_dir) / "andromeda" / "vision_result.json",
            )
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["classification"], "Galaxy")
            self.assertEqual(payload["scientific_tags"], ["Spiral galaxy"])

    def test_save_result_maps_all_agent_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ResultStorageService(base_dir=temp_dir)

            vision_path = service.save_result("andromeda.jpg", _vision_result())
            research_path = service.save_result("andromeda.jpg", _research_result())
            report_path = service.save_result("andromeda.jpg", _science_report())

            self.assertEqual(vision_path.name, "vision_result.json")
            self.assertEqual(research_path.name, "research_result.json")
            self.assertEqual(report_path.name, "science_report.json")

    def test_load_result_reconstructs_dataclass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ResultStorageService(base_dir=temp_dir)
            service.save_result("andromeda.jpg", _research_result())

            result = service.load_result("andromeda.jpg", ResearchResult)

            self.assertIsInstance(result, ResearchResult)
            self.assertEqual(result.topic, "Galaxy")
            self.assertEqual(result.related_tags, ["Spiral galaxy", "Dark matter"])

    def test_load_result_accepts_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ResultStorageService(base_dir=temp_dir)
            service.save_result("andromeda.jpg", _science_report())

            result = service.load_result("andromeda.jpg", "science_report")

            self.assertIsInstance(result, ScienceReport)
            self.assertIn("star formation", result.scientific_summary)

    def test_save_result_rejects_unsupported_type(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ResultStorageService(base_dir=temp_dir)

            with self.assertRaises(ValueError):
                service.save_result("andromeda.jpg", {"not": "a supported result"})


def _vision_result() -> VisionAnalysisResult:
    return VisionAnalysisResult(
        classification="Galaxy",
        confidence=0.98,
        description="Andromeda appears as a face-on spiral galaxy.",
        astronomical_objects=["Spiral Galaxy", "Stars"],
        scientific_tags=["Spiral galaxy"],
    )


def _research_result() -> ResearchResult:
    return ResearchResult(
        topic="Galaxy",
        definition="A galaxy is a gravitationally bound system of stars.",
        scientific_importance="Galaxy rotation curves provide evidence for dark matter.",
        space_exploration_relevance="Galactic structure informs radiation planning.",
        earth_impact="Galaxy research advances image processing.",
        source="galaxy.md",
        related_tags=["Spiral galaxy", "Dark matter"],
    )


def _science_report() -> ScienceReport:
    return ScienceReport(
        scientific_summary="A spiral galaxy with active star formation.",
        space_exploration_importance="It helps map mission radiation environments.",
        earth_impact="It improves image processing and sensors.",
        curiosities="The Milky Way is also a spiral galaxy.",
    )


if __name__ == "__main__":
    unittest.main()
