SELECT
  metric_time__year
  , SUM(french_market_revenue) AS french_market_revenue
FROM (
  SELECT
    DATE_TRUNC('year', sales_src_10000.order_date) AS metric_time__year
    , sales_src_10000.status AS sales__status
    , stores_src_10000.country AS store__store_country
    , sales_src_10000.revenue AS french_market_revenue
  FROM "warehouse"."gold"."fact_sales" sales_src_10000
  LEFT OUTER JOIN
    "warehouse"."gold"."dim_stores" stores_src_10000
  ON
    sales_src_10000.store_id = stores_src_10000.store_id
) subq_5
WHERE sales__status = 'completed' AND store__store_country = 'France'
GROUP BY
  metric_time__year
