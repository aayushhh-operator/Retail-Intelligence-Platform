"""Exceptions for the warehouse loading framework."""

class WarehouseError(Exception):
    """Base class for all warehouse errors."""
    pass

class DatabaseConnectionError(WarehouseError):
    """Raised when the database connection fails."""
    pass

class SchemaValidationError(WarehouseError):
    """Raised when dataset schema validation fails."""
    pass

class LoadError(WarehouseError):
    """Raised when loading data into the warehouse fails."""
    pass

class SchemaCreationError(WarehouseError):
    """Raised when schema creation fails."""
    pass
