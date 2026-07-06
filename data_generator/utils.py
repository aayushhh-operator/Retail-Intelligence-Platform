"""Shared helpers for deterministic synthetic retail data generation."""

from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable, Sequence, TypeVar

from faker import Faker

from data_generator import config

T = TypeVar("T")


def create_faker() -> Faker:
    """Return a seeded Faker instance."""
    fake = Faker("en_IN")
    Faker.seed(config.RANDOM_SEED)
    return fake


def seed_random() -> random.Random:
    """Return a seeded random number generator."""
    return random.Random(config.RANDOM_SEED)


def make_id(prefix: str, number: int, width: int = 6) -> str:
    """Create stable business identifiers such as CUS000001."""
    return f"{prefix}{number:0{width}d}"


def random_date_between(
    rng: random.Random,
    start_date: date,
    end_date: date,
) -> date:
    """Return a random date between two inclusive bounds."""
    days = (end_date - start_date).days
    return start_date + timedelta(days=rng.randint(0, days))


def random_datetime_after(
    rng: random.Random,
    source_date: date,
    max_hours: int,
) -> datetime:
    """Return a datetime shortly after a source date."""
    base = datetime.combine(source_date, datetime.min.time())
    return base + timedelta(
        hours=rng.randint(0, max_hours),
        minutes=rng.randint(0, 59),
        seconds=rng.randint(0, 59),
    )


def weighted_choice(
    rng: random.Random,
    values: Sequence[T],
    weights: Sequence[float],
) -> T:
    """Return one item using explicit relative weights."""
    return rng.choices(values, weights=weights, k=1)[0]


def choose_issue_indexes(
    rng: random.Random,
    row_count: int,
    issue_rate: float | None = None,
) -> set[int]:
    """Return indexes that should receive controlled data quality issues."""
    if row_count <= 0:
        return set()
    rate = config.DATA_QUALITY_ISSUE_RATE if issue_rate is None else issue_rate
    issue_count = max(1, int(row_count * rate))
    issue_count = min(issue_count, row_count)
    return set(rng.sample(range(row_count), issue_count))


def add_duplicate_rows(
    rng: random.Random,
    rows: list[dict[str, Any]],
    issue_rate: float | None = None,
) -> None:
    """Append a small number of duplicate rows for later validation phases."""
    if not rows:
        return
    rate = config.DATA_QUALITY_ISSUE_RATE if issue_rate is None else issue_rate
    duplicate_count = max(1, int(len(rows) * rate * 0.25))
    for row in rng.sample(rows, min(duplicate_count, len(rows))):
        rows.append(dict(row))


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: Sequence[str]) -> int:
    """Write dictionaries to CSV and return the number of rows written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def money(value: float) -> float:
    """Round a numeric value to two decimal places for CSV output."""
    return round(value, 2)


def format_date(value: date | datetime) -> str:
    """Format dates and datetimes consistently for generated CSV files."""
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    return value.isoformat()


def write_json(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    """Write dictionaries to JSON and return the number of rows written."""
    import json
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    data = []
    for row in rows:
        data.append(row)
        count += 1
    with path.open("w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=2)
    return count

