"""Custom Exceptions for the Retail Intelligence Platform."""


class RetailIntelligenceError(Exception):
    """Base exception for all custom platform errors."""

    pass


class DataGenerationError(RetailIntelligenceError):
    """Raised when synthetic data generation fails."""

    pass


class ExtractionError(RetailIntelligenceError):
    """Raised when data extraction from APIs or sources fails."""

    pass


class ValidationError(RetailIntelligenceError):
    """Raised when data fails quality validation."""

    pass


class TransformationError(RetailIntelligenceError):
    """Raised when data transformation fails."""

    pass


class WarehouseLoadError(RetailIntelligenceError):
    """Raised when loading data into the data warehouse fails."""

    pass


class AIExecutionError(RetailIntelligenceError):
    """Raised when the AI Copilot fails to generate or execute SQL."""

    pass


class ConfigurationError(RetailIntelligenceError):
    """Raised when required configuration is missing or invalid."""

    pass
