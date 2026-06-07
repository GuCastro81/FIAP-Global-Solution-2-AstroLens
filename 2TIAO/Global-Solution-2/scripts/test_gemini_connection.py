"""Smoke test for GeminiService connectivity and workflows."""

import argparse
import logging
import os
from typing import Optional

from bootstrap import add_repo_root

repo_root = add_repo_root()

from src.services.gemini_service import GeminiService, load_env_file


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def _run_text_test(service: GeminiService, prompt: str) -> None:
    response = service.generate_text(prompt)
    if response.ok:
        logging.info("Text generation ok. Response length: %s", len(response.data.text))
    else:
        logging.error("Text generation failed: %s", response.error)


def _run_image_test(service: GeminiService, prompt: str, image_path: str) -> None:
    response = service.analyze_image(prompt, image_path=image_path)
    if response.ok:
        logging.info("Image analysis ok. Response length: %s", len(response.data.text))
    else:
        logging.error("Image analysis failed: %s", response.error)


def main(argv: Optional[list[str]] = None) -> int:
    _configure_logging()

    parser = argparse.ArgumentParser(description="Gemini service smoke test")
    parser.add_argument("--prompt", default="Describe the image.")
    parser.add_argument("--text-only", action="store_true")
    parser.add_argument("--image-path", default=None)
    args = parser.parse_args(argv)

    load_env_file(str(repo_root / ".env"))
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logging.warning(
            "GEMINI_API_KEY or GOOGLE_API_KEY is not set. Calls will likely fail."
        )

    service = GeminiService()
    _run_text_test(service, args.prompt)

    if not args.text_only and args.image_path:
        _run_image_test(service, args.prompt, args.image_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
