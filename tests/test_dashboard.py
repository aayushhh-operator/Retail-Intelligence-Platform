"""Tests for Phase 9 Streamlit Dashboard."""

from unittest.mock import patch

import pandas as pd
import pytest

from dashboard.services.db_service import execute_query


def test_db_service_handles_failures():
    """Ensure that the db_service does not crash the app on invalid queries, but returns an empty dataframe."""
    df = execute_query("SELECT * FROM non_existent_table")
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_db_service_success():
    """Test successful query execution using a mocked engine."""
    mock_df = pd.DataFrame({"total_revenue": [1000], "total_orders": [5]})

    # Mock the execute_query directly to avoid actual DB connection in unit tests
    with patch("dashboard.services.db_service.execute_query", return_value=mock_df):
        from dashboard.services.analytics_service import get_total_revenue

        result = get_total_revenue()

        assert not result.empty
        assert result.iloc[0]["total_revenue"] == 1000
