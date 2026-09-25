WITH active_keys AS (
    SELECT DISTINCT customer_key
    FROM analytics.fact_sales
    WHERE customer_key <> 0
      AND NOT is_cancellation
),
customer_revenue AS (
    SELECT
        f.customer_key,
        SUM(f.line_amount) AS net_revenue
    FROM analytics.fact_sales AS f
    JOIN active_keys USING (customer_key)
    GROUP BY f.customer_key
),
ranked AS (
    SELECT
        customer_key,
        net_revenue,
        ROW_NUMBER() OVER (
            ORDER BY net_revenue DESC, customer_key
        ) AS revenue_rank
    FROM customer_revenue
),
totals AS (
    SELECT SUM(net_revenue) AS total_net_revenue
    FROM customer_revenue
)
SELECT
    ROUND(totals.total_net_revenue, 2) AS active_customer_net_revenue,
    ROUND(
        SUM(ranked.net_revenue)
            FILTER (WHERE ranked.revenue_rank = 1),
        2
    ) AS top_1_net_revenue,
    ROUND(
        SUM(ranked.net_revenue)
            FILTER (WHERE ranked.revenue_rank <= 10),
        2
    ) AS top_10_net_revenue,
    ROUND(
        SUM(ranked.net_revenue)
            FILTER (WHERE ranked.revenue_rank <= 100),
        2
    ) AS top_100_net_revenue,
    ROUND(
        SUM(ranked.net_revenue)
            FILTER (WHERE ranked.revenue_rank = 1)
        / NULLIF(totals.total_net_revenue, 0),
        4
    ) AS top_1_share,
    ROUND(
        SUM(ranked.net_revenue)
            FILTER (WHERE ranked.revenue_rank <= 10)
        / NULLIF(totals.total_net_revenue, 0),
        4
    ) AS top_10_share,
    ROUND(
        SUM(ranked.net_revenue)
            FILTER (WHERE ranked.revenue_rank <= 100)
        / NULLIF(totals.total_net_revenue, 0),
        4
    ) AS top_100_share
FROM ranked
CROSS JOIN totals
GROUP BY totals.total_net_revenue;
