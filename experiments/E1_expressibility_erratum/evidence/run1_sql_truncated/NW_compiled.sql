SELECT
    DATE_TRUNC('year', order_date) AS metric_time__year
    , sales_id AS sales
    , status AS sales__status
    , revenue AS __revenue
    , quantity AS __quantity_sold
  FROM "warehouse"."gold"."fact_sales" sales_src_10000
)

SELECT
  metric_time__year AS metric_time__year
  , SUM(revenue) AS revenue
FROM (
  SELECT
    subq_9.metric_time__year AS metric_time__year
    , subq_9.sales__status AS sales__status
    , subq_15.sales__revenue AS sales__revenue
    , subq_21.sales__quantity_sold AS sales__quantity_sold
    , subq_9.__revenue AS revenue
  FROM (
    SELECT
      metric_time__year
      , sales
      , sales__status
      , __revenue
    FROM sma_10002_cte
  ) subq_9
  LEFT OUTER JOIN (
    SELECT
      sales
      , SUM(__revenue) AS sales__revenue
    FROM sma_10002_cte
    GROUP BY
      sales
  ) subq_15
  ON
    subq_9.sales = subq_15.sales
  LEFT OUTER JOIN (
    SELECT
      sales
      , SUM(__quantity_sold) AS sales__quantity_sold
    FROM sma_10002_cte
    GROUP BY
      sales
  ) subq_21
  ON
    subq_9.sales = subq_21.sales
) subq_23
WHERE sales__revenue >= 100 * sales__quantity_sold AND sales__status = 'completed'
GROUP BY
  metric_time__year
