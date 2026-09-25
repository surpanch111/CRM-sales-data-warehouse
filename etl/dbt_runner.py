import subprocess
from pathlib import Path

from etl.utils.logger import get_logger

log = get_logger(__name__)

DBT_PROJECT_DIR = Path("/usr/local/airflow/crm_warehouse_dbt")


def run_dbt_models():
    """Run dbt models."""

    log.info("=== Running dbt models ===")

    result = subprocess.run(
    [
        "dbt",
        "run",
        "--profiles-dir",
        "/usr/local/airflow",
    ],
    cwd=DBT_PROJECT_DIR,
    capture_output=True,
    text=True,
    )

    log.info(result.stdout)

    if result.returncode != 0:
        log.error(result.stderr)
        raise Exception("dbt run failed")

    log.info("dbt models completed successfully")


def run_dbt_tests():
    """Run dbt tests."""

    log.info("=== Running dbt tests ===")

    result = subprocess.run(
    [
        "dbt",
        "test",
        "--profiles-dir",
        "/usr/local/airflow",
    ],
    cwd=DBT_PROJECT_DIR,
    capture_output=True,
    text=True,
    )

    log.info(result.stdout)

    if result.returncode != 0:
        log.error(result.stderr)
        raise Exception("dbt test failed")

    log.info("dbt tests completed successfully")
