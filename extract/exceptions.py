"""Custom exceptions for the extraction layer."""

from __future__ import annotations


class ExtractionError(Exception):
    """Raised when a dataset cannot be extracted or saved."""
