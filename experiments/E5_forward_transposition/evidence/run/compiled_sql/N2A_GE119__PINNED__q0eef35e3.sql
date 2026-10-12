-- stack N2A_GE119__PINNED__q0eef35e3
-- query {"group_by": ["metric_time__year"], "metric": "premium_completed_revenue", "where": ["{{ TimeDimension('metric_time', 'day') }} >= '2025-01-01'"]}
-- semantic manifest 212df5a65771bcebbf12f5818f213cf6d805197f93e355a7809e93b2e09057e4
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
  sales__status = 'completed' AND sales__unit_price >= 119
) AND (
  metric_time__day >= '2025-01-01'
)
GROUP BY
  metric_time__year
