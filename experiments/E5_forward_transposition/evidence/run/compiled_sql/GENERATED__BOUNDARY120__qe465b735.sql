-- stack GENERATED__BOUNDARY120__qe465b735
-- query {"group_by": ["metric_time__year"], "metric": "premium_completed_revenue", "where": []}
-- semantic manifest fd26cecdbb44ff2e0e8807db1ce0af4836a0b412c8ad29646aecbaddcf6ce265
SELECT
  metric_time__year
  , SUM(premium_completed_revenue) AS premium_completed_revenue
FROM (
  SELECT
    DATE_TRUNC('year', order_date) AS metric_time__year
    , status AS sales__status
    , unit_price AS sales__unit_price
    , revenue AS premium_completed_revenue
  FROM "warehouse"."gold"."fact_sales" sales_src_10000
) subq_2
WHERE sales__status = 'completed' AND sales__unit_price >= 120
GROUP BY
  metric_time__year
