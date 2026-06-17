"""Optional image generation agent using Google Gemini/Imagen when available."""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from src.services.gemini_service import GeminiResponse, GeminiService

try:
    from google.genai import types

    _GENAI_TYPES_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency guard
    types = None
    _GENAI_TYPES_AVAILABLE = False

_LOGGER = logging.getLogger(__name__)
_DEFAULT_IMAGEN_MODEL = "imagen-4.0-generate-001"
_UNAVAILABLE_MESSAGE = (
    "Image generation is not available with the current API configuration. "
    "The enhanced prompt can still be used manually."
)


@dataclass(frozen=True)
class ImageGenerationResult:
    """Structured output for optional image generation."""

    image_path: str
    model_used: str
    status: str
    message: str
    prompt_used: str


class ImageGenerationAgent:
    """Generate an image from an enhanced artist prompt if Imagen is available."""

    def __init__(
        self,
        gemini_service: GeminiService,
        *,
        output_dir: Path | str | None = None,
        model_name: str = _DEFAULT_IMAGEN_MODEL,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._gemini_service = gemini_service
        self._output_dir = Path(output_dir) if output_dir else _default_output_dir()
        self._model_name = model_name
        self._logger = logger or _LOGGER

    def generate(
        self,
        *,
        enhanced_artist_prompt: str,
        negative_prompt: str,
        visual_style: str,
    ) -> ImageGenerationResult:
        """Generate one image or return an unavailable result without crashing."""
        if not enhanced_artist_prompt.strip():
            return self._unavailable("Enhanced artist prompt must not be empty.", "")

        prompt = _build_prompt(enhanced_artist_prompt, negative_prompt, visual_style)

        if not _GENAI_TYPES_AVAILABLE:
            return self._unavailable("google-genai image types are not available.", prompt)

        client = self._gemini_service._get_client()
        if isinstance(client, GeminiResponse):
            message = client.error.message if client.error else _UNAVAILABLE_MESSAGE
            self._logger.warning("Image generation unavailable: %s", message)
            return self._unavailable(message, prompt)

        generate_images = getattr(getattr(client, "models", None), "generate_images", None)
        if generate_images is None:
            return self._unavailable("Gemini SDK does not expose image generation.", prompt)

        try:
            config = types.GenerateImagesConfig(
                numberOfImages=1,
                aspectRatio="16:9",
                outputMimeType="image/png",
            )
            response = generate_images(
                model=self._model_name,
                prompt=prompt,
                config=config,
            )
            image_bytes = _extract_first_image_bytes(response)
            if not image_bytes:
                return self._unavailable(
                    "Image generation returned no image bytes.", prompt
                )

            image_path = self._save_image(image_bytes)
            return ImageGenerationResult(
                image_path=str(image_path),
                model_used=self._model_name,
                status="generated",
                message="Image generated successfully.",
                prompt_used=prompt,
            )
        except Exception as exc:  # pragma: no cover - network/API dependent
            self._logger.warning("Image generation unavailable: %s", exc)
            return self._unavailable(str(exc), prompt)

    def _save_image(self, image_bytes: bytes) -> Path:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = int(time.time())
        output_path = self._output_dir / f"k2_18_b_artist_concept_{timestamp}.png"
        output_path.write_bytes(image_bytes)
        return output_path

    def _unavailable(self, detail: str, prompt: str) -> ImageGenerationResult:
        message = _UNAVAILABLE_MESSAGE
        if detail:
            message = f"{message} Detail: {detail}"
        return ImageGenerationResult(
            image_path="",
            model_used=self._model_name,
            status="unavailable",
            message=message,
            prompt_used=prompt,
        )


def _build_prompt(
    enhanced_artist_prompt: str,
    negative_prompt: str,
    visual_style: str,
) -> str:
    prompt = (
        f"{enhanced_artist_prompt.strip()} Visual style: {visual_style.strip()} "
        f"Avoid these unsupported visual elements: {negative_prompt.strip()}"
    ).strip()
    return re.sub(r"\s+", " ", prompt)


def _extract_first_image_bytes(response: Any) -> bytes:
    generated_images = getattr(response, "generated_images", None) or []
    if not generated_images:
        return b""

    image = getattr(generated_images[0], "image", None)
    if image is None and isinstance(generated_images[0], dict):
        image = generated_images[0].get("image")

    if image is None:
        return b""
    if isinstance(image, dict):
        return image.get("image_bytes") or b""
    return getattr(image, "image_bytes", None) or b""


def _default_output_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / "data" / "generated_images"
