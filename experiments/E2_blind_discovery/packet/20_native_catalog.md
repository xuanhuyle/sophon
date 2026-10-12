# Native MetricFlow catalog listings (MetricFlow 0.211.0 via dbt-metricflow 0.13.0, `mf` CLI)

## $ mf list metrics
```
✔ 🌱 We've found 19 metrics.
The list below shows metrics in the format of "metric_name: list of available dimensions"
• active_customers: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• average_order_value: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• average_order_value_live: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• completed_revenue: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• cost: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• discount: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• gross_margin_rate: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• gross_profit: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• gross_profit_live: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• orders: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• orders_live: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• purchasing_customers: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 1 more
• quantity_sold: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• repeat_customer_rate: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 1 more
• repeat_customers: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 1 more
• return_rate: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• returned_orders: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• revenue: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more
• revenue_live: customer__city, customer__country, customer__is_repeat_customer, customer__last_order_date, customer__signup_date and 8 more

```
## $ mf list dimensions --metrics active_customers
```
✔ 🌱 We've found 13 common dimensions for metrics ['active_customers'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales__channel
• sales__order_date
• sales__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics active_customers
```
✔ 🌱 We've found 5 common entities for metrics ['active_customers'].
• customer
• order
• product
• sales
• store

```
## $ mf list dimensions --metrics average_order_value
```
✔ 🌱 We've found 13 common dimensions for metrics ['average_order_value'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales__channel
• sales__order_date
• sales__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics average_order_value
```
✔ 🌱 We've found 5 common entities for metrics ['average_order_value'].
• customer
• order
• product
• sales
• store

```
## $ mf list dimensions --metrics average_order_value_live
```
✔ 🌱 We've found 13 common dimensions for metrics ['average_order_value_live'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales_live__channel
• sales_live__event_ts
• sales_live__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics average_order_value_live
```
✔ 🌱 We've found 5 common entities for metrics ['average_order_value_live'].
• customer
• order
• product
• sales_live
• store

```
## $ mf list dimensions --metrics completed_revenue
```
✔ 🌱 We've found 13 common dimensions for metrics ['completed_revenue'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales__channel
• sales__order_date
• sales__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics completed_revenue
```
✔ 🌱 We've found 5 common entities for metrics ['completed_revenue'].
• customer
• order
• product
• sales
• store

```
## $ mf list dimensions --metrics cost
```
✔ 🌱 We've found 13 common dimensions for metrics ['cost'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales__channel
• sales__order_date
• sales__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics cost
```
✔ 🌱 We've found 5 common entities for metrics ['cost'].
• customer
• order
• product
• sales
• store

```
## $ mf list dimensions --metrics discount
```
✔ 🌱 We've found 13 common dimensions for metrics ['discount'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales__channel
• sales__order_date
• sales__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics discount
```
✔ 🌱 We've found 5 common entities for metrics ['discount'].
• customer
• order
• product
• sales
• store

```
## $ mf list dimensions --metrics gross_margin_rate
```
✔ 🌱 We've found 13 common dimensions for metrics ['gross_margin_rate'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales__channel
• sales__order_date
• sales__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics gross_margin_rate
```
✔ 🌱 We've found 5 common entities for metrics ['gross_margin_rate'].
• customer
• order
• product
• sales
• store

```
## $ mf list dimensions --metrics gross_profit
```
✔ 🌱 We've found 13 common dimensions for metrics ['gross_profit'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales__channel
• sales__order_date
• sales__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics gross_profit
```
✔ 🌱 We've found 5 common entities for metrics ['gross_profit'].
• customer
• order
• product
• sales
• store

```
## $ mf list dimensions --metrics gross_profit_live
```
✔ 🌱 We've found 13 common dimensions for metrics ['gross_profit_live'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales_live__channel
• sales_live__event_ts
• sales_live__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics gross_profit_live
```
✔ 🌱 We've found 5 common entities for metrics ['gross_profit_live'].
• customer
• order
• product
• sales_live
• store

```
## $ mf list dimensions --metrics orders
```
✔ 🌱 We've found 13 common dimensions for metrics ['orders'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales__channel
• sales__order_date
• sales__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics orders
```
✔ 🌱 We've found 5 common entities for metrics ['orders'].
• customer
• order
• product
• sales
• store

```
## $ mf list dimensions --metrics orders_live
```
✔ 🌱 We've found 13 common dimensions for metrics ['orders_live'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales_live__channel
• sales_live__event_ts
• sales_live__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics orders_live
```
✔ 🌱 We've found 5 common entities for metrics ['orders_live'].
• customer
• order
• product
• sales_live
• store

```
## $ mf list dimensions --metrics purchasing_customers
```
✔ 🌱 We've found 6 common dimensions for metrics ['purchasing_customers'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time

```
## $ mf list entities --metrics purchasing_customers
```
✔ 🌱 We've found 1 common entities for metrics ['purchasing_customers'].
• customer

```
## $ mf list dimensions --metrics quantity_sold
```
✔ 🌱 We've found 13 common dimensions for metrics ['quantity_sold'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales__channel
• sales__order_date
• sales__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics quantity_sold
```
✔ 🌱 We've found 5 common entities for metrics ['quantity_sold'].
• customer
• order
• product
• sales
• store

```
## $ mf list dimensions --metrics repeat_customer_rate
```
✔ 🌱 We've found 6 common dimensions for metrics ['repeat_customer_rate'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time

```
## $ mf list entities --metrics repeat_customer_rate
```
✔ 🌱 We've found 1 common entities for metrics ['repeat_customer_rate'].
• customer

```
## $ mf list dimensions --metrics repeat_customers
```
✔ 🌱 We've found 6 common dimensions for metrics ['repeat_customers'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time

```
## $ mf list entities --metrics repeat_customers
```
✔ 🌱 We've found 1 common entities for metrics ['repeat_customers'].
• customer

```
## $ mf list dimensions --metrics return_rate
```
✔ 🌱 We've found 13 common dimensions for metrics ['return_rate'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales__channel
• sales__order_date
• sales__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics return_rate
```
✔ 🌱 We've found 5 common entities for metrics ['return_rate'].
• customer
• order
• product
• sales
• store

```
## $ mf list dimensions --metrics returned_orders
```
✔ 🌱 We've found 13 common dimensions for metrics ['returned_orders'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales__channel
• sales__order_date
• sales__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics returned_orders
```
✔ 🌱 We've found 5 common entities for metrics ['returned_orders'].
• customer
• order
• product
• sales
• store

```
## $ mf list dimensions --metrics revenue
```
✔ 🌱 We've found 13 common dimensions for metrics ['revenue'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales__channel
• sales__order_date
• sales__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics revenue
```
✔ 🌱 We've found 5 common entities for metrics ['revenue'].
• customer
• order
• product
• sales
• store

```
## $ mf list dimensions --metrics revenue_live
```
✔ 🌱 We've found 13 common dimensions for metrics ['revenue_live'].
• customer__city
• customer__country
• customer__is_repeat_customer
• customer__last_order_date
• customer__signup_date
• metric_time
• product__category
• product__product_name
• sales_live__channel
• sales_live__event_ts
• sales_live__status
• store__store_city
• store__store_country

```
## $ mf list entities --metrics revenue_live
```
✔ 🌱 We've found 5 common entities for metrics ['revenue_live'].
• customer
• order
• product
• sales_live
• store

```
