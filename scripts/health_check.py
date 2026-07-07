"""Health check for PostgreSQL database connection."""

from __future__ import annotations

import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from config.settings import settings

def main() -> None:
    print("Performing Health Check on Data Warehouse...")
    
    db = settings.database
    uri = f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.name}"
    
    try:
        engine = create_engine(uri)
        with engine.connect() as conn:
            print(f"\u2705 Successfully connected to PostgreSQL at {db.host}:{db.port}/{db.name}")
    except OperationalError as e:
        print("\n\u274c FAILED to connect to PostgreSQL.")
        print("Please ensure Docker containers are running (`make docker-up`) and credentials in .env are correct.")
        print(f"Error details: {e}")
        sys.exit(1)
        
if __name__ == "__main__":
    main()
