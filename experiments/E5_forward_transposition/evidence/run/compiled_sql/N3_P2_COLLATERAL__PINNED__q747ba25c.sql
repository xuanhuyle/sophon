-- stack N3_P2_COLLATERAL__PINNED__q747ba25c
-- query {"group_by": ["metric_time__year"], "metric": "french_market_revenue", "where": []}
-- semantic manifest 2173bf6084282618809389dbddb73b994b858a04f970ca41c49869ed97073957
SELECT
  metric_time__year
  , SUM(french_market_revenue) AS french_market_revenue
FROM (
  SELECT
    DATE_TRUNC('year', sales_src_10000.order_date) AS metric_time__year
    , sales_src_10000.status AS sales__status
    , sales_src_10000.unit_price AS sales__unit_price
    , customers_src_10000.country AS customer__country
    , sales_src_10000.revenue AS french_market_revenue
  FROM "warehouse"."gold"."fact_sales" sales_src_10000
  LEFT OUTER JOIN
    "warehouse"."gold"."dim_customers" customers_src_10000
  ON
    sales_src_10000.customer_id = customers_src_10000.customer_id
) subq_5
WHERE sales__status = 'completed' AND customer__country = 'France' AND sales__unit_price >= 120
GROUP BY
  metric_time__year
