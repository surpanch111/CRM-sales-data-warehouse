"""
Run the full pipeline end-to-end: extract -> load -> transform -> quality checks.
Halts immediately on any stage failure so bad data never reaches the warehouse.
"""
from __future__ import annotations

import sys

from etl import extract, load_staging, transform_warehouse, quality_checks
from etl.utils.logger import get_logger

log = get_logger(__name__)


def main() -> int:
    stages = [
        ("extract",         extract.main),
        ("load_staging",    load_staging.main),
        ("transform",       transform_warehouse.main),
        ("quality_checks",  quality_checks.main),
    ]

    for name, fn in stages:
        log.info(">>> Running stage: %s", name)
        rc = fn()
        if rc != 0:
            log.error("<<< Stage '%s' failed with code %d. Halting pipeline.", name, rc)
            return rc
        log.info("<<< Stage '%s' completed", name)

    log.info("Pipeline completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())