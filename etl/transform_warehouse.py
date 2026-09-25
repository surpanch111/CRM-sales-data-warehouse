"""
Stage 3 — Transform staging into warehouse (star schema).

Executes SQL files from sql/transformations/ in alphabetical order, all
inside a single transaction. If any file fails, the warehouse stays in its
previous good state.
"""
from __future__ import annotations

import sys
from pathlib import Path

from etl.utils.db import raw_connection
from etl.utils.logger import get_logger

log = get_logger(__name__)

ROOT = Path(__file__).resolve().parent.parent
TRANSFORM_DIR = ROOT / "sql" / "transformations"


def main() -> int:
    log.info("=== Stage 5: Transform warehouse ===")

    sql_files = sorted(TRANSFORM_DIR.glob("*.sql"))
    if not sql_files:
        log.error("No .sql files found in %s", TRANSFORM_DIR)
        return 1

    log.info("Found %d transformation file(s):", len(sql_files))
    for f in sql_files:
        log.info("  - %s", f.name)

    try:
        # Single transaction across all files: all-or-nothing semantics
        with raw_connection() as conn, conn.cursor() as cur:
            for sql_file in sql_files:
                log.info("Running %s ...", sql_file.name)
                sql = sql_file.read_text(encoding="utf-8")
                cur.execute(sql)
                # rowcount on multi-statement scripts reflects the LAST statement;
                # not always meaningful but useful as a smoke signal
                if cur.rowcount > 0:
                    log.info("  (last statement affected %d rows)", cur.rowcount)
                log.info("  ok")
    except Exception as e:
        log.error("Transform failed, rolling back: %s", e)
        raise

    log.info("Transform complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())