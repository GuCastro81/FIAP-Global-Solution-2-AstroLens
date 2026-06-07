"""Smoke test for the NASA Image and Video Library service."""

import json
from dataclasses import asdict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from bootstrap import add_repo_root

add_repo_root()

from src.services.nasa_service import NASAService, NASAServiceError

_QUERIES = ("andromeda", "orion nebula", "jupiter")
_RESULT_LIMIT = 3
_URL_TIMEOUT_SECONDS = 15


def main() -> int:
    service = NASAService()
    for query in _QUERIES:
        print(f"\n=== Search: {query} ===")
        try:
            results = service.search_images(query)
            first_results = results[:_RESULT_LIMIT]
            print(json.dumps([asdict(item) for item in first_results], indent=2))

            if len(first_results) < _RESULT_LIMIT:
                print(
                    f"Expected {_RESULT_LIMIT} results, received {len(first_results)}."
                )
                return 1

            for result in first_results:
                if not all(
                    (
                        result.title,
                        result.description,
                        result.nasa_id,
                        result.image_url,
                    )
                ):
                    print(f"Result has missing required fields: {result.nasa_id}")
                    return 1
                if not _image_url_is_accessible(result.image_url):
                    print(f"Image URL is not accessible: {result.image_url}")
                    return 1

            details = service.get_image_details(first_results[0].nasa_id)
            if details.nasa_id != first_results[0].nasa_id:
                print(f"Detail lookup returned the wrong NASA ID: {details.nasa_id}")
                return 1
        except (NASAServiceError, ValueError) as exc:
            print(f"NASA service test failed for {query!r}: {exc}")
            return 1

    print("\nNASA service smoke test passed.")
    return 0


def _image_url_is_accessible(image_url: str) -> bool:
    request = Request(
        image_url,
        headers={
            "Range": "bytes=0-0",
            "User-Agent": "AstroLens-AI/1.0",
        },
    )
    try:
        with urlopen(request, timeout=_URL_TIMEOUT_SECONDS) as response:
            content_type = response.headers.get_content_type()
            response.read(1)
            return 200 <= response.status < 300 and content_type.startswith("image/")
    except (HTTPError, URLError, OSError):
        return False


if __name__ == "__main__":
    raise SystemExit(main())
