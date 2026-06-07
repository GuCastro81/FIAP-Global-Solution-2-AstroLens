"""CLI smoke test for ScienceWriterAgent."""

import argparse
import json
import logging
from typing import Optional

from bootstrap import add_repo_root

repo_root = add_repo_root()

from src.agents.research_agent import ResearchResult
from src.agents.science_writer_agent import ScienceWriterAgent
from src.agents.vision_agent import VisionAnalysisResult
from src.services.gemini_service import GeminiService
from src.storage.result_storage_service import ResultStorageService


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="AstroLens AI science writer test")
    parser.add_argument(
        "image_path",
        nargs="?",
        default=str(repo_root / "data" / "images" / "andromeda.jpg"),
        help="Path to the image whose stored results should be used",
    )
    args = parser.parse_args(argv)

    storage_service = ResultStorageService()
    vision_result = storage_service.load_result(args.image_path, VisionAnalysisResult)
    research_result = storage_service.load_result(args.image_path, ResearchResult)

    agent = ScienceWriterAgent(GeminiService())
    report = agent.write(vision_result, research_result)
    storage_service.save_result(args.image_path, report)

    print(
        json.dumps(
            {
                "scientific_summary": report.scientific_summary,
                "space_exploration_importance": report.space_exploration_importance,
                "earth_impact": report.earth_impact,
                "curiosities": report.curiosities,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
