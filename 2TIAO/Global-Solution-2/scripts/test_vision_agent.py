"""CLI smoke test for VisionAgent."""

import argparse
import json
import logging
from typing import Optional

from bootstrap import add_repo_root

add_repo_root()

from src.agents.vision_agent import VisionAgent
from src.services.gemini_service import GeminiService
from src.storage.result_storage_service import ResultStorageService


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="VisionAgent smoke test")
    parser.add_argument("image_path", help="Path to an astronomical image")
    args = parser.parse_args(argv)

    service = GeminiService()
    agent = VisionAgent(service)
    storage_service = ResultStorageService()
    result = agent.analyze(args.image_path)
    storage_service.save_result(args.image_path, result)

    print(
        json.dumps(
            {
                "classification": result.classification,
                "confidence": result.confidence,
                "description": result.description,
                "astronomical_objects": result.astronomical_objects,
                "scientific_tags": result.scientific_tags,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
