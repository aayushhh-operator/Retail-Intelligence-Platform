"""Environment-driven settings for the Retail Intelligence Platform."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is installed in later setup.

    def load_dotenv() -> None:
        """Fallback used before project dependencies are installed."""
        return None


load_dotenv()


def _get_env(name: str, default: str = "") -> str:
    """Return an environment variable with a project-level default."""
    return os.getenv(name, default)


def _get_int_env(name: str, default: int) -> int:
    """Return an integer environment variable with a safe fallback."""
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


@dataclass(frozen=True)
class DatabaseSettings:
    """Database settings for the planned PostgreSQL warehouse."""

    host: str = _get_env("DATABASE_HOST", "localhost")
    port: int = _get_int_env("DATABASE_PORT", 5432)
    name: str = _get_env("DATABASE_NAME", "retail_intelligence")
    user: str = _get_env("DATABASE_USER", "retail_user")
    password: str = _get_env("DATABASE_PASSWORD", "")


@dataclass(frozen=True)
class DirectorySettings:
    """Filesystem locations used by future pipeline stages."""

    project_root: Path = Path(__file__).resolve().parents[1]
    data_dir: Path = Path(_get_env("DATA_DIR", "data"))
    source_data_dir: Path = Path(_get_env("SOURCE_DATA_DIR", "data/source"))
    raw_data_dir: Path = Path(_get_env("RAW_DATA_DIR", "data/raw"))
    processed_data_dir: Path = Path(_get_env("PROCESSED_DATA_DIR", "data/processed"))
    export_data_dir: Path = Path(_get_env("EXPORT_DATA_DIR", "data/exports"))
    log_dir: Path = Path(_get_env("LOG_DIR", "logs"))


@dataclass(frozen=True)
class LoggingSettings:
    """Logging settings shared by local and orchestrated pipeline runs."""

    level: str = _get_env("LOG_LEVEL", "INFO")
    log_file: str = _get_env("LOG_FILE", "retail_intelligence.log")


@dataclass(frozen=True)
class ValidationSettings:
    """Configurable thresholds for the data quality framework."""

    # Quality score boundaries for PASS / WARNING / FAIL
    pass_threshold: float = float(_get_env("VALIDATION_PASS_THRESHOLD", "95"))
    warning_threshold: float = float(_get_env("VALIDATION_WARNING_THRESHOLD", "90"))
    # Maximum allowed missing value percentage before flagging as WARNING
    max_missing_percentage: float = float(_get_env("VALIDATION_MAX_MISSING_PCT", "20"))
    # Maximum allowed duplicate row percentage before flagging as WARNING
    max_duplicate_percentage: float = float(
        _get_env("VALIDATION_MAX_DUPLICATE_PCT", "5")
    )
    # IQR multiplier for outlier detection (standard = 1.5)
    outlier_iqr_multiplier: float = float(_get_env("VALIDATION_OUTLIER_IQR", "1.5"))


@dataclass(frozen=True)
class AISettings:
    """AI assistant configuration."""

    groq_api_key: str = _get_env("GROQ_API_KEY", "")
    openai_api_key: str = _get_env("OPENAI_API_KEY", "")
    model: str = _get_env("AI_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")


@dataclass(frozen=True)
class AirflowSettings:
    """Airflow orchestration configuration."""

    airflow_home: str = _get_env("AIRFLOW_HOME", "")
    dag_dir: str = _get_env("AIRFLOW_DAG_DIR", "airflow")


@dataclass(frozen=True)
class SparkSettings:
    """Spark distributed processing configuration."""

    master_url: str = _get_env("SPARK_MASTER_URL", "")
    app_name: str = _get_env("SPARK_APP_NAME", "RetailIntelligencePlatform")


@dataclass(frozen=True)
class Settings:
    """Application settings grouped by concern."""

    database: DatabaseSettings = DatabaseSettings()
    directories: DirectorySettings = DirectorySettings()
    logging: LoggingSettings = LoggingSettings()
    validation: ValidationSettings = ValidationSettings()
    ai: AISettings = AISettings()
    airflow: AirflowSettings = AirflowSettings()
    spark: SparkSettings = SparkSettings()


settings = Settings()
