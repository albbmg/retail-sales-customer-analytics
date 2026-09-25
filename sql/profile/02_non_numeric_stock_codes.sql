SELECT
    p.stock_code,
    p.product_description,
    COUNT(*)::BIGINT AS transaction_lines,
    COUNT(DISTINCT f.invoice_no)::BIGINT AS invoices,
    ROUND(COALESCE(SUM(f.line_amount), 0), 2) AS net_revenue
FROM analytics.fact_sales AS f
JOIN analytics.dim_product AS p USING (product_key)
WHERE p.stock_code IS NOT NULL
  AND p.stock_code !~ '^[0-9]'
GROUP BY p.stock_code, p.product_description
ORDER BY ABS(COALESCE(SUM(f.line_amount), 0)) DESC, p.stock_code
LIMIT 30;
