SELECT
    DATE_TRUNC('month', d.full_date)::DATE AS month_start,
    COUNT(DISTINCT f.invoice_no)
        FILTER (WHERE f.is_cancellation) AS cancellation_invoices,
    COUNT(*) FILTER (WHERE f.is_cancellation) AS cancellation_lines,
    ROUND(
        ABS(
            COALESCE(
                SUM(f.line_amount) FILTER (WHERE f.is_cancellation),
                0
            )
        ),
        2
    ) AS cancellation_value,
    ABS(
        COALESCE(
            SUM(f.quantity) FILTER (WHERE f.is_cancellation),
            0
        )
    ) AS cancellation_units
FROM analytics.fact_sales AS f
JOIN analytics.dim_date AS d USING (date_key)
GROUP BY 1
HAVING COUNT(*) FILTER (WHERE f.is_cancellation) > 0
ORDER BY month_start;
