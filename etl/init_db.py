"""
Stage 0 — Initialize Database.

Executes all DDL scripts in sql/ddl/ to ensure schemas and tables exist
before any data is loaded.
"""
from pathlib import Path
from etl.utils.db import execute_sql_directory
from etl.utils.logger import get_logger

log = get_logger(__name__)

ROOT = Path(__file__).resolve().parent.parent
DDL_DIR = ROOT / "sql" / "ddl"

def main():
    log.info("=== Stage 0: Initialize Database ===")
    if not DDL_DIR.exists():
        log.error("DDL directory not found: %s", DDL_DIR)
        return 1
    
    try:
        execute_sql_directory(DDL_DIR)
        log.info("Database initialization successful.")
        return 0
    except Exception as e:
        log.error("Database initialization failed: %s", e)
        raise

if __name__ == "__main__":
    main()
