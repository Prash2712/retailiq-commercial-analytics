from __future__ import annotations

import os
from decimal import Decimal

import pandas as pd
import psycopg
import pytest

from retailiq.warehouse import build_warehouse

TEST_DB_URL = os.getenv("RETAILIQ_TEST_DB_URL")
pytestmark = pytest.mark.skipif(
    not TEST_DB_URL,
    reason="PostgreSQL integration database not configured",
)


def synthetic_transactions() -> pd.DataFrame:
    timestamp = pd.Timestamp("2011-01-10 10:00:00")
    return pd.DataFrame(
        {
            "source_sheet": ["test"] * 6,
            "source_row_number": [2, 3, 4, 5, 6, 7],
            "invoice_no": ["100001", "100002", "100003", "100003", "C100004", "100005"],
            "stock_code": ["A", "B", "A", "A", "A", "FREE"],
            "description": [
                "Product A",
                "Product B",
                "Product A",
                "Product A",
                "Product A",
                "Sample",
            ],
            "quantity": [2, 1, 3, 3, -1, 1],
            "invoice_date": [timestamp] * 6,
            "unit_price": [10.0, 5.0, 10.0, 10.0, 10.0, 0.0],
            "customer_id": ["C1", "C1", "C2", "C2", "C1", None],
            "country": ["United Kingdom"] * 6,
            "is_cancellation": [False, False, False, False, True, False],
            "line_value": [20.0, 5.0, 30.0, 30.0, -10.0, 0.0],
        }
    )


def test_warehouse_build_reconciles_and_populates_commercial_marts(tmp_path) -> None:
    parquet_path = tmp_path / "synthetic.parquet"
    synthetic_transactions().to_parquet(parquet_path, index=False)

    summary = build_warehouse(parquet_path, TEST_DB_URL)

    assert summary["staging_row_count"] == 6
    assert summary["fact_row_count"] == 6
    assert summary["row_count_difference"] == 0
    assert summary["line_value_difference"] == Decimal("0.0000")

    with psycopg.connect(TEST_DB_URL) as connection:
        commercial = connection.execute(
            """
            SELECT
                SUM(gross_sales_value),
                SUM(cancellation_value),
                SUM(net_sales_value),
                SUM(orders),
                MAX(average_order_value)
            FROM mart.daily_commercial_performance
            """
        ).fetchone()
        repeated_rows = connection.execute(
            "SELECT COUNT(*) FROM core.fact_transaction_line WHERE is_repeated_exact_row"
        ).fetchone()[0]
        customer_count = connection.execute(
            "SELECT COUNT(*) FROM mart.customer_summary"
        ).fetchone()[0]

    assert commercial == (
        Decimal("85.0000"),
        Decimal("10.0000"),
        Decimal("75.0000"),
        3,
        Decimal("25.0000000000000000"),
    )
    assert repeated_rows == 1
    assert customer_count == 2
