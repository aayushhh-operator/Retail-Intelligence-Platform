"""Custom exceptions for the validation framework."""

from __future__ import annotations


class ValidationError(Exception):
    """Raised when a dataset cannot be validated."""
