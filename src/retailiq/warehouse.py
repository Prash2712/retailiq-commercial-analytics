from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg
import pyarrow.parquet as pq
from psycopg.rows import dict_row

from retailiq.config import PROJECT_ROOT

DEFAULT_DB_URL = "postgresql://retailiq:retailiq@localhost:5432/retailiq"
SQL_ROOT = PROJECT_ROOT / "sql"

STAGING_COLUMNS = [
    "source_sheet",
    "source_row_number",
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
    "is_cancellation",
    "line_value",
]


def database_url(value: str | None = None) -> str:
    return value or os.getenv("RETAILIQ_DB_URL", DEFAULT_DB_URL)


def _to_db_value(value: Any) -> Any:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    if hasattr(value, "item"):
        return value.item()
    return value


def execute_sql_file(path: Path, dsn: str | None = None) -> None:
    sql_text = path.read_text(encoding="utf-8")
    with psycopg.connect(database_url(dsn), autocommit=True) as connection:
        connection.execute(sql_text)


def initialise_warehouse(dsn: str | None = None) -> None:
    execute_sql_file(SQL_ROOT / "ddl" / "001_create_warehouse.sql", dsn)


def load_staging(
    parquet_path: Path,
    dsn: str | None = None,
    batch_size: int = 50_000,
) -> int:
    if not parquet_path.exists():
        raise FileNotFoundError(f"Normalised parquet not found: {parquet_path}")

    parquet = pq.ParquetFile(parquet_path)
    available = set(parquet.schema_arrow.names)
    missing = set(STAGING_COLUMNS).difference(available)
    if missing:
        raise ValueError(f"Parquet schema missing warehouse columns: {sorted(missing)}")

    loaded_rows = 0
    copy_sql = f"COPY staging.retail_line ({', '.join(STAGING_COLUMNS)}) FROM STDIN"

    with psycopg.connect(database_url(dsn)) as connection:
        connection.execute("TRUNCATE TABLE staging.retail_line")
        with connection.cursor().copy(copy_sql) as copy:
            for batch in parquet.iter_batches(batch_size=batch_size, columns=STAGING_COLUMNS):
                frame = batch.to_pandas()
                for row in frame.itertuples(index=False, name=None):
                    copy.write_row(tuple(_to_db_value(value) for value in row))
                loaded_rows += len(frame)

    return loaded_rows


def build_core_and_marts(dsn: str | None = None) -> None:
    execute_sql_file(SQL_ROOT / "models" / "010_build_core_model.sql", dsn)
    execute_sql_file(SQL_ROOT / "marts" / "020_create_commercial_marts.sql", dsn)


def reconciliation_summary(dsn: str | None = None) -> dict[str, Any]:
    query = "SELECT * FROM mart.reconciliation_summary"
    with psycopg.connect(database_url(dsn), row_factory=dict_row) as connection:
        row = connection.execute(query).fetchone()
    if row is None:
        raise RuntimeError("Reconciliation view returned no result")
    return dict(row)


def assert_reconciled(summary: dict[str, Any]) -> None:
    if summary["row_count_difference"] != 0:
        raise RuntimeError(f"Warehouse row-count reconciliation failed: {summary}")
    if summary["line_value_difference"] != 0:
        raise RuntimeError(f"Warehouse value reconciliation failed: {summary}")


def build_warehouse(parquet_path: Path, dsn: str | None = None) -> dict[str, Any]:
    initialise_warehouse(dsn)
    load_staging(parquet_path, dsn)
    build_core_and_marts(dsn)
    summary = reconciliation_summary(dsn)
    assert_reconciled(summary)
    return summary
