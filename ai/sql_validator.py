"""Strict Read-Only SQL Validator."""

import re


class UnsafeSQLError(Exception):
    pass


def validate_sql(sql: str) -> str:
    """Ensure the SQL is safe for execution."""
    sql_clean = sql.strip()
    # Remove markdown code blocks if the LLM leaked them
    sql_clean = re.sub(r"^```sql", "", sql_clean, flags=re.IGNORECASE).strip()
    sql_clean = re.sub(r"^```", "", sql_clean).strip()
    sql_clean = re.sub(r"```$", "", sql_clean).strip()

    # 1. Block multiple statements
    if ";" in sql_clean and sql_clean.rfind(";") != len(sql_clean) - 1:
        raise UnsafeSQLError(
            "Multiple SQL statements (semicolon chaining) are not allowed."
        )

    # 2. Block DML and DDL
    forbidden_keywords = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "GRANT",
        "REVOKE",
        "COPY",
        "VACUUM",
        "REPLACE",
    ]
    upper_sql = sql_clean.upper()
    for kw in forbidden_keywords:
        if re.search(r"\b" + kw + r"\b", upper_sql):
            raise UnsafeSQLError(
                f"Destructive or modifying operations ({kw}) are strictly prohibited."
            )

    # 3. Must be a SELECT
    if not upper_sql.startswith("SELECT") and not upper_sql.startswith("WITH"):
        raise UnsafeSQLError("Query must start with SELECT or WITH.")

    return sql_clean
