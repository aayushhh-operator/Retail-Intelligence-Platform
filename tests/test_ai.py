"""Tests for AI Module and strict SQL validation."""

import pytest
from ai.sql_validator import validate_sql, UnsafeSQLError

def test_sql_validator_allows_valid_select():
    sql = "SELECT * FROM analytics.fact_orders"
    assert validate_sql(sql) == sql

def test_sql_validator_allows_with_clause():
    sql = "WITH cte AS (SELECT 1) SELECT * FROM cte"
    assert validate_sql(sql) == sql

def test_sql_validator_blocks_multiple_statements():
    sql = "SELECT * FROM analytics.fact_orders; SELECT * FROM dim_customer;"
    with pytest.raises(UnsafeSQLError, match="Multiple SQL statements"):
        validate_sql(sql)

def test_sql_validator_blocks_dml():
    queries = [
        "DELETE FROM analytics.fact_orders",
        "UPDATE analytics.fact_orders SET quantity = 0",
        "INSERT INTO analytics.fact_orders (id) VALUES (1)",
        "TRUNCATE TABLE analytics.fact_orders"
    ]
    for sql in queries:
        with pytest.raises(UnsafeSQLError, match="Destructive or modifying operations"):
            validate_sql(sql)

def test_sql_validator_blocks_ddl():
    queries = [
        "DROP TABLE analytics.fact_orders",
        "ALTER TABLE analytics.fact_orders ADD COLUMN fake INT",
        "CREATE TABLE fake (id INT)",
        "GRANT ALL ON analytics.fact_orders TO user"
    ]
    for sql in queries:
        with pytest.raises(UnsafeSQLError, match="Destructive or modifying operations"):
            validate_sql(sql)

def test_sql_validator_removes_markdown():
    sql = "```sql\\nSELECT * FROM test\\n```"
    result = validate_sql(sql)
    assert "```" not in result
    assert result.startswith("SELECT")
