SELECT
  metric_time__year
  , SUM(completed_revenue) AS completed_revenue
FROM (
  SELECT
    DATE_TRUNC('year', order_date) AS metric_time__year
    , status AS sales__status
    , revenue AS completed_revenue
  FROM "warehouse"."gold"."fact_sales" sales_src_10000
) subq_2
WHERE sales__status = 'completed'
GROUP BY
  metric_time__year
ORDER BY metric_time__year
