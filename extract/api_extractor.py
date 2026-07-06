"""API source extractor implementation."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from extract.exceptions import ExtractionError
from extract.extractor import BaseExtractor, ExtractedPayload


class APIExtractor(BaseExtractor):
    """Extract HTTP API responses into raw JSON files."""

    def connect(self) -> None:
        """Prepare API extraction.

        The standard library HTTP client opens the connection during extraction,
        so this method exists to satisfy the common extractor contract.
        """

    def extract(self) -> bytes:
        """Fetch raw bytes from the configured API endpoint."""
        request = Request(
            self.source_config.source,
            headers={"User-Agent": "RetailIntelligencePlatform/1.0"},
        )
        try:
            with urlopen(request, timeout=30) as response:
                return response.read()
        except URLError as exc:
            raise ExtractionError(f"API request failed: {exc}") from exc

    def save(self, extracted_data: bytes) -> ExtractedPayload:
        """Save API response bytes as raw JSON and collect metadata."""
        destination = self.destination_path()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(extracted_data)
        payload: Any = json.loads(extracted_data.decode("utf-8"))

        if isinstance(payload, list):
            rows = len(payload)
            columns = sorted({key for item in payload if isinstance(item, dict) for key in item})
        elif isinstance(payload, dict):
            rows = 1
            columns = sorted(payload.keys())
        else:
            rows = 1
            columns = []

        return ExtractedPayload(
            destination_path=destination,
            rows=rows,
            columns=columns,
            file_size_bytes=destination.stat().st_size,
            extra={"format": "json", "http_method": "GET"},
        )

