SELECT
    COUNT(*)::BIGINT AS staging_rows,
    COUNT(DISTINCT invoice_no)::BIGINT AS distinct_invoices,
    MIN(invoice_date) AS first_invoice_timestamp,
    MAX(invoice_date) AS last_invoice_timestamp,
    COUNT(*) FILTER (WHERE customer_id IS NULL)::BIGINT
        AS missing_customer_lines,
    ROUND(
        COUNT(*) FILTER (WHERE customer_id IS NULL)::NUMERIC
        / NULLIF(COUNT(*), 0),
        4
    ) AS missing_customer_line_rate,
    COUNT(*) FILTER (WHERE description IS NULL)::BIGINT
        AS missing_description_lines,
    COUNT(*) FILTER (WHERE country IS NULL)::BIGINT
        AS missing_country_lines,
    COUNT(*) FILTER (WHERE stock_code IS NULL)::BIGINT
        AS missing_stock_code_lines,
    COUNT(*) FILTER (WHERE unit_price = 0)::BIGINT
        AS zero_price_lines,
    COUNT(*) FILTER (WHERE unit_price < 0)::BIGINT
        AS negative_price_lines,
    COUNT(*) FILTER (
        WHERE quantity < 0
          AND NOT is_cancellation
    )::BIGINT AS negative_quantity_non_cancellation_lines,
    COUNT(*) FILTER (WHERE is_cancellation)::BIGINT
        AS cancellation_lines,
    COUNT(DISTINCT invoice_no)
        FILTER (WHERE is_cancellation)::BIGINT
        AS cancellation_invoices,
    COUNT(DISTINCT customer_id)::BIGINT AS identified_customers,
    COUNT(DISTINCT stock_code)::BIGINT AS distinct_stock_codes,
    COUNT(DISTINCT country)::BIGINT AS distinct_countries
FROM staging.transactions;
