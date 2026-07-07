"""Tests for Phase 6 Analytics layer."""

from unittest.mock import MagicMock

import pytest

from analytics.star_schema import StarSchemaBuilder
from analytics.utils import AnalyticsDBManager


def test_dim_builder_initialization():
    """Test dimension builder can be initialized."""
    from analytics.dim_builder import DimensionBuilder

    mock_db = MagicMock()
    builder = DimensionBuilder(mock_db)
    assert builder.db == mock_db


def test_fact_builder_initialization():
    """Test fact builder can be initialized."""
    from analytics.fact_builder import FactBuilder

    mock_db = MagicMock()
    builder = FactBuilder(mock_db)
    assert builder.db == mock_db


def test_star_schema_orchestrator():
    """Test star schema orchestrator delegates appropriately."""
    mock_db = MagicMock()
    builder = StarSchemaBuilder(mock_db)
    assert builder.dim_builder is not None
    assert builder.fact_builder is not None


def test_model_dataclasses_exist():
    """Test model data classes can be imported."""
    try:
        from analytics.models.dim_customer import DimCustomer
        from analytics.models.fact_orders import FactOrders

        assert True
    except ImportError:
        pytest.fail("Models were not generated or accessible.")
