WITH aggregates AS (
    SELECT
        COALESCE(SUM(line_amount), 0) AS net_revenue,
        COALESCE(
            SUM(line_amount) FILTER (WHERE NOT is_cancellation),
            0
        ) AS non_cancellation_revenue,
        COUNT(DISTINCT invoice_no)
            FILTER (WHERE NOT is_cancellation) AS sales_orders,
        COALESCE(
            SUM(quantity)
                FILTER (WHERE NOT is_cancellation AND quantity > 0),
            0
        ) AS units_sold,
        COUNT(DISTINCT customer_key)
            FILTER (
                WHERE customer_key <> 0
                AND NOT is_cancellation
            ) AS active_customers,
        COUNT(DISTINCT invoice_no)
            FILTER (WHERE is_cancellation) AS cancellation_invoices,
        COUNT(DISTINCT invoice_no) AS total_invoices
    FROM analytics.fact_sales
),
active_customer_revenue AS (
    SELECT
        COALESCE(SUM(line_amount), 0) AS net_revenue
    FROM analytics.fact_sales
    WHERE customer_key IN (
        SELECT DISTINCT customer_key
        FROM analytics.fact_sales
        WHERE customer_key <> 0
          AND NOT is_cancellation
    )
)
SELECT
    ROUND(aggregates.net_revenue, 2) AS net_revenue,
    ROUND(
        aggregates.non_cancellation_revenue,
        2
    ) AS non_cancellation_revenue,
    aggregates.sales_orders,
    aggregates.units_sold,
    ROUND(
        aggregates.non_cancellation_revenue
        / NULLIF(aggregates.sales_orders, 0),
        2
    ) AS average_order_value,
    aggregates.active_customers,
    ROUND(
        active_customer_revenue.net_revenue
        / NULLIF(aggregates.active_customers, 0),
        2
    ) AS net_revenue_per_active_customer,
    ROUND(
        aggregates.cancellation_invoices::NUMERIC
        / NULLIF(aggregates.total_invoices, 0),
        4
    ) AS cancellation_invoice_rate
FROM aggregates
CROSS JOIN active_customer_revenue;
