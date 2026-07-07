"""Generate synthetic website events data."""

from __future__ import annotations

import random
from typing import Any

from data_generator import config
from data_generator.utils import (add_duplicate_rows, choose_issue_indexes,
                                  create_faker, format_date, make_id,
                                  random_datetime_after)


def generate_website_events(rng: random.Random) -> list[dict[str, Any]]:
    """Generate random website events."""
    fake = create_faker()
    events: list[dict[str, Any]] = []

    event_types = [
        "page_view",
        "add_to_cart",
        "remove_from_cart",
        "checkout_started",
        "purchase",
        "search",
    ]

    for i in range(1, config.NUMBER_OF_WEBSITE_EVENTS + 1):
        event_id = make_id("EVT", i, width=8)
        event_type = rng.choices(event_types, weights=[50, 15, 5, 10, 10, 10], k=1)[0]
        event_date = fake.date_time_between(
            start_date=config.START_DATE, end_date=config.END_DATE
        )

        events.append(
            {
                "event_id": event_id,
                "event_type": event_type,
                "timestamp": format_date(event_date),
                "session_id": make_id("SESS", rng.randint(1, 100000), width=8),
                "customer_id": (
                    make_id("CUS", rng.randint(1, config.NUMBER_OF_CUSTOMERS), width=6)
                    if rng.random() > 0.3
                    else None
                ),
                "url": fake.uri(),
                "device": rng.choice(["desktop", "mobile", "tablet"]),
            }
        )

    issue_indexes = choose_issue_indexes(rng, len(events))
    for idx in issue_indexes:
        issue_type = rng.choice(["missing_session", "missing_type"])
        if issue_type == "missing_session":
            events[idx]["session_id"] = None
        else:
            events[idx]["event_type"] = None

    add_duplicate_rows(rng, events)
    return events
