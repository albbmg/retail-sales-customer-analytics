CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.transactions (
    invoice_no TEXT,
    stock_code TEXT,
    description TEXT,
    quantity INTEGER,
    invoice_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    unit_price DOUBLE PRECISION,
    customer_id BIGINT,
    country TEXT,
    source_period TEXT NOT NULL,
    source_row INTEGER NOT NULL CHECK (source_row >= 2),
    is_cancellation BOOLEAN NOT NULL,
    line_amount DOUBLE PRECISION,
    PRIMARY KEY (source_period, source_row)
);
