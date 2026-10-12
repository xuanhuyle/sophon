-- stack BASELINE__PINNED__qe465b735
-- query {"group_by": ["metric_time__year"], "metric": "premium_completed_revenue", "where": []}
-- semantic manifest 3532b0e66f9758055ec4e8fc2085e15226c87adecdd6c72ab2554afb4c7515bf
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
WHERE sales__status = 'completed' AND sales__unit_price >= 100
GROUP BY
  metric_time__year
