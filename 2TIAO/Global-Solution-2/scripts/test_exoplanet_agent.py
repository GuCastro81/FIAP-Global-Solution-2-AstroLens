"""CLI smoke test for the isolated K2-18 b ExoplanetSpectrumAgent."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from typing import Optional

from bootstrap import add_repo_root

REPO_ROOT = add_repo_root()

from src.agents.exoplanet_spectrum_agent import ExoplanetSpectrumAgent
from src.services.gemini_service import GeminiService
from src.storage.result_storage_service import ResultStorageService

K2_18B_IMAGE_PATH = (
    REPO_ROOT
    / "data"
    / "images"
    / "exoplanets"
    / "k2-18b"
    / "atmosphere_composition.jpg"
)


def main(argv: Optional[list[str]] = None) -> int:
    del argv
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if not K2_18B_IMAGE_PATH.exists():
        raise FileNotFoundError(f"K2-18 b image not found: {K2_18B_IMAGE_PATH}")
    if K2_18B_IMAGE_PATH.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        raise ValueError(
            "Unsupported K2-18 b image format. Supported formats: .jpg, .jpeg, .png."
        )

    service = GeminiService()
    agent = ExoplanetSpectrumAgent(service)
    storage_service = ResultStorageService()

    result = agent.analyze(K2_18B_IMAGE_PATH)
    storage_service.save_result(K2_18B_IMAGE_PATH, result)

    print(json.dumps(asdict(result), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
