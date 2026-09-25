WITH totals AS (
    SELECT
        COUNT(*)::NUMERIC AS total_lines,
        SUM(line_amount) AS total_net_revenue
    FROM analytics.fact_sales
),
unknown_customer AS (
    SELECT
        COUNT(*)::NUMERIC AS unknown_lines,
        SUM(line_amount) AS unknown_net_revenue,
        COUNT(DISTINCT invoice_no)
            FILTER (WHERE NOT is_cancellation) AS unknown_sales_orders
    FROM analytics.fact_sales
    WHERE customer_key = 0
)
SELECT
    unknown_customer.unknown_lines::BIGINT AS unknown_customer_lines,
    ROUND(
        unknown_customer.unknown_lines
        / NULLIF(totals.total_lines, 0),
        4
    ) AS unknown_line_share,
    ROUND(
        COALESCE(unknown_customer.unknown_net_revenue, 0),
        2
    ) AS unknown_net_revenue,
    ROUND(
        COALESCE(unknown_customer.unknown_net_revenue, 0)
        / NULLIF(totals.total_net_revenue, 0),
        4
    ) AS unknown_revenue_share,
    unknown_customer.unknown_sales_orders
FROM unknown_customer
CROSS JOIN totals;
