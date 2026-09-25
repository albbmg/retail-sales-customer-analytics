WITH checks AS (
    SELECT
        'staging_fact_row_count'::TEXT AS check_name,
        ABS(
            (SELECT COUNT(*) FROM staging.transactions)
            - (SELECT COUNT(*) FROM analytics.fact_sales)
        )::BIGINT AS failed_rows

    UNION ALL

    SELECT
        'source_lineage_one_to_one',
        COUNT(*)::BIGINT
    FROM staging.transactions AS s
    FULL OUTER JOIN analytics.fact_sales AS f
        USING (source_period, source_row)
    WHERE s.source_row IS NULL OR f.source_row IS NULL

    UNION ALL

    SELECT
        'fact_dimension_orphans',
        COUNT(*)::BIGINT
    FROM analytics.fact_sales AS f
    LEFT JOIN analytics.dim_date AS d USING (date_key)
    LEFT JOIN analytics.dim_customer AS c USING (customer_key)
    LEFT JOIN analytics.dim_product AS p USING (product_key)
    LEFT JOIN analytics.dim_country AS co USING (country_key)
    WHERE
        d.date_key IS NULL
        OR c.customer_key IS NULL
        OR p.product_key IS NULL
        OR co.country_key IS NULL

    UNION ALL

    SELECT
        'unknown_customer_mapping',
        COUNT(*)::BIGINT
    FROM staging.transactions AS s
    JOIN analytics.fact_sales AS f
        USING (source_period, source_row)
    WHERE
        (s.customer_id IS NULL AND f.customer_key <> 0)
        OR (s.customer_id IS NOT NULL AND f.customer_key = 0)

    UNION ALL

    SELECT
        'unknown_product_mapping',
        COUNT(*)::BIGINT
    FROM staging.transactions AS s
    JOIN analytics.fact_sales AS f
        USING (source_period, source_row)
    WHERE
        (s.stock_code IS NULL AND f.product_key <> 0)
        OR (s.stock_code IS NOT NULL AND f.product_key = 0)

    UNION ALL

    SELECT
        'unknown_country_mapping',
        COUNT(*)::BIGINT
    FROM staging.transactions AS s
    JOIN analytics.fact_sales AS f
        USING (source_period, source_row)
    WHERE
        (s.country IS NULL AND f.country_key <> 0)
        OR (s.country IS NOT NULL AND f.country_key = 0)

    UNION ALL

    SELECT
        'cancellation_flag_consistency',
        COUNT(*)::BIGINT
    FROM staging.transactions AS s
    JOIN analytics.fact_sales AS f
        USING (source_period, source_row)
    WHERE f.is_cancellation IS DISTINCT FROM s.is_cancellation

    UNION ALL

    SELECT
        'date_key_consistency',
        COUNT(*)::BIGINT
    FROM staging.transactions AS s
    JOIN analytics.fact_sales AS f
        USING (source_period, source_row)
    WHERE f.date_key IS DISTINCT FROM
        TO_CHAR(s.invoice_date::DATE, 'YYYYMMDD')::INTEGER

    UNION ALL

    SELECT
        'unit_price_consistency',
        COUNT(*)::BIGINT
    FROM staging.transactions AS s
    JOIN analytics.fact_sales AS f
        USING (source_period, source_row)
    WHERE f.unit_price IS DISTINCT FROM ROUND(s.unit_price::NUMERIC, 4)

    UNION ALL

    SELECT
        'line_amount_consistency',
        COUNT(*)::BIGINT
    FROM staging.transactions AS s
    JOIN analytics.fact_sales AS f
        USING (source_period, source_row)
    WHERE f.line_amount IS DISTINCT FROM ROUND(s.line_amount::NUMERIC, 4)

    UNION ALL

    SELECT
        'product_type_classification_consistency',
        COUNT(*)::BIGINT
    FROM analytics.dim_product AS p
    WHERE
        p.stock_code IS NOT NULL
        AND p.product_type IS DISTINCT FROM
            CASE
                WHEN p.stock_code IN ('DOT', 'POST', 'C2') THEN 'shipping'
                WHEN p.stock_code IN (
                    'AMAZONFEE',
                    'BANK CHARGES',
                    'CRUK'
                ) THEN 'fee'
                WHEN p.stock_code IN (
                    'B',
                    'M',
                    'ADJUST',
                    'ADJUST2'
                ) THEN 'adjustment'
                WHEN p.stock_code = 'D' THEN 'discount'
                WHEN p.stock_code = 'S' THEN 'sample'
                WHEN p.stock_code ~* '^gift_' THEN 'voucher'
                WHEN p.stock_code ~* '^TEST' THEN 'test'
                ELSE 'merchandise'
            END

    UNION ALL

    SELECT
        'customer_business_key_uniqueness',
        COUNT(*)::BIGINT
    FROM (
        SELECT customer_id
        FROM analytics.dim_customer
        WHERE customer_id IS NOT NULL
        GROUP BY customer_id
        HAVING COUNT(*) > 1
    ) AS duplicates

    UNION ALL

    SELECT
        'product_business_key_uniqueness',
        COUNT(*)::BIGINT
    FROM (
        SELECT stock_code
        FROM analytics.dim_product
        WHERE stock_code IS NOT NULL
        GROUP BY stock_code
        HAVING COUNT(*) > 1
    ) AS duplicates

    UNION ALL

    SELECT
        'country_business_key_uniqueness',
        COUNT(*)::BIGINT
    FROM (
        SELECT country_name
        FROM analytics.dim_country
        WHERE country_name IS NOT NULL
        GROUP BY country_name
        HAVING COUNT(*) > 1
    ) AS duplicates
)
SELECT
    check_name,
    failed_rows
FROM checks
ORDER BY check_name;
