"""Generate synthetic customer source data."""

from __future__ import annotations

import random
from typing import Any

from data_generator import config
from data_generator.utils import (
    add_duplicate_rows,
    choose_issue_indexes,
    create_faker,
    format_date,
    make_id,
    random_date_between,
)

CUSTOMER_FIELDS = (
    "customer_id",
    "first_name",
    "last_name",
    "full_name",
    "email",
    "phone",
    "gender",
    "date_of_birth",
    "city",
    "state",
    "country",
    "zipcode",
    "signup_date",
    "is_active",
    "customer_segment",
)


def generate_customers(rng: random.Random) -> list[dict[str, Any]]:
    """Generate customer records with small controlled quality defects."""
    fake = create_faker()
    rows: list[dict[str, Any]] = []
    issue_indexes = choose_issue_indexes(rng, config.NUMBER_OF_CUSTOMERS)
    segments = ("New", "Regular", "Premium", "At Risk", "Wholesale")
    genders = ("Female", "Male", "Non-binary", "Prefer not to say")

    for index in range(1, config.NUMBER_OF_CUSTOMERS + 1):
        gender = rng.choice(genders)
        first_name = fake.first_name()
        last_name = fake.last_name()
        signup_date = random_date_between(rng, config.START_DATE, config.END_DATE)

        row = {
            "customer_id": make_id("CUS", index),
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}",
            "email": fake.unique.email(),
            "phone": fake.phone_number(),
            "gender": gender,
            "date_of_birth": format_date(fake.date_of_birth(minimum_age=18, maximum_age=75)),
            "city": fake.city(),
            "state": fake.state(),
            "country": "India",
            "zipcode": fake.postcode(),
            "signup_date": format_date(signup_date),
            "is_active": rng.choice((True, True, True, False)),
            "customer_segment": rng.choice(segments),
        }

        if index - 1 in issue_indexes:
            issue_type = rng.choice(("missing_email", "invalid_email", "null_phone", "missing_id", "bad_zip"))
            if issue_type == "missing_email":
                row["email"] = ""
            elif issue_type == "invalid_email":
                row["email"] = f"{first_name.lower()}.{last_name.lower()}example.com"
            elif issue_type == "null_phone":
                row["phone"] = ""
            elif issue_type == "missing_id":
                row["customer_id"] = ""
            elif issue_type == "bad_zip":
                row["zipcode"] = "INVALID"

        rows.append(row)

    add_duplicate_rows(rng, rows)
    return rows

