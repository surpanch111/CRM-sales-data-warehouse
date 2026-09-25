"""
Stage 2 — Load staging.

Reads the parquet snapshots produced by extract.py and bulk-loads them
into Postgres using COPY FROM STDIN. This is dramatically faster than
pandas.to_sql() (which falls back to row-by-row INSERTs) and uses constant
memory because it streams rather than buffering everything.

Pattern: truncate-and-reload. Idempotent, no state to track.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd

from etl.utils.db import raw_connection
from etl.utils.logger import get_logger

log = get_logger(__name__)

ROOT = Path(__file__).resolve().parent.parent
STAGING_DIR = ROOT / "data" / "staging"

# (parquet file, target table, ordered column list matching DDL)
TARGETS = [
    (
        "accounts.parquet",
        "staging.accounts",
        ["account", "sector", "year_established", "revenue",
         "employees", "office_location", "subsidiary_of"],
    ),
    (
        "products.parquet",
        "staging.products",
        ["product", "series", "sales_price"],
    ),
    (
        "sales_teams.parquet",
        "staging.sales_teams",
        ["sales_agent", "manager", "regional_office"],
    ),
    (
        "sales_pipeline.parquet",
        "staging.sales_pipeline",
        ["opportunity_id", "sales_agent", "product", "account",
         "deal_stage", "engage_date", "close_date", "close_value"],
    ),
]


def load_one(parquet_name: str, table: str, columns: list[str], cur) -> int:
    """Truncate the target table, then COPY parquet contents in. Returns row count."""
    parquet_path = STAGING_DIR / parquet_name
    if not parquet_path.exists():
        log.error("Missing parquet: %s — run extract.py first", parquet_path)
        return -1

    log.info("Loading %s -> %s", parquet_name, table)

    df = pd.read_parquet(parquet_path)

    # Reorder/select to match DDL column order. Missing columns in parquet
    # become NULL in the output (defensive against schema drift).
    for col in columns:
        if col not in df.columns:
            df[col] = pd.NA
    df = df[columns]

    log.info("  rows: %d, columns: %d", len(df), len(columns))

    # Truncate first — staging is reload-safe by design
    cur.execute(f"TRUNCATE TABLE {table};")

    # Serialize to in-memory CSV for COPY. Tab separator + \\N for NULL is
    # the safest combination (fewer edge cases than commas + quoted strings).
    buf = io.StringIO()
    df.to_csv(
        buf,
        sep="\t",
        header=False,
        index=False,
        na_rep="\\N",       # Postgres' NULL marker in text COPY
        date_format="%Y-%m-%d",
    )
    buf.seek(0)

    cols_sql = ", ".join(columns)
    copy_sql = (
        f"COPY {table} ({cols_sql}) "
        f"FROM STDIN WITH (FORMAT text, DELIMITER E'\\t', NULL '\\N')"
    )
    cur.copy_expert(copy_sql, buf)

    log.info("  loaded %d rows", len(df))
    return len(df)


def main() -> int:
    log.info("=== Stage 4: Load staging ===")

    if not STAGING_DIR.exists() or not any(STAGING_DIR.glob("*.parquet")):
        log.error("No parquet files in %s — run `python -m etl.extract` first", STAGING_DIR)
        return 1

    total = 0
    failures = 0

    # One transaction wraps all four loads — all-or-nothing
    try:
        with raw_connection() as conn, conn.cursor() as cur:
            for parquet_name, table, columns in TARGETS:
                n = load_one(parquet_name, table, columns, cur)
                if n < 0:
                    failures += 1
                else:
                    total += n
    except Exception as e:
        log.error("Load failed, transaction rolled back: %s", e)
        raise

    log.info(
        "Load complete: %d rows across %d tables (%d failures)",
        total, len(TARGETS) - failures, failures,
    )
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())