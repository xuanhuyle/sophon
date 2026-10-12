-- stack GENERATED__BOUNDARY120__q0eef35e3
-- query {"group_by": ["metric_time__year"], "metric": "premium_completed_revenue", "where": ["{{ TimeDimension('metric_time', 'day') }} >= '2025-01-01'"]}
-- semantic manifest fd26cecdbb44ff2e0e8807db1ce0af4836a0b412c8ad29646aecbaddcf6ce265
SELECT
  metric_time__year
  , SUM(premium_completed_revenue) AS premium_completed_revenue
FROM (
  SELECT
    DATE_TRUNC('day', order_date) AS metric_time__day
    , DATE_TRUNC('year', order_date) AS metric_time__year
    , status AS sales__status
    , unit_price AS sales__unit_price
    , revenue AS premium_completed_revenue
  FROM "warehouse"."gold"."fact_sales" sales_src_10000
) subq_2
WHERE (
  sales__status = 'completed' AND sales__unit_price >= 120
) AND (
  metric_time__day >= '2025-01-01'
)
GROUP BY
  metric_time__year
