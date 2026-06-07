"""End-to-end test pipeline for VisionAgent and ResearchAgent."""

import argparse
from dataclasses import asdict
import json
import logging
from typing import Optional

from bootstrap import add_repo_root

repo_root = add_repo_root()

from src.agents.research_agent import ResearchAgent
from src.agents.vision_agent import (
    VisionAgent,
    VisionAnalysisResult,
)
from src.services.gemini_service import GeminiService
from src.storage.result_storage_service import ResultStorageService


def _format_vision_output(result: VisionAnalysisResult) -> dict:
    return {
        "classification": result.classification,
        "confidence": result.confidence,
        "description": result.description,
        "astronomical_objects": result.astronomical_objects,
        "scientific_tags": result.scientific_tags,
    }


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="AstroLens AI pipeline test")
    parser.add_argument("image_path", help="Path to an astronomical image")
    args = parser.parse_args(argv)

    service = GeminiService()
    vision_agent = VisionAgent(service)
    research_agent = ResearchAgent()
    storage_service = ResultStorageService()

    vision_result = vision_agent.analyze(args.image_path)
    research_result = research_agent.research(vision_result)

    vision_payload = _format_vision_output(vision_result)
    research_payload = asdict(research_result)

    storage_service.save_result(args.image_path, vision_result)
    storage_service.save_result(args.image_path, research_result)

    print("=== Vision Agent ===")
    print(json.dumps(vision_payload, indent=2))
    print("\n=== Research Agent ===")
    print(json.dumps(research_payload, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
