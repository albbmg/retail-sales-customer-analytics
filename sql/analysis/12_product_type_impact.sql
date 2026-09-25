SELECT
    p.product_type,
    COUNT(*)::BIGINT AS transaction_lines,
    COUNT(DISTINCT f.invoice_no)::BIGINT AS invoices,
    ROUND(COALESCE(SUM(f.line_amount), 0), 2) AS net_revenue,
    ROUND(
        COALESCE(
            SUM(f.line_amount) FILTER (WHERE NOT f.is_cancellation),
            0
        ),
        2
    ) AS non_cancellation_revenue,
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
GROUP BY p.product_type
ORDER BY ABS(COALESCE(SUM(f.line_amount), 0)) DESC, p.product_type;
