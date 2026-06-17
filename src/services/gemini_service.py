"""Gemini service integration for text and vision use cases."""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

try:
    from google import genai
    from google.genai import errors, types

    _GENAI_AVAILABLE = True
except Exception:  # pragma: no cover - import guard for optional dependency
    genai = None
    errors = None
    types = None
    _GENAI_AVAILABLE = False

_LOGGER = logging.getLogger(__name__)
_PRIMARY_MODEL = "gemini-2.5-flash"
_FALLBACK_MODEL = "gemini-2.0-flash"
_RETRY_STATUS_CODES = {429, 500, 503}
_RETRY_DELAYS_SECONDS = (2, 4, 8)


@dataclass(frozen=True)
class GeminiError:
    """Structured error details for Gemini responses."""

    type: str
    message: str


@dataclass(frozen=True)
class GeminiGenerationData:
    """Structured output for Gemini generation responses."""

    text: str
    usage: Optional[Any]
    mode: str
    image_mime_type: Optional[str] = None


@dataclass(frozen=True)
class GeminiResponse:
    """Standard response envelope for Gemini service calls."""

    ok: bool
    model: str
    data: Optional[GeminiGenerationData]
    error: Optional[GeminiError]


def load_env_file(path: str) -> None:
    """Load key-value pairs from a .env file into the process environment."""
    if not os.path.isfile(path):
        _LOGGER.debug(".env file not found at %s", path)
        return

    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"\'")
            if key and (key not in os.environ or not os.environ.get(key)):
                os.environ[key] = value


class GeminiService:
    """Reusable Gemini integration for text generation and image analysis."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = _PRIMARY_MODEL,
        fallback_model: str = _FALLBACK_MODEL,
        env_path: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._logger = logger or _LOGGER
        self.model_name = model_name
        self.fallback_model = fallback_model
        self._client = None

        if api_key is None:
            env_path = env_path or self._default_env_path()
            load_env_file(env_path)
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        self.api_key = api_key
        if not self.api_key:
            self._logger.warning(
                "GEMINI_API_KEY/GOOGLE_API_KEY is not set. Calls will fail."
            )

    def generate_text(self, prompt: str) -> GeminiResponse:
        """Generate text from a prompt using Gemini."""
        if not prompt:
            return self._error("InvalidRequest", "Prompt must not be empty.")

        return self._generate_with_retries(
            prompt=prompt,
            image_part=None,
            mode="text",
        )

    def analyze_image(
        self,
        prompt: str,
        *,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> GeminiResponse:
        """Analyze an image with Gemini Vision using a prompt and image input."""
        if not prompt:
            return self._error("InvalidRequest", "Prompt must not be empty.")
        if image_path is None and image_bytes is None:
            return self._error("InvalidRequest", "Provide image_path or image_bytes.")

        if image_path:
            try:
                with open(image_path, "rb") as handle:
                    image_bytes = handle.read()
            except OSError as exc:
                return self._error("ImageReadError", str(exc))

        mime_type = mime_type or self._guess_mime_type(image_path)
        if not mime_type:
            return self._error("InvalidRequest", "Unable to determine image mime type.")

        client = self._get_client()
        if isinstance(client, GeminiResponse):
            return client

        image_part = self._build_image_part(image_bytes=image_bytes, mime_type=mime_type)
        if isinstance(image_part, GeminiResponse):
            return image_part

        return self._generate_with_retries(
            prompt=prompt,
            image_part=image_part,
            mode="vision",
            image_mime_type=mime_type,
            client=client,
        )

    def _get_client(self) -> Any:
        if not self.api_key:
            return self._error(
                "MissingAPIKey",
                "GEMINI_API_KEY or GOOGLE_API_KEY is required.",
            )
        if not _GENAI_AVAILABLE:
            return self._error(
                "MissingDependency",
                "google-genai is not installed. Install it to use Gemini.",
            )
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _success(self, data: GeminiGenerationData, model_name: str) -> GeminiResponse:
        return GeminiResponse(
            ok=True,
            model=model_name,
            data=data,
            error=None,
        )

    def _error(
        self, error_type: str, message: str, model_name: Optional[str] = None
    ) -> GeminiResponse:
        self._logger.error("GeminiService error %s: %s", error_type, message)
        return GeminiResponse(
            ok=False,
            model=model_name or self.model_name,
            data=None,
            error=GeminiError(type=error_type, message=message),
        )

    @staticmethod
    def _default_env_path() -> str:
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        return os.path.join(root, ".env")

    @staticmethod
    def _guess_mime_type(image_path: Optional[str]) -> Optional[str]:
        if not image_path:
            return "image/jpeg"
        _, ext = os.path.splitext(image_path.lower())
        return {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }.get(ext)

    def _build_image_part(
        self, *, image_bytes: Optional[bytes], mime_type: Optional[str]
    ) -> Union[GeminiResponse, Dict[str, Any]]:
        if not image_bytes:
            return self._error("InvalidRequest", "Image bytes are empty.")
        if not mime_type:
            return self._error("InvalidRequest", "Image mime type is required.")
        return types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    def _generate_with_retries(
        self,
        *,
        prompt: str,
        image_part: Optional[Any],
        mode: str,
        image_mime_type: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> GeminiResponse:
        client = client or self._get_client()
        if isinstance(client, GeminiResponse):
            return client

        model_name = self.model_name
        attempts = 1 + len(_RETRY_DELAYS_SECONDS)

        for attempt_index in range(attempts):
            try:
                contents = [prompt, image_part] if image_part is not None else prompt
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                )
                usage = getattr(response, "usage_metadata", None)
                data = GeminiGenerationData(
                    text=response.text,
                    usage=usage,
                    mode=mode,
                    image_mime_type=image_mime_type,
                )
                return self._success(data, model_name=model_name)
            except Exception as exc:  # pragma: no cover - network dependent
                status_code = self._extract_status_code(exc)
                if status_code == 503 and model_name == self.model_name:
                    self._logger.warning(
                        "Primary model unavailable (503). Switching to fallback: %s",
                        self.fallback_model,
                    )
                    model_name = self.fallback_model
                if status_code in _RETRY_STATUS_CODES and attempt_index < attempts - 1:
                    delay = _RETRY_DELAYS_SECONDS[attempt_index]
                    self._logger.warning(
                        "Gemini request failed with %s. Retrying in %ss (attempt %s/%s).",
                        status_code,
                        delay,
                        attempt_index + 1,
                        attempts,
                    )
                    time.sleep(delay)
                    continue

                self._logger.exception("Gemini request failed after retries.")
                return self._error(type(exc).__name__, str(exc), model_name=model_name)

        return self._error(
            "RetryExceeded",
            "Request failed after retry attempts.",
            model_name=model_name,
        )

    @staticmethod
    def _extract_status_code(error: Exception) -> Optional[int]:
        if errors and isinstance(error, errors.APIError):
            return getattr(error, "code", None)
        return getattr(error, "code", None)
