BEGIN;

TRUNCATE TABLE
    core.fact_transaction_line,
    core.dim_customer,
    core.dim_product,
    core.dim_geography,
    core.dim_date
RESTART IDENTITY CASCADE;

INSERT INTO core.dim_date (
    date_key,
    full_date,
    calendar_year,
    calendar_quarter,
    calendar_month,
    month_name,
    year_month,
    iso_week,
    day_of_month,
    day_of_week,
    day_name,
    is_weekend
)
SELECT
    TO_CHAR(d::DATE, 'YYYYMMDD')::INTEGER AS date_key,
    d::DATE AS full_date,
    EXTRACT(YEAR FROM d)::SMALLINT AS calendar_year,
    EXTRACT(QUARTER FROM d)::SMALLINT AS calendar_quarter,
    EXTRACT(MONTH FROM d)::SMALLINT AS calendar_month,
    TO_CHAR(d, 'FMMonth') AS month_name,
    TO_CHAR(d, 'YYYY-MM') AS year_month,
    EXTRACT(WEEK FROM d)::SMALLINT AS iso_week,
    EXTRACT(DAY FROM d)::SMALLINT AS day_of_month,
    EXTRACT(ISODOW FROM d)::SMALLINT AS day_of_week,
    TO_CHAR(d, 'FMDay') AS day_name,
    EXTRACT(ISODOW FROM d) IN (6, 7) AS is_weekend
FROM GENERATE_SERIES(
    (SELECT MIN(invoice_date)::DATE FROM staging.retail_line),
    (SELECT MAX(invoice_date)::DATE FROM staging.retail_line),
    INTERVAL '1 day'
) AS calendar(d);

INSERT INTO core.dim_customer (customer_id)
SELECT DISTINCT customer_id
FROM staging.retail_line
WHERE customer_id IS NOT NULL
  AND BTRIM(customer_id) <> ''
ORDER BY customer_id;

WITH ranked_product_description AS (
    SELECT
        stock_code,
        NULLIF(BTRIM(description), '') AS product_description,
        ROW_NUMBER() OVER (
            PARTITION BY stock_code
            ORDER BY
                (description IS NULL OR BTRIM(description) = '') ASC,
                invoice_date DESC NULLS LAST,
                source_sheet,
                source_row_number DESC
        ) AS rn
    FROM staging.retail_line
    WHERE stock_code IS NOT NULL
      AND BTRIM(stock_code) <> ''
)
INSERT INTO core.dim_product (stock_code, product_description)
SELECT stock_code, product_description
FROM ranked_product_description
WHERE rn = 1
ORDER BY stock_code;

INSERT INTO core.dim_geography (country)
SELECT DISTINCT BTRIM(country)
FROM staging.retail_line
WHERE country IS NOT NULL
  AND BTRIM(country) <> ''
ORDER BY BTRIM(country);

WITH classified AS (
    SELECT
        s.*,
        CASE
            WHEN s.is_cancellation OR COALESCE(s.quantity, 0) < 0 THEN 'cancellation'
            WHEN COALESCE(s.quantity, 0) > 0 AND COALESCE(s.unit_price, 0) > 0 THEN 'sale'
            ELSE 'non_revenue'
        END AS event_type,
        ROW_NUMBER() OVER (
            PARTITION BY
                invoice_no,
                stock_code,
                description,
                quantity,
                invoice_date,
                unit_price,
                customer_id,
                country,
                is_cancellation,
                line_value
            ORDER BY source_sheet, source_row_number
        ) AS exact_row_occurrence
    FROM staging.retail_line AS s
)
INSERT INTO core.fact_transaction_line (
    source_sheet,
    source_row_number,
    invoice_no,
    invoice_timestamp,
    date_key,
    customer_key,
    product_key,
    geography_key,
    quantity,
    unit_price,
    line_value,
    is_cancellation,
    event_type,
    exact_row_occurrence,
    is_repeated_exact_row
)
SELECT
    c.source_sheet,
    c.source_row_number,
    c.invoice_no,
    c.invoice_date,
    d.date_key,
    customer.customer_key,
    product.product_key,
    geography.geography_key,
    c.quantity,
    c.unit_price,
    c.line_value,
    c.is_cancellation,
    c.event_type,
    c.exact_row_occurrence,
    c.exact_row_occurrence > 1
FROM classified AS c
LEFT JOIN core.dim_date AS d
    ON d.full_date = c.invoice_date::DATE
LEFT JOIN core.dim_customer AS customer
    ON customer.customer_id = c.customer_id
LEFT JOIN core.dim_product AS product
    ON product.stock_code = c.stock_code
LEFT JOIN core.dim_geography AS geography
    ON geography.country = BTRIM(c.country);

COMMIT;
