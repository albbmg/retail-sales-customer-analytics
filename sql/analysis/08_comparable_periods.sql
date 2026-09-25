WITH periods(label, start_date, end_date) AS (
    VALUES
        ('2010 Jan-Nov', DATE '2010-01-01', DATE '2010-12-01'),
        ('2011 Jan-Nov', DATE '2011-01-01', DATE '2011-12-01')
)
SELECT
    periods.label,
    ROUND(COALESCE(SUM(f.line_amount), 0), 2) AS net_revenue,
    ROUND(
        COALESCE(
            SUM(f.line_amount) FILTER (WHERE NOT f.is_cancellation),
            0
        ),
        2
    ) AS non_cancellation_revenue,
    COUNT(DISTINCT f.invoice_no)
        FILTER (WHERE NOT f.is_cancellation) AS sales_orders,
    COALESCE(
        SUM(f.quantity)
            FILTER (
                WHERE NOT f.is_cancellation
                AND f.quantity > 0
            ),
        0
    ) AS units_sold,
    COUNT(DISTINCT f.customer_key)
        FILTER (
            WHERE f.customer_key <> 0
            AND NOT f.is_cancellation
        ) AS active_customers,
    ROUND(
        COALESCE(
            SUM(f.line_amount) FILTER (WHERE NOT f.is_cancellation),
            0
        )
        / NULLIF(
            COUNT(DISTINCT f.invoice_no)
                FILTER (WHERE NOT f.is_cancellation),
            0
        ),
        2
    ) AS average_order_value,
    ROUND(
        COUNT(DISTINCT f.invoice_no)
            FILTER (WHERE f.is_cancellation)::NUMERIC
        / NULLIF(COUNT(DISTINCT f.invoice_no), 0),
        4
    ) AS cancellation_invoice_rate
FROM periods
LEFT JOIN analytics.fact_sales AS f
    ON f.invoice_timestamp >= periods.start_date
   AND f.invoice_timestamp < periods.end_date
GROUP BY periods.label, periods.start_date
ORDER BY periods.start_date;
