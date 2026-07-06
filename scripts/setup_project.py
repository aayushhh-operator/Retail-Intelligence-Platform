"""Project setup checks for the Retail Intelligence Platform scaffold."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.constants import (
    AI_DIR,
    AIRFLOW_DIR,
    CONFIG_DIR,
    DASHBOARD_DIR,
    DATA_DIR,
    DOCS_DIR,
    EXTRACT_DIR,
    LOAD_DIR,
    LOGS_DIR,
    SCRIPTS_DIR,
    SPARK_DIR,
    SQL_DIR,
    TESTS_DIR,
    TRANSFORM_DIR,
    VALIDATE_DIR,
    WAREHOUSE_DIR,
)


REQUIRED_DIRECTORIES = (
    CONFIG_DIR,
    DATA_DIR,
    "data/source",
    "data/raw",
    "data/processed",
    "data/exports",
    EXTRACT_DIR,
    VALIDATE_DIR,
    TRANSFORM_DIR,
    LOAD_DIR,
    WAREHOUSE_DIR,
    SQL_DIR,
    AIRFLOW_DIR,
    SPARK_DIR,
    DASHBOARD_DIR,
    AI_DIR,
    LOGS_DIR,
    TESTS_DIR,
    DOCS_DIR,
    SCRIPTS_DIR,
    ".github/workflows",
)


def check_directories(project_root: Path) -> list[Path]:
    """Return required directories that are missing from the scaffold."""
    return [
        project_root / directory
        for directory in REQUIRED_DIRECTORIES
        if not (project_root / directory).is_dir()
    ]


def main() -> None:
    """Run scaffold checks used by placeholder maintenance commands."""
    parser = argparse.ArgumentParser(description="Retail platform setup checks.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether required scaffold directories exist.",
    )
    args = parser.parse_args()

    if args.check:
        missing_directories = check_directories(PROJECT_ROOT)
        if missing_directories:
            missing = "\n".join(str(path) for path in missing_directories)
            raise SystemExit(f"Missing required directories:\n{missing}")
        print("Project scaffold directories are present.")
        return

    print("No setup actions are implemented in Phase 0.")


if __name__ == "__main__":
    main()
