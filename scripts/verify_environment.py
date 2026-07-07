"""Verify environment variables are set correctly for the pipeline."""

from __future__ import annotations

import sys
from config.settings import settings

def main() -> None:
    print("Verifying Retail Intelligence Platform Environment...")
    missing = []
    
    # DB
    if not settings.database.password:
        missing.append("DATABASE_PASSWORD")
        
    # Directories
    dirs = [
        settings.directories.data_dir,
        settings.directories.source_data_dir,
        settings.directories.raw_data_dir,
        settings.directories.processed_data_dir,
        settings.directories.export_data_dir,
        settings.directories.log_dir
    ]
    for d in dirs:
        if not d.exists():
            print(f"Warning: Directory {d} does not exist. (It may be created dynamically)")

    # AI
    if not settings.ai.groq_api_key and not settings.ai.openai_api_key:
        missing.append("GROQ_API_KEY (or OPENAI_API_KEY)")
        
    if missing:
        print("\nERROR: The following required environment variables are missing:")
        for m in missing:
            print(f" - {m}")
        print("\nPlease update your .env file from .env.example.")
        sys.exit(1)
        
    print("\nEnvironment is fully configured! \u2728")
    sys.exit(0)

if __name__ == "__main__":
    main()
