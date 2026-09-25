SELECT
    p.product_type,
    p.stock_code,
    p.product_description,
    COUNT(*)::BIGINT AS transaction_lines,
    COUNT(DISTINCT f.invoice_no)::BIGINT AS invoices,
    ROUND(COALESCE(SUM(f.line_amount), 0), 2) AS net_revenue,
    ROUND(
        ABS(
            COALESCE(
                SUM(f.line_amount) FILTER (WHERE f.is_cancellation),
                0
            )
        ),
        2
    ) AS cancellation_value
FROM analytics.fact_sales AS f
JOIN analytics.dim_product AS p USING (product_key)
WHERE p.product_type NOT IN ('merchandise', 'unknown')
GROUP BY
    p.product_type,
    p.stock_code,
    p.product_description
ORDER BY
    ABS(COALESCE(SUM(f.line_amount), 0)) DESC,
    p.stock_code;
