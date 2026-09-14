from __future__ import annotations

import json
import os
from datetime import date, datetime
from decimal import Decimal

import psycopg
from psycopg.rows import dict_row


def json_default(value: object) -> str:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"Cannot serialise {type(value).__name__}")


def main() -> None:
    dsn = os.environ["RETAILIQ_TEST_DB_URL"]
    query = """
    WITH fact AS (
        SELECT
            COUNT(*) AS fact_rows,
            MIN(invoice_timestamp)::DATE AS min_transaction_date,
            MAX(invoice_timestamp)::DATE AS max_transaction_date,
            COUNT(DISTINCT product_key) AS products,
            COUNT(DISTINCT geography_key) AS countries,
            COUNT(*) FILTER (WHERE is_repeated_exact_row) AS repeated_exact_rows,
            COUNT(DISTINCT invoice_no) FILTER (WHERE event_type = 'sale') AS sale_orders,
            COUNT(DISTINCT invoice_no) FILTER (WHERE event_type = 'cancellation')
                AS cancellation_orders,
            SUM(CASE WHEN event_type = 'sale' THEN line_value ELSE 0 END)
                AS gross_sales_value,
            SUM(
                CASE
                    WHEN event_type = 'cancellation' THEN ABS(COALESCE(line_value, 0))
                    ELSE 0
                END
            ) AS cancellation_value
        FROM core.fact_transaction_line
    ),
    customer AS (
        SELECT
            COUNT(*) AS known_customers,
            COUNT(*) FILTER (WHERE is_repeat_customer) AS repeat_customers
        FROM mart.customer_summary
    ),
    quality AS (
        SELECT
            COUNT(*) FILTER (WHERE customer_id IS NULL) AS missing_customer_id_rows
        FROM staging.retail_line
    ),
    reconcile AS (
        SELECT * FROM mart.reconciliation_summary
    )
    SELECT
        f.fact_rows,
        f.min_transaction_date,
        f.max_transaction_date,
        f.products,
        f.countries,
        f.repeated_exact_rows,
        f.sale_orders,
        f.cancellation_orders,
        f.gross_sales_value,
        f.cancellation_value,
        f.gross_sales_value - f.cancellation_value AS net_sales_value,
        c.known_customers,
        c.repeat_customers,
        c.repeat_customers::NUMERIC / NULLIF(c.known_customers, 0) AS repeat_customer_rate,
        q.missing_customer_id_rows,
        r.staging_row_count,
        r.fact_row_count,
        r.row_count_difference,
        r.line_value_difference
    FROM fact AS f
    CROSS JOIN customer AS c
    CROSS JOIN quality AS q
    CROSS JOIN reconcile AS r
    """

    with psycopg.connect(dsn, row_factory=dict_row) as connection:
        result = connection.execute(query).fetchone()

    if result is None:
        raise RuntimeError("Verified metrics query returned no result")

    print("VERIFIED_METRICS_JSON")
    print(json.dumps(dict(result), indent=2, default=json_default))


if __name__ == "__main__":
    main()
