# Raw landing files (CSV headers; written by scripts/generate_raw_data.py, loaded into schema bronze)

- data/raw/customers.csv: customer_id, first_name, last_name, email, country, city, signup_date
- data/raw/order_items.csv: order_item_id, order_id, product_id, quantity, unit_price
- data/raw/orders.csv: order_id, customer_id, store_id, order_date, channel, status
- data/raw/products.csv: product_id, product_name, category, unit_cost, list_price
- data/raw/stores.csv: store_id, store_name, country, city
