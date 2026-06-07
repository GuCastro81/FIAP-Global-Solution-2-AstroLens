"""Tests for NASAService response parsing and errors."""

import io
import json
import unittest
from urllib.error import URLError

from src.services.nasa_service import NASAService, NASAServiceError


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def _payload() -> dict:
    return {
        "collection": {
            "items": [
                {
                    "data": [
                        {
                            "title": "Andromeda Galaxy",
                            "description": "A neighboring spiral galaxy.",
                            "nasa_id": "PIA04921",
                            "media_type": "image",
                        }
                    ],
                    "links": [
                        {
                            "href": "https://images-assets.nasa.gov/image.jpg",
                            "render": "image",
                        }
                    ],
                }
            ]
        }
    }


class TestNASAService(unittest.TestCase):
    def test_search_images_returns_normalized_results(self) -> None:
        def opener(request, timeout):
            self.assertIn("media_type=image", request.full_url)
            self.assertIn("q=Andromeda", request.full_url)
            self.assertEqual(timeout, 15)
            return _Response(json.dumps(_payload()).encode())

        results = NASAService(opener=opener).search_images("Andromeda")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Andromeda Galaxy")
        self.assertEqual(results[0].nasa_id, "PIA04921")
        self.assertEqual(
            results[0].image_url, "https://images-assets.nasa.gov/image.jpg"
        )

    def test_get_image_details_matches_exact_id(self) -> None:
        service = NASAService(
            opener=lambda request, timeout: _Response(
                json.dumps(_payload()).encode()
            )
        )

        result = service.get_image_details("PIA04921")

        self.assertEqual(result.description, "A neighboring spiral galaxy.")

    def test_empty_values_are_rejected(self) -> None:
        service = NASAService()
        with self.assertRaises(ValueError):
            service.search_images(" ")
        with self.assertRaises(ValueError):
            service.get_image_details("")

    def test_network_errors_are_wrapped(self) -> None:
        def opener(request, timeout):
            raise URLError("offline")

        with self.assertRaisesRegex(NASAServiceError, "offline"):
            NASAService(opener=opener).search_images("Mars")


if __name__ == "__main__":
    unittest.main()
