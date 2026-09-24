WITH country_metrics AS (
    SELECT
        COALESCE(c.country_name, 'Unknown') AS country_name,
        COALESCE(SUM(f.line_amount), 0) AS net_revenue,
        COALESCE(
            SUM(f.line_amount) FILTER (WHERE NOT f.is_cancellation),
            0
        ) AS non_cancellation_revenue,
        COUNT(DISTINCT f.invoice_no)
            FILTER (WHERE NOT f.is_cancellation) AS sales_orders,
        COUNT(DISTINCT f.customer_key)
            FILTER (
                WHERE f.customer_key <> 0
                AND NOT f.is_cancellation
            ) AS active_customers,
        COUNT(DISTINCT f.invoice_no)
            FILTER (WHERE f.is_cancellation) AS cancellation_invoices
    FROM analytics.fact_sales AS f
    JOIN analytics.dim_country AS c USING (country_key)
    GROUP BY COALESCE(c.country_name, 'Unknown')
)
SELECT
    country_name,
    ROUND(net_revenue, 2) AS net_revenue,
    ROUND(non_cancellation_revenue, 2) AS non_cancellation_revenue,
    sales_orders,
    active_customers,
    cancellation_invoices
FROM country_metrics
ORDER BY net_revenue DESC, country_name;
