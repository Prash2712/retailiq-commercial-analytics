BEGIN;

CREATE OR REPLACE VIEW mart.daily_commercial_performance AS
WITH daily AS (
    SELECT
        d.full_date,
        d.calendar_year,
        d.calendar_quarter,
        d.calendar_month,
        d.month_name,
        d.year_month,
        SUM(CASE WHEN f.event_type = 'sale' THEN f.line_value ELSE 0 END) AS gross_sales_value,
        SUM(
            CASE
                WHEN f.event_type = 'cancellation' THEN ABS(COALESCE(f.line_value, 0))
                ELSE 0
            END
        ) AS cancellation_value,
        COUNT(DISTINCT f.invoice_no) FILTER (WHERE f.event_type = 'sale') AS orders,
        COUNT(DISTINCT f.invoice_no) FILTER (WHERE f.event_type = 'cancellation')
            AS cancellation_orders,
        SUM(CASE WHEN f.event_type = 'sale' THEN f.quantity ELSE 0 END) AS units_sold,
        COUNT(DISTINCT f.customer_key) FILTER (WHERE f.event_type = 'sale') AS active_customers
    FROM core.fact_transaction_line AS f
    JOIN core.dim_date AS d
        ON d.date_key = f.date_key
    GROUP BY
        d.full_date,
        d.calendar_year,
        d.calendar_quarter,
        d.calendar_month,
        d.month_name,
        d.year_month
)
SELECT
    *,
    gross_sales_value - cancellation_value AS net_sales_value,
    gross_sales_value / NULLIF(orders, 0) AS average_order_value
FROM daily;

CREATE OR REPLACE VIEW mart.customer_summary AS
WITH reference_date AS (
    SELECT MAX(invoice_timestamp::DATE) AS max_sale_date
    FROM core.fact_transaction_line
    WHERE event_type = 'sale'
),
customer_activity AS (
    SELECT
        c.customer_id,
        MIN(f.invoice_timestamp::DATE) FILTER (WHERE f.event_type = 'sale') AS first_purchase_date,
        MAX(f.invoice_timestamp::DATE) FILTER (WHERE f.event_type = 'sale') AS last_purchase_date,
        COUNT(DISTINCT f.invoice_no) FILTER (WHERE f.event_type = 'sale') AS order_count,
        SUM(CASE WHEN f.event_type = 'sale' THEN f.quantity ELSE 0 END) AS units_purchased,
        SUM(CASE WHEN f.event_type = 'sale' THEN f.line_value ELSE 0 END) AS gross_sales_value,
        SUM(
            CASE
                WHEN f.event_type = 'cancellation' THEN ABS(COALESCE(f.line_value, 0))
                ELSE 0
            END
        ) AS cancellation_value
    FROM core.dim_customer AS c
    JOIN core.fact_transaction_line AS f
        ON f.customer_key = c.customer_key
    GROUP BY c.customer_id
)
SELECT
    a.customer_id,
    a.first_purchase_date,
    a.last_purchase_date,
    a.order_count,
    a.units_purchased,
    a.gross_sales_value,
    a.cancellation_value,
    a.gross_sales_value - a.cancellation_value AS net_sales_value,
    r.max_sale_date - a.last_purchase_date AS recency_days,
    a.order_count >= 2 AS is_repeat_customer
FROM customer_activity AS a
CROSS JOIN reference_date AS r
WHERE a.order_count > 0;

CREATE OR REPLACE VIEW mart.customer_rfm AS
WITH scored AS (
    SELECT
        customer_id,
        recency_days,
        order_count AS frequency,
        net_sales_value AS monetary_value,
        NTILE(5) OVER (ORDER BY recency_days DESC NULLS FIRST) AS recency_score,
        NTILE(5) OVER (ORDER BY order_count ASC) AS frequency_score,
        NTILE(5) OVER (ORDER BY net_sales_value ASC) AS monetary_score
    FROM mart.customer_summary
)
SELECT
    *,
    CONCAT(recency_score, frequency_score, monetary_score) AS rfm_score
FROM scored;

CREATE OR REPLACE VIEW mart.customer_cohort_retention AS
WITH sales_activity AS (
    SELECT DISTINCT
        c.customer_id,
        DATE_TRUNC('month', f.invoice_timestamp)::DATE AS activity_month
    FROM core.fact_transaction_line AS f
    JOIN core.dim_customer AS c
        ON c.customer_key = f.customer_key
    WHERE f.event_type = 'sale'
),
first_purchase AS (
    SELECT
        customer_id,
        MIN(activity_month) AS cohort_month
    FROM sales_activity
    GROUP BY customer_id
),
cohort_activity AS (
    SELECT
        fp.cohort_month,
        sa.activity_month,
        (
            (EXTRACT(YEAR FROM sa.activity_month) - EXTRACT(YEAR FROM fp.cohort_month)) * 12
            + EXTRACT(MONTH FROM sa.activity_month)
            - EXTRACT(MONTH FROM fp.cohort_month)
        )::INTEGER AS months_since_first_purchase,
        COUNT(DISTINCT sa.customer_id) AS active_customers
    FROM sales_activity AS sa
    JOIN first_purchase AS fp
        ON fp.customer_id = sa.customer_id
    GROUP BY fp.cohort_month, sa.activity_month
),
cohort_size AS (
    SELECT
        cohort_month,
        COUNT(*) AS cohort_customers
    FROM first_purchase
    GROUP BY cohort_month
)
SELECT
    ca.cohort_month,
    ca.activity_month,
    ca.months_since_first_purchase,
    cs.cohort_customers,
    ca.active_customers,
    ca.active_customers::NUMERIC / NULLIF(cs.cohort_customers, 0) AS retention_rate
FROM cohort_activity AS ca
JOIN cohort_size AS cs
    ON cs.cohort_month = ca.cohort_month;

CREATE OR REPLACE VIEW mart.product_performance AS
SELECT
    p.stock_code,
    p.product_description,
    SUM(CASE WHEN f.event_type = 'sale' THEN f.line_value ELSE 0 END) AS gross_sales_value,
    SUM(
        CASE
            WHEN f.event_type = 'cancellation' THEN ABS(COALESCE(f.line_value, 0))
            ELSE 0
        END
    ) AS cancellation_value,
    SUM(CASE WHEN f.event_type = 'sale' THEN f.line_value ELSE 0 END)
        - SUM(
            CASE
                WHEN f.event_type = 'cancellation' THEN ABS(COALESCE(f.line_value, 0))
                ELSE 0
            END
        ) AS net_sales_value,
    SUM(CASE WHEN f.event_type = 'sale' THEN f.quantity ELSE 0 END) AS units_sold,
    COUNT(DISTINCT f.invoice_no) FILTER (WHERE f.event_type = 'sale') AS sales_orders,
    COUNT(DISTINCT f.customer_key) FILTER (WHERE f.event_type = 'sale') AS customers
FROM core.dim_product AS p
JOIN core.fact_transaction_line AS f
    ON f.product_key = p.product_key
GROUP BY p.stock_code, p.product_description;

CREATE OR REPLACE VIEW mart.country_performance AS
SELECT
    g.country,
    SUM(CASE WHEN f.event_type = 'sale' THEN f.line_value ELSE 0 END) AS gross_sales_value,
    SUM(
        CASE
            WHEN f.event_type = 'cancellation' THEN ABS(COALESCE(f.line_value, 0))
            ELSE 0
        END
    ) AS cancellation_value,
    SUM(CASE WHEN f.event_type = 'sale' THEN f.line_value ELSE 0 END)
        - SUM(
            CASE
                WHEN f.event_type = 'cancellation' THEN ABS(COALESCE(f.line_value, 0))
                ELSE 0
            END
        ) AS net_sales_value,
    COUNT(DISTINCT f.invoice_no) FILTER (WHERE f.event_type = 'sale') AS orders,
    COUNT(DISTINCT f.customer_key) FILTER (WHERE f.event_type = 'sale') AS customers
FROM core.dim_geography AS g
JOIN core.fact_transaction_line AS f
    ON f.geography_key = g.geography_key
GROUP BY g.country;

CREATE OR REPLACE VIEW mart.data_quality_summary AS
SELECT 'source_rows'::TEXT AS metric, COUNT(*)::NUMERIC AS value
FROM staging.retail_line
UNION ALL
SELECT 'missing_customer_id', COUNT(*)::NUMERIC
FROM staging.retail_line
WHERE customer_id IS NULL
UNION ALL
SELECT 'missing_description', COUNT(*)::NUMERIC
FROM staging.retail_line
WHERE description IS NULL OR BTRIM(description) = ''
UNION ALL
SELECT 'non_positive_quantity_rows', COUNT(*)::NUMERIC
FROM staging.retail_line
WHERE quantity <= 0
UNION ALL
SELECT 'non_positive_unit_price_rows', COUNT(*)::NUMERIC
FROM staging.retail_line
WHERE unit_price <= 0
UNION ALL
SELECT 'cancellation_rows', COUNT(*)::NUMERIC
FROM staging.retail_line
WHERE is_cancellation
UNION ALL
SELECT 'repeated_exact_rows', COUNT(*)::NUMERIC
FROM core.fact_transaction_line
WHERE is_repeated_exact_row;

CREATE OR REPLACE VIEW mart.reconciliation_summary AS
WITH staging_totals AS (
    SELECT
        COUNT(*) AS row_count,
        COALESCE(SUM(line_value), 0) AS line_value
    FROM staging.retail_line
),
fact_totals AS (
    SELECT
        COUNT(*) AS row_count,
        COALESCE(SUM(line_value), 0) AS line_value
    FROM core.fact_transaction_line
)
SELECT
    s.row_count AS staging_row_count,
    f.row_count AS fact_row_count,
    f.row_count - s.row_count AS row_count_difference,
    s.line_value AS staging_line_value,
    f.line_value AS fact_line_value,
    f.line_value - s.line_value AS line_value_difference
FROM staging_totals AS s
CROSS JOIN fact_totals AS f;

COMMIT;
