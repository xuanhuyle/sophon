# Warehouse schema (DuckDB file built by the upstream pipeline; every relation and column)


## bronze.customers (BASE TABLE)
- customer_id: BIGINT
- first_name: VARCHAR
- last_name: VARCHAR
- email: VARCHAR
- country: VARCHAR
- city: VARCHAR
- signup_date: VARCHAR

## bronze.order_events (BASE TABLE)
- event_id: VARCHAR
- order_id: BIGINT
- order_item_id: BIGINT
- customer_id: BIGINT
- store_id: BIGINT
- product_id: BIGINT
- quantity: INTEGER
- unit_price: DECIMAL(10,2)
- channel: VARCHAR
- status: VARCHAR
- event_ts: TIMESTAMP

## bronze.order_items (BASE TABLE)
- order_item_id: BIGINT
- order_id: BIGINT
- product_id: BIGINT
- quantity: BIGINT
- unit_price: DOUBLE

## bronze.orders (BASE TABLE)
- order_id: BIGINT
- customer_id: BIGINT
- store_id: BIGINT
- order_date: VARCHAR
- channel: VARCHAR
- status: VARCHAR

## bronze.products (BASE TABLE)
- product_id: BIGINT
- product_name: VARCHAR
- category: VARCHAR
- unit_cost: DOUBLE
- list_price: DOUBLE

## bronze.stores (BASE TABLE)
- store_id: BIGINT
- store_name: VARCHAR
- country: VARCHAR
- city: VARCHAR

## gold.dim_customers (BASE TABLE)
- customer_id: BIGINT
- first_name: VARCHAR
- last_name: VARCHAR
- full_name: VARCHAR
- email: VARCHAR
- country: VARCHAR
- city: VARCHAR
- signup_date: DATE

## gold.dim_dates (BASE TABLE)
- date_id: INTEGER
- date_day: DATE
- year: BIGINT
- quarter: BIGINT
- quarter_name: VARCHAR
- month: BIGINT
- month_name: VARCHAR
- week_of_year: BIGINT
- day_of_week: BIGINT
- day_name: VARCHAR
- is_weekend: BOOLEAN

## gold.dim_products (BASE TABLE)
- product_id: BIGINT
- product_name: VARCHAR
- category: VARCHAR
- unit_cost: DECIMAL(10,2)
- list_price: DECIMAL(10,2)
- unit_margin: DECIMAL(10,2)
- margin_rate: DOUBLE

## gold.dim_stores (BASE TABLE)
- store_id: BIGINT
- store_name: VARCHAR
- country: VARCHAR
- city: VARCHAR

## gold.fact_customer_orders (BASE TABLE)
- customer_id: BIGINT
- order_count: BIGINT
- is_repeat_customer: BOOLEAN
- last_order_date: DATE

## gold.fact_sales (BASE TABLE)
- sales_id: BIGINT
- order_id: BIGINT
- customer_id: BIGINT
- product_id: BIGINT
- store_id: BIGINT
- order_date: DATE
- date_id: INTEGER
- channel: VARCHAR
- status: VARCHAR
- quantity: INTEGER
- unit_price: DECIMAL(10,2)
- unit_cost: DECIMAL(10,2)
- revenue: DECIMAL(12,2)
- cost_amount: DECIMAL(12,2)
- profit: DECIMAL(12,2)
- discount_amount: DECIMAL(12,2)
- is_completed: BOOLEAN
- is_returned: BOOLEAN
- is_cancelled: BOOLEAN

## gold.fact_sales_live (BASE TABLE)
- event_id: VARCHAR
- order_id: BIGINT
- order_item_id: BIGINT
- customer_id: BIGINT
- product_id: BIGINT
- store_id: BIGINT
- event_ts: TIMESTAMP
- event_date: DATE
- date_id: INTEGER
- channel: VARCHAR
- status: VARCHAR
- quantity: INTEGER
- unit_price: DECIMAL(10,2)
- unit_cost: DECIMAL(10,2)
- revenue: DECIMAL(12,2)
- cost_amount: DECIMAL(12,2)
- profit: DECIMAL(12,2)
- discount_amount: DECIMAL(12,2)
- is_completed: BOOLEAN
- is_returned: BOOLEAN
- is_cancelled: BOOLEAN

## gold.rt_freshness (VIEW)
- last_event_ts: TIMESTAMP
- as_of: TIMESTAMP WITH TIME ZONE
- freshness_seconds: BIGINT
- no_events_yet: BOOLEAN

## silver.stg_customers (VIEW)
- customer_id: BIGINT
- first_name: VARCHAR
- last_name: VARCHAR
- email: VARCHAR
- country: VARCHAR
- city: VARCHAR
- signup_date: DATE

## silver.stg_order_events (VIEW)
- event_id: VARCHAR
- order_id: BIGINT
- order_item_id: BIGINT
- customer_id: BIGINT
- store_id: BIGINT
- product_id: BIGINT
- quantity: INTEGER
- unit_price: DECIMAL(10,2)
- channel: VARCHAR
- status: VARCHAR
- event_ts: TIMESTAMP

## silver.stg_order_items (VIEW)
- order_item_id: BIGINT
- order_id: BIGINT
- product_id: BIGINT
- quantity: INTEGER
- unit_price: DECIMAL(10,2)

## silver.stg_orders (VIEW)
- order_id: BIGINT
- customer_id: BIGINT
- store_id: BIGINT
- order_date: DATE
- channel: VARCHAR
- status: VARCHAR

## silver.stg_products (VIEW)
- product_id: BIGINT
- product_name: VARCHAR
- category: VARCHAR
- unit_cost: DECIMAL(10,2)
- list_price: DECIMAL(10,2)
- unit_margin: DECIMAL(10,2)

## silver.stg_stores (VIEW)
- store_id: BIGINT
- store_name: VARCHAR
- country: VARCHAR
- city: VARCHAR

# Observed values of every VARCHAR or BOOLEAN column with at most 12 distinct values (row counts)

- bronze.orders.channel: 'in_store'=872, 'online'=1328
- bronze.orders.status: 'cancelled'=183, 'completed'=1801, 'returned'=216
- bronze.products.category: 'Clothing'=28, 'Electronics'=22, 'Home'=21, 'Sports'=29
- bronze.stores.store_name: 'Store Chrétien'=1, 'Store Devaux'=1, 'Store Gauthier-sur-Evrard'=1, 'Store Gomes'=1, 'Store Hoareaudan'=1, 'Store Labbéboeuf'=1, 'Store Ollivier-sur-Dupuy'=1, 'Store Perez'=1, 'Store Ribeiro'=1, 'Store Thibault'=1
- bronze.stores.country: 'Belgium'=2, 'France'=2, 'Germany'=2, 'Italy'=2, 'Spain'=2
- bronze.stores.city: 'Descamps-sur-David'=1, 'Duhamel'=1, 'Faivre-les-Bains'=1, 'Garnier-la-Forêt'=1, 'Gayboeuf'=1, 'Saint Jacqueline'=1, 'Saint Marcel'=1, 'Saint Marianne'=1, 'Saint Martine'=1, 'Saint Éricnec'=1
- gold.dim_customers.country: 'Belgium'=99, 'France'=90, 'Germany'=105, 'Italy'=108, 'Spain'=98
- gold.dim_dates.quarter_name: 'Q1'=271, 'Q2'=273, 'Q3'=276, 'Q4'=276
- gold.dim_dates.month_name: 'April'=90, 'August'=93, 'December'=93, 'February'=85, 'January'=93, 'July'=93, 'June'=90, 'March'=93, 'May'=93, 'November'=90, 'October'=93, 'September'=90
- gold.dim_dates.day_name: 'Friday'=156, 'Monday'=157, 'Saturday'=156, 'Sunday'=156, 'Thursday'=157, 'Tuesday'=157, 'Wednesday'=157
- gold.dim_dates.is_weekend: False=784, True=312
- gold.dim_products.category: 'Clothing'=28, 'Electronics'=22, 'Home'=21, 'Sports'=29
- gold.dim_stores.store_name: 'Store Chrétien'=1, 'Store Devaux'=1, 'Store Gauthier-sur-Evrard'=1, 'Store Gomes'=1, 'Store Hoareaudan'=1, 'Store Labbéboeuf'=1, 'Store Ollivier-sur-Dupuy'=1, 'Store Perez'=1, 'Store Ribeiro'=1, 'Store Thibault'=1
- gold.dim_stores.country: 'Belgium'=2, 'France'=2, 'Germany'=2, 'Italy'=2, 'Spain'=2
- gold.dim_stores.city: 'Descamps-sur-David'=1, 'Duhamel'=1, 'Faivre-les-Bains'=1, 'Garnier-la-Forêt'=1, 'Gayboeuf'=1, 'Saint Jacqueline'=1, 'Saint Marcel'=1, 'Saint Marianne'=1, 'Saint Martine'=1, 'Saint Éricnec'=1
- gold.fact_customer_orders.is_repeat_customer: False=23, True=471
- gold.fact_sales.channel: 'in_store'=2181, 'online'=3345
- gold.fact_sales.status: 'cancelled'=470, 'completed'=4512, 'returned'=544
- gold.fact_sales.is_completed: False=1014, True=4512
- gold.fact_sales.is_returned: False=4982, True=544
- gold.fact_sales.is_cancelled: False=5056, True=470
- gold.rt_freshness.no_events_yet: True=1
- silver.stg_customers.country: 'Belgium'=99, 'France'=90, 'Germany'=105, 'Italy'=108, 'Spain'=98
- silver.stg_orders.channel: 'in_store'=872, 'online'=1328
- silver.stg_orders.status: 'cancelled'=183, 'completed'=1801, 'returned'=216
- silver.stg_products.category: 'Clothing'=28, 'Electronics'=22, 'Home'=21, 'Sports'=29
- silver.stg_stores.store_name: 'Store Chrétien'=1, 'Store Devaux'=1, 'Store Gauthier-sur-Evrard'=1, 'Store Gomes'=1, 'Store Hoareaudan'=1, 'Store Labbéboeuf'=1, 'Store Ollivier-sur-Dupuy'=1, 'Store Perez'=1, 'Store Ribeiro'=1, 'Store Thibault'=1
- silver.stg_stores.country: 'Belgium'=2, 'France'=2, 'Germany'=2, 'Italy'=2, 'Spain'=2
- silver.stg_stores.city: 'Descamps-sur-David'=1, 'Duhamel'=1, 'Faivre-les-Bains'=1, 'Garnier-la-Forêt'=1, 'Gayboeuf'=1, 'Saint Jacqueline'=1, 'Saint Marcel'=1, 'Saint Marianne'=1, 'Saint Martine'=1, 'Saint Éricnec'=1

# Row counts

- bronze.customers: 500 rows
- bronze.order_events: 0 rows
- bronze.order_items: 5526 rows
- bronze.orders: 2200 rows
- bronze.products: 100 rows
- bronze.stores: 10 rows
- gold.dim_customers: 500 rows
- gold.dim_dates: 1096 rows
- gold.dim_products: 100 rows
- gold.dim_stores: 10 rows
- gold.fact_customer_orders: 494 rows
- gold.fact_sales: 5526 rows
- gold.fact_sales_live: 0 rows
- gold.rt_freshness: 1 rows
- silver.stg_customers: 500 rows
- silver.stg_order_events: 0 rows
- silver.stg_order_items: 5526 rows
- silver.stg_orders: 2200 rows
- silver.stg_products: 100 rows
- silver.stg_stores: 10 rows
