-- stack BASELINE__BOUNDARY120__q747ba25c
-- query {"group_by": ["metric_time__year"], "metric": "french_market_revenue", "where": []}
-- semantic manifest 3532b0e66f9758055ec4e8fc2085e15226c87adecdd6c72ab2554afb4c7515bf
SELECT
  metric_time__year
  , SUM(french_market_revenue) AS french_market_revenue
FROM (
  SELECT
    DATE_TRUNC('year', sales_src_10000.order_date) AS metric_time__year
    , sales_src_10000.status AS sales__status
    , customers_src_10000.country AS customer__country
    , sales_src_10000.revenue AS french_market_revenue
  FROM "warehouse"."gold"."fact_sales" sales_src_10000
  LEFT OUTER JOIN
    "warehouse"."gold"."dim_customers" customers_src_10000
  ON
    sales_src_10000.customer_id = customers_src_10000.customer_id
) subq_5
WHERE sales__status = 'completed' AND customer__country = 'France'
GROUP BY
  metric_time__year
