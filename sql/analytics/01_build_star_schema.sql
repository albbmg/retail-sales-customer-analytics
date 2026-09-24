CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year SMALLINT NOT NULL,
    quarter SMALLINT NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month SMALLINT NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_name TEXT NOT NULL,
    day SMALLINT NOT NULL CHECK (day BETWEEN 1 AND 31),
    iso_day_of_week SMALLINT NOT NULL CHECK (iso_day_of_week BETWEEN 1 AND 7),
    day_name TEXT NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_customer (
    customer_key BIGINT PRIMARY KEY,
    customer_id BIGINT UNIQUE,
    customer_label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_product (
    product_key BIGINT PRIMARY KEY,
    stock_code TEXT UNIQUE,
    product_description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analytics.dim_country (
    country_key BIGINT PRIMARY KEY,
    country_name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS analytics.fact_sales (
    source_period TEXT NOT NULL,
    source_row INTEGER NOT NULL,
    invoice_no TEXT,
    invoice_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    customer_key BIGINT NOT NULL REFERENCES analytics.dim_customer(customer_key),
    product_key BIGINT NOT NULL REFERENCES analytics.dim_product(product_key),
    country_key BIGINT NOT NULL REFERENCES analytics.dim_country(country_key),
    quantity INTEGER,
    unit_price NUMERIC(18, 4),
    line_amount NUMERIC(20, 4),
    is_cancellation BOOLEAN NOT NULL,
    PRIMARY KEY (source_period, source_row)
);

TRUNCATE TABLE
    analytics.fact_sales,
    analytics.dim_date,
    analytics.dim_customer,
    analytics.dim_product,
    analytics.dim_country;

INSERT INTO analytics.dim_customer (
    customer_key,
    customer_id,
    customer_label
)
VALUES (0, NULL, 'Unknown customer');

INSERT INTO analytics.dim_product (
    product_key,
    stock_code,
    product_description
)
VALUES (0, NULL, 'Unknown product');

INSERT INTO analytics.dim_country (
    country_key,
    country_name
)
VALUES (0, NULL);

INSERT INTO analytics.dim_date (
    date_key,
    full_date,
    year,
    quarter,
    month,
    month_name,
    day,
    iso_day_of_week,
    day_name,
    is_weekend
)
SELECT
    TO_CHAR(calendar_date, 'YYYYMMDD')::INTEGER AS date_key,
    calendar_date,
    EXTRACT(YEAR FROM calendar_date)::SMALLINT AS year,
    EXTRACT(QUARTER FROM calendar_date)::SMALLINT AS quarter,
    EXTRACT(MONTH FROM calendar_date)::SMALLINT AS month,
    TRIM(TO_CHAR(calendar_date, 'Month')) AS month_name,
    EXTRACT(DAY FROM calendar_date)::SMALLINT AS day,
    EXTRACT(ISODOW FROM calendar_date)::SMALLINT AS iso_day_of_week,
    TRIM(TO_CHAR(calendar_date, 'Day')) AS day_name,
    EXTRACT(ISODOW FROM calendar_date) IN (6, 7) AS is_weekend
FROM GENERATE_SERIES(
    (SELECT MIN(invoice_date)::DATE FROM staging.transactions),
    (SELECT MAX(invoice_date)::DATE FROM staging.transactions),
    INTERVAL '1 day'
) AS generated(calendar_timestamp)
CROSS JOIN LATERAL (
    SELECT generated.calendar_timestamp::DATE AS calendar_date
) AS calendar
ORDER BY calendar_date;

INSERT INTO analytics.dim_customer (
    customer_key,
    customer_id,
    customer_label
)
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id)::BIGINT AS customer_key,
    customer_id,
    'Customer ' || customer_id::TEXT AS customer_label
FROM (
    SELECT DISTINCT customer_id
    FROM staging.transactions
    WHERE customer_id IS NOT NULL
) AS customers
ORDER BY customer_id;

WITH canonical_products AS (
    SELECT DISTINCT ON (stock_code)
        stock_code,
        description
    FROM staging.transactions
    WHERE stock_code IS NOT NULL
    ORDER BY
        stock_code,
        (description IS NOT NULL) DESC,
        invoice_date DESC NULLS LAST,
        source_period DESC,
        source_row DESC
)
INSERT INTO analytics.dim_product (
    product_key,
    stock_code,
    product_description
)
SELECT
    ROW_NUMBER() OVER (ORDER BY stock_code)::BIGINT AS product_key,
    stock_code,
    COALESCE(description, 'No description') AS product_description
FROM canonical_products
ORDER BY stock_code;

INSERT INTO analytics.dim_country (
    country_key,
    country_name
)
SELECT
    ROW_NUMBER() OVER (ORDER BY country)::BIGINT AS country_key,
    country
FROM (
    SELECT DISTINCT country
    FROM staging.transactions
    WHERE country IS NOT NULL
) AS countries
ORDER BY country;

INSERT INTO analytics.fact_sales (
    source_period,
    source_row,
    invoice_no,
    invoice_timestamp,
    date_key,
    customer_key,
    product_key,
    country_key,
    quantity,
    unit_price,
    line_amount,
    is_cancellation
)
SELECT
    transactions.source_period,
    transactions.source_row,
    transactions.invoice_no,
    transactions.invoice_date,
    TO_CHAR(transactions.invoice_date::DATE, 'YYYYMMDD')::INTEGER,
    COALESCE(customers.customer_key, 0),
    COALESCE(products.product_key, 0),
    COALESCE(countries.country_key, 0),
    transactions.quantity,
    ROUND(transactions.unit_price::NUMERIC, 4),
    ROUND(transactions.line_amount::NUMERIC, 4),
    transactions.is_cancellation
FROM staging.transactions AS transactions
LEFT JOIN analytics.dim_customer AS customers
    ON customers.customer_id = transactions.customer_id
LEFT JOIN analytics.dim_product AS products
    ON products.stock_code = transactions.stock_code
LEFT JOIN analytics.dim_country AS countries
    ON countries.country_name = transactions.country
ORDER BY
    transactions.source_period,
    transactions.source_row;
