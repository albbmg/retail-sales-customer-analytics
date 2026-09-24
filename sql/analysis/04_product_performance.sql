WITH product_metrics AS (
    SELECT
        p.stock_code,
        p.product_description,
        COALESCE(SUM(f.line_amount), 0) AS net_revenue,
        COALESCE(
            SUM(f.line_amount) FILTER (WHERE NOT f.is_cancellation),
            0
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
        ABS(
            COALESCE(
                SUM(f.line_amount) FILTER (WHERE f.is_cancellation),
                0
            )
        ) AS cancellation_value
    FROM analytics.fact_sales AS f
    JOIN analytics.dim_product AS p USING (product_key)
    WHERE f.product_key <> 0
    GROUP BY p.stock_code, p.product_description
)
SELECT
    stock_code,
    product_description,
    ROUND(net_revenue, 2) AS net_revenue,
    sales_orders,
    units_sold,
    ROUND(cancellation_value, 2) AS cancellation_value
FROM product_metrics
ORDER BY net_revenue DESC, stock_code;
