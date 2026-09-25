"""
Stage 4 — Quality checks.

Runs sql/quality_checks/checks.sql and treats any returned rows as failures.
Exit code 0 = all checks passed. Exit code 1 = at least one failure.

Designed to fail loudly. Better to halt the pipeline than ship bad data.
"""
from __future__ import annotations

import sys
from pathlib import Path

from etl.utils.db import raw_connection
from etl.utils.logger import get_logger

log = get_logger(__name__)

ROOT = Path(__file__).resolve().parent.parent
CHECKS_SQL = ROOT / "sql" / "quality_checks" / "checks.sql"


def main() -> int:
    log.info("=== Stage 6: Quality checks ===")

    if not CHECKS_SQL.exists():
        log.error("Missing checks file: %s", CHECKS_SQL)
        return 1

    sql = CHECKS_SQL.read_text(encoding="utf-8")

    with raw_connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        failures = cur.fetchall()

    if not failures:
        log.info("All checks PASSED ✓")
        return 0

    # Group failures by check name for cleaner output
    grouped: dict[str, list[str]] = {}
    for check_name, detail in failures:
        grouped.setdefault(check_name, []).append(detail or "")

    log.error("=" * 60)
    log.error("QUALITY CHECKS FAILED — %d failure(s) across %d check(s)",
              len(failures), len(grouped))
    log.error("=" * 60)

    for check_name, details in grouped.items():
        log.error("  %s (%d):", check_name, len(details))
        # Limit details printed per check — failures can be voluminous
        for d in details[:5]:
            log.error("    - %s", d)
        if len(details) > 5:
            log.error("    ... and %d more", len(details) - 5)

    log.error("=" * 60)
    log.error("Pipeline halted. Fix data quality issues before publishing.")
    return 1


if __name__ == "__main__":
    sys.exit(main())