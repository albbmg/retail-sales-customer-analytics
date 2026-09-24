WITH customer_metrics AS (
    SELECT
        c.customer_id,
        c.customer_label,
        MIN(f.invoice_timestamp::DATE)
            FILTER (WHERE NOT f.is_cancellation) AS first_purchase_date,
        MAX(f.invoice_timestamp::DATE)
            FILTER (WHERE NOT f.is_cancellation) AS last_purchase_date,
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
        COUNT(DISTINCT f.invoice_no)
            FILTER (WHERE f.is_cancellation) AS cancellation_invoices
    FROM analytics.fact_sales AS f
    JOIN analytics.dim_customer AS c USING (customer_key)
    WHERE f.customer_key <> 0
    GROUP BY c.customer_id, c.customer_label
)
SELECT
    customer_id,
    customer_label,
    first_purchase_date,
    last_purchase_date,
    ROUND(net_revenue, 2) AS net_revenue,
    sales_orders,
    units_sold,
    ROUND(
        non_cancellation_revenue / NULLIF(sales_orders, 0),
        2
    ) AS average_order_value,
    cancellation_invoices
FROM customer_metrics
ORDER BY net_revenue DESC, customer_id;
