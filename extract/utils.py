"""Utility functions for extraction and raw file persistence."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


def ensure_directory(path: Path) -> None:
    """Create a directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def sha256_checksum(path: Path) -> str:
    """Return a SHA256 checksum for a file using streamed reads."""
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_file(source_path: Path, destination_path: Path) -> None:
    """Copy a source file to raw storage without modifying contents."""
    ensure_directory(destination_path.parent)
    shutil.copyfile(source_path, destination_path)


def count_csv_rows(path: Path) -> int:
    """Count CSV data rows without loading the file into memory."""
    with path.open("r", encoding="utf-8", newline="") as file_obj:
        row_count = sum(1 for _ in file_obj)
    return max(0, row_count - 1)


def detect_csv_columns(path: Path) -> list[str]:
    """Return CSV header columns from the first line."""
    import csv

    with path.open("r", encoding="utf-8", newline="") as file_obj:
        reader = csv.reader(file_obj)
        return next(reader, [])

