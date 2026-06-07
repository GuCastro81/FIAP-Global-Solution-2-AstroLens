# NASAService

`NASAService` uses the NASA Image and Video Library API at
`https://images-api.nasa.gov`.

## Smoke Test

Run:

```bash
python scripts/test_nasa_service.py
```

The smoke test performs live searches for `andromeda`, `orion nebula`, and
`jupiter`. For the first three results from each query, it verifies:

- `title`
- `description`
- `nasa_id`
- `image_url`
- The image URL returns a successful HTTP response with an image content type

It also performs an exact NASA ID detail lookup for the first result of every
query.

## API Limitations

- Search responses use Collection+JSON and are paginated. The documented
  default page size is 100; clients must follow pagination links or request
  subsequent pages for larger result sets.
- Search result image links are preview renditions and can be thumbnails,
  small, or medium images. Use `/asset/{nasa_id}` when a manifest of available
  renditions or the original asset is required.
- Search relevance and metadata completeness vary across NASA collections.
  Applications should tolerate missing optional metadata and short
  descriptions.
- Assets can be moved or removed, so a previously returned image URL can later
  return an HTTP error. URLs should be checked at use time.
- NASA's Image Library API documentation does not publish a numeric rate limit
  or rate-limit headers. Clients should still use timeouts, avoid unnecessary
  repeated requests, and handle all 4xx and 5xx responses gracefully.

Official reference:
https://images.nasa.gov/docs/images.nasa.gov_api_docs.pdf
