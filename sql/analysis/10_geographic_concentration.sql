WITH country_revenue AS (
    SELECT
        COALESCE(c.country_name, 'Unknown') AS country_name,
        SUM(f.line_amount) AS net_revenue
    FROM analytics.fact_sales AS f
    JOIN analytics.dim_country AS c USING (country_key)
    GROUP BY COALESCE(c.country_name, 'Unknown')
),
ranked AS (
    SELECT
        country_name,
        net_revenue,
        ROW_NUMBER() OVER (
            ORDER BY net_revenue DESC, country_name
        ) AS revenue_rank
    FROM country_revenue
),
totals AS (
    SELECT SUM(net_revenue) AS total_net_revenue
    FROM country_revenue
)
SELECT
    ROUND(totals.total_net_revenue, 2) AS total_net_revenue,
    ROUND(
        SUM(ranked.net_revenue)
            FILTER (WHERE ranked.country_name = 'United Kingdom'),
        2
    ) AS uk_net_revenue,
    ROUND(
        SUM(ranked.net_revenue)
            FILTER (WHERE ranked.country_name = 'United Kingdom')
        / NULLIF(totals.total_net_revenue, 0),
        4
    ) AS uk_share,
    ROUND(
        SUM(ranked.net_revenue)
            FILTER (WHERE ranked.revenue_rank <= 5)
        / NULLIF(totals.total_net_revenue, 0),
        4
    ) AS top_5_country_share
FROM ranked
CROSS JOIN totals
GROUP BY totals.total_net_revenue;
