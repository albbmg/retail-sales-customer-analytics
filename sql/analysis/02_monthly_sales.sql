WITH monthly AS (
    SELECT
        DATE_TRUNC('month', d.full_date)::DATE AS month_start,
        COALESCE(SUM(f.line_amount), 0) AS net_revenue,
        COALESCE(
            SUM(f.line_amount) FILTER (WHERE NOT f.is_cancellation),
            0
        ) AS non_cancellation_revenue,
        COUNT(DISTINCT f.invoice_no)
            FILTER (WHERE NOT f.is_cancellation) AS sales_orders,
        COUNT(DISTINCT f.invoice_no)
            FILTER (WHERE f.is_cancellation) AS cancellation_invoices,
        COUNT(DISTINCT f.invoice_no) AS total_invoices,
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
            ) AS active_customers
    FROM analytics.fact_sales AS f
    JOIN analytics.dim_date AS d USING (date_key)
    GROUP BY 1
)
SELECT
    month_start,
    ROUND(net_revenue, 2) AS net_revenue,
    ROUND(non_cancellation_revenue, 2) AS non_cancellation_revenue,
    sales_orders,
    units_sold,
    active_customers,
    ROUND(
        non_cancellation_revenue / NULLIF(sales_orders, 0),
        2
    ) AS average_order_value,
    cancellation_invoices,
    ROUND(
        cancellation_invoices::NUMERIC
        / NULLIF(total_invoices, 0),
        4
    ) AS cancellation_invoice_rate
FROM monthly
ORDER BY month_start;
