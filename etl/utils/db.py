"""Database connection utilities."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

load_dotenv()


def _cfg() -> dict[str, str]:
    return {
        "host": os.getenv("POSTGRES_HOST", "postgres"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "dbname": os.getenv("POSTGRES_DB", "postgres"),
    }


def get_engine() -> Engine:
    """SQLAlchemy engine for pandas reads and ad-hoc queries."""
    c = _cfg()
    url = (
        f"postgresql+psycopg2://{c['user']}:{c['password']}"
        f"@{c['host']}:{c['port']}/{c['dbname']}"
    )
    return create_engine(url, future=True, pool_pre_ping=True)


@contextmanager
def raw_connection():
    """Raw psycopg2 connection — needed for COPY (SQLAlchemy doesn't expose it cleanly)."""
    c = _cfg()
    conn = psycopg2.connect(
        host=c["host"],
        port=c["port"],
        user=c["user"],
        password=c["password"],
        dbname=c["dbname"],
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_sql_file(path: str | Path) -> None:
    """Execute a .sql file as a single batch."""
    sql = Path(path).read_text(encoding="utf-8")
    with raw_connection() as conn, conn.cursor() as cur:
        cur.execute(sql)


def execute_sql_directory(directory_path: str | Path) -> None:
    """Execute all .sql files in a directory in alphabetical order."""
    path = Path(directory_path)
    sql_files = sorted(path.glob("*.sql"))
    for sql_file in sql_files:
        execute_sql_file(sql_file)
