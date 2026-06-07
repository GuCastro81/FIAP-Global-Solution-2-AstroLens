"""NASA Image and Video Library API integration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

_API_ROOT = "https://images-api.nasa.gov"
_DEFAULT_TIMEOUT_SECONDS = 15
_USER_AGENT = "AstroLens-AI/1.0"


@dataclass(frozen=True)
class NASAImage:
    """Normalized NASA image metadata used by the application."""

    title: str
    description: str
    image_url: str
    nasa_id: str


class NASAServiceError(RuntimeError):
    """Raised when the NASA API cannot fulfill a request."""


class NASAService:
    """Client for NASA's Image and Video Library API."""

    def __init__(
        self,
        *,
        api_root: str = _API_ROOT,
        timeout: int = _DEFAULT_TIMEOUT_SECONDS,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        self.api_root = api_root.rstrip("/")
        self.timeout = timeout
        self._opener = opener

    def search_images(self, query: str) -> List[NASAImage]:
        """Search NASA's library for images matching a text query."""
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("Search query must not be empty.")

        payload = self._get_json(
            "/search",
            {"q": normalized_query, "media_type": "image"},
        )
        return [
            image
            for item in _collection_items(payload)
            if (image := _parse_image(item)) is not None
        ]

    def get_image_details(self, nasa_id: str) -> NASAImage:
        """Return normalized metadata for a NASA image ID."""
        normalized_id = nasa_id.strip()
        if not normalized_id:
            raise ValueError("NASA ID must not be empty.")

        payload = self._get_json(
            "/search",
            {"nasa_id": normalized_id, "media_type": "image"},
        )
        for item in _collection_items(payload):
            image = _parse_image(item)
            if image and image.nasa_id == normalized_id:
                return image

        raise NASAServiceError(f"NASA image not found: {normalized_id}")

    def _get_json(
        self, path: str, params: Dict[str, str] | None = None
    ) -> Dict[str, Any]:
        query_string = f"?{urlencode(params)}" if params else ""
        url = f"{self.api_root}/{quote(path.lstrip('/'), safe='/')}{query_string}"
        request = Request(
            url,
            headers={"Accept": "application/json", "User-Agent": _USER_AGENT},
        )

        try:
            with self._opener(request, timeout=self.timeout) as response:
                payload = json.load(response)
        except HTTPError as exc:
            raise NASAServiceError(
                f"NASA API request failed with HTTP {exc.code}."
            ) from exc
        except URLError as exc:
            reason = getattr(exc, "reason", exc)
            raise NASAServiceError(f"NASA API request failed: {reason}") from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise NASAServiceError(f"Invalid response from NASA API: {exc}") from exc

        if not isinstance(payload, dict):
            raise NASAServiceError("NASA API returned an unexpected response.")
        return payload


def _collection_items(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    collection = payload.get("collection", {})
    if not isinstance(collection, dict):
        return []
    items = collection.get("items", [])
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _parse_image(item: Dict[str, Any]) -> NASAImage | None:
    data_items = item.get("data", [])
    if not isinstance(data_items, list) or not data_items:
        return None

    metadata = data_items[0]
    if not isinstance(metadata, dict):
        return None

    nasa_id = str(metadata.get("nasa_id", "")).strip()
    if not nasa_id:
        return None

    image_url = _find_image_url(item.get("links", []))
    if not image_url:
        return None

    return NASAImage(
        title=str(metadata.get("title", "")).strip() or nasa_id,
        description=str(metadata.get("description", "")).strip(),
        image_url=image_url,
        nasa_id=nasa_id,
    )


def _find_image_url(links: Any) -> str:
    if not isinstance(links, list):
        return ""

    fallback = ""
    for link in links:
        if not isinstance(link, dict):
            continue
        href = str(link.get("href", "")).strip()
        if not href:
            continue
        if not fallback:
            fallback = href
        if link.get("render") == "image":
            return href
    return fallback
