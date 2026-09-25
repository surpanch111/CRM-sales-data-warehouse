"""
Stage 1 — Extract.

Reads the four Maven CRM CSVs from data/raw/, performs lightweight cleaning
(whitespace stripping, dtype coercion, date parsing), then writes columnar
parquet snapshots to data/staging/.

Parquet is roughly 5-10x smaller than CSV and preserves dtypes, which matters
when this scales up. Same code, better behavior on big data.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import pandas as pd

from etl.utils.logger import get_logger

log = get_logger(__name__)

# Resolve project paths relative to this file (works from any cwd)
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
STAGING_DIR = ROOT / "data" / "staging"
STAGING_DIR.mkdir(parents=True, exist_ok=True)


# Known source data inconsistencies — fix early, before staging.
# products.csv has "GTX Pro"; sales_pipeline.csv has "GTXPro". Affects 1480 rows.
# Discovered via orphan-reference diagnostic in Stage 5.
PRODUCT_NAME_FIXES = {
    "GTXPro": "GTX Pro",
}

# Sector spelling typo in accounts.csv (12 accounts affected).
SECTOR_NAME_FIXES = {
    "technolgy": "technology",
}


# ---------- Cleaning functions: one per source file ----------


def _clean_accounts(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower() for c in df.columns]
    for col in ("account", "sector", "office_location", "subsidiary_of"):
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()

    # Normalize known sector spelling inconsistencies
    if "sector" in df.columns:
        before_fix = (df["sector"] == "technolgy").sum()
        df["sector"] = df["sector"].replace(SECTOR_NAME_FIXES)
        if before_fix:
            log.info("  normalized %d 'technolgy' values to 'technology'", before_fix)
    if "year_established" in df.columns:
        df["year_established"] = pd.to_numeric(
            df["year_established"], errors="coerce"
        ).astype("Int64")
    if "employees" in df.columns:
        df["employees"] = pd.to_numeric(df["employees"], errors="coerce").astype(
            "Int64"
        )
    if "revenue" in df.columns:
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
    return df


def _clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower() for c in df.columns]
    for col in ("product", "series"):
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
    if "sales_price" in df.columns:
        df["sales_price"] = pd.to_numeric(df["sales_price"], errors="coerce")
    return df


def _clean_sales_teams(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower() for c in df.columns]
    for col in df.columns:
        df[col] = df[col].astype("string").str.strip()
    return df


def _clean_sales_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower() for c in df.columns]

    for col in ("opportunity_id", "sales_agent", "product", "account", "deal_stage"):
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()

    # Normalize known product name inconsistencies before they cause join misses
    if "product" in df.columns:
        before_fix = (df["product"] == "GTXPro").sum()
        df["product"] = df["product"].replace(PRODUCT_NAME_FIXES)
        if before_fix:
            log.info("  normalized %d 'GTXPro' values to 'GTX Pro'", before_fix)

    # Maven uses YYYY-MM-DD strings; coerce errors to NaT rather than crash
    for col in ("engage_date", "close_date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

    if "close_value" in df.columns:
        df["close_value"] = pd.to_numeric(df["close_value"], errors="coerce")

    # Drop rows missing the primary key — they can't go anywhere useful
    if "opportunity_id" in df.columns:
        before = len(df)
        df = df.dropna(subset=["opportunity_id"])
        dropped = before - len(df)
        if dropped:
            log.warning("Dropped %d rows with NULL opportunity_id", dropped)

    return df


# ---------- Source registry ----------

# (csv filename, parquet filename, cleaner function)
SOURCES: list[tuple[str, str, Callable[[pd.DataFrame], pd.DataFrame]]] = [
    ("accounts.csv", "accounts.parquet", _clean_accounts),
    ("products.csv", "products.parquet", _clean_products),
    ("sales_teams.csv", "sales_teams.parquet", _clean_sales_teams),
    ("sales_pipeline.csv", "sales_pipeline.parquet", _clean_sales_pipeline),
]


def extract_one(csv_name: str, parquet_name: str, cleaner) -> int:
    """Extract a single file. Returns row count, or -1 on failure."""
    csv_path = RAW_DIR / csv_name
    if not csv_path.exists():
        log.error("Missing source file: %s", csv_path)
        log.error(
            "Download the CRM + Sales dataset from Maven Analytics and place CSVs in data/raw/"
        )
        return -1

    log.info("Reading %s", csv_path.name)
    df = pd.read_csv(csv_path)
    raw_rows, raw_cols = df.shape
    log.info("  raw shape: %d rows x %d cols", raw_rows, raw_cols)

    df = cleaner(df)
    log.info("  cleaned: %d rows", len(df))

    out_path = STAGING_DIR / parquet_name
    df.to_parquet(out_path, index=False, engine="pyarrow", compression="snappy")
    size_kb = out_path.stat().st_size / 1024
    log.info("  -> %s (%.1f KB)", out_path.name, size_kb)
    return len(df)


def main() -> int:
    log.info("=== Stage 3: Extract ===")

    if not RAW_DIR.exists() or not any(RAW_DIR.glob("*.csv")):
        log.error("No CSVs found in %s", RAW_DIR)
        log.error("Place the four Maven CRM CSVs there and try again.")
        return 1

    total_rows = 0
    failures = 0
    for csv_name, parquet_name, cleaner in SOURCES:
        n = extract_one(csv_name, parquet_name, cleaner)
        if n < 0:
            failures += 1
        else:
            total_rows += n

    log.info(
        "Extract complete: %d rows across %d files (%d failures)",
        total_rows,
        len(SOURCES) - failures,
        failures,
    )
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
