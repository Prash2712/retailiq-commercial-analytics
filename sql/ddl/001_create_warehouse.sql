BEGIN;

CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS mart;

CREATE TABLE IF NOT EXISTS staging.retail_line (
    source_sheet TEXT NOT NULL,
    source_row_number BIGINT NOT NULL,
    invoice_no TEXT,
    stock_code TEXT,
    description TEXT,
    quantity NUMERIC,
    invoice_date TIMESTAMP,
    unit_price NUMERIC(18, 4),
    customer_id TEXT,
    country TEXT,
    is_cancellation BOOLEAN NOT NULL,
    line_value NUMERIC(20, 4),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source_sheet, source_row_number)
);

CREATE TABLE IF NOT EXISTS core.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    calendar_year SMALLINT NOT NULL,
    calendar_quarter SMALLINT NOT NULL,
    calendar_month SMALLINT NOT NULL,
    month_name TEXT NOT NULL,
    year_month TEXT NOT NULL,
    iso_week SMALLINT NOT NULL,
    day_of_month SMALLINT NOT NULL,
    day_of_week SMALLINT NOT NULL,
    day_name TEXT NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS core.dim_customer (
    customer_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS core.dim_product (
    product_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stock_code TEXT NOT NULL UNIQUE,
    product_description TEXT
);

CREATE TABLE IF NOT EXISTS core.dim_geography (
    geography_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS core.fact_transaction_line (
    transaction_line_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_sheet TEXT NOT NULL,
    source_row_number BIGINT NOT NULL,
    invoice_no TEXT,
    invoice_timestamp TIMESTAMP,
    date_key INTEGER REFERENCES core.dim_date(date_key),
    customer_key BIGINT REFERENCES core.dim_customer(customer_key),
    product_key BIGINT REFERENCES core.dim_product(product_key),
    geography_key BIGINT REFERENCES core.dim_geography(geography_key),
    quantity NUMERIC,
    unit_price NUMERIC(18, 4),
    line_value NUMERIC(20, 4),
    is_cancellation BOOLEAN NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('sale', 'cancellation', 'non_revenue')),
    exact_row_occurrence INTEGER NOT NULL CHECK (exact_row_occurrence >= 1),
    is_repeated_exact_row BOOLEAN NOT NULL,
    UNIQUE (source_sheet, source_row_number)
);

CREATE INDEX IF NOT EXISTS idx_fact_invoice_timestamp
    ON core.fact_transaction_line (invoice_timestamp);
CREATE INDEX IF NOT EXISTS idx_fact_invoice_no
    ON core.fact_transaction_line (invoice_no);
CREATE INDEX IF NOT EXISTS idx_fact_customer_key
    ON core.fact_transaction_line (customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_product_key
    ON core.fact_transaction_line (product_key);
CREATE INDEX IF NOT EXISTS idx_fact_geography_key
    ON core.fact_transaction_line (geography_key);
CREATE INDEX IF NOT EXISTS idx_fact_event_type
    ON core.fact_transaction_line (event_type);

COMMIT;
