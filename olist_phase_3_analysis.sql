-- ============================================================
-- Project 1: E-commerce Sales & Customer Behaviour Analysis
-- Phase 3: SQL Analysis in MySQL
-- Dataset: Olist Brazilian E-Commerce
-- ============================================================


-- ============================================================
-- STEP 1: Create the database and select it
-- ============================================================

CREATE DATABASE IF NOT EXISTS olist_ecommerce;
USE olist_ecommerce;


-- ============================================================
-- STEP 2: Create tables to match your CSV files
-- ============================================================

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id                        VARCHAR(50) PRIMARY KEY,
    customer_id                     VARCHAR(50),
    order_status                    VARCHAR(30),
    order_purchase_timestamp        DATETIME,
    order_approved_at               DATETIME,
    order_delivered_carrier_date    DATETIME,
    order_delivered_customer_date   DATETIME,
    order_estimated_delivery_date   DATETIME,
    order_year                      INT,
    order_month                     INT,
    order_month_name                VARCHAR(20),
    order_dayofweek                 VARCHAR(15),
    order_hour                      INT
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id             VARCHAR(50) PRIMARY KEY,
    customer_unique_id      VARCHAR(50),
    customer_zip_code       VARCHAR(10),
    customer_city           VARCHAR(100),
    customer_state          VARCHAR(5)
);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    order_id            VARCHAR(50),
    order_item_id       INT,
    product_id          VARCHAR(50),
    seller_id           VARCHAR(50),
    shipping_limit_date DATETIME,
    price               DECIMAL(10,2),
    freight_value       DECIMAL(10,2),
    revenue             DECIMAL(10,2)
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    product_id                      VARCHAR(50) PRIMARY KEY,
    product_category_name           VARCHAR(100),
    product_category_name_english   VARCHAR(100),
    product_name_length             INT,
    product_description_length      INT,
    product_photos_qty              INT,
    product_weight_g                DECIMAL(10,2),
    product_length_cm               DECIMAL(10,2),
    product_height_cm               DECIMAL(10,2),
    product_width_cm                DECIMAL(10,2)
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    order_id                VARCHAR(50),
    payment_sequential      INT,
    payment_type            VARCHAR(30),
    payment_installments    INT,
    payment_value           DECIMAL(10,2)
);


-- ============================================================
-- STEP 3: Import CSVs using MySQL Workbench Table Data Import
-- ============================================================
-- For each table, use: Server → Data Import → Import from CSV
-- OR use the Table Data Import Wizard (right-click table → Import)
--
-- Import these files into matching tables:
--   olist_orders_dataset.csv      → orders
--   olist_customers_dataset.csv   → customers
--   olist_order_items_dataset.csv → order_items
--   olist_products_dataset.csv    → products
--   olist_order_payments_dataset  → payments
-- ============================================================


-- ============================================================
-- QUERY 1: Total revenue, orders and avg order value by month
-- ============================================================

SELECT
    o.order_year,
    o.order_month,
    COUNT(DISTINCT o.order_id)          AS total_orders,
    ROUND(SUM(oi.revenue), 2)           AS total_revenue,
    ROUND(AVG(oi.revenue), 2)           AS avg_item_value,
    ROUND(SUM(oi.revenue) /
          COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
  AND o.order_year IN (2017, 2018)
GROUP BY o.order_year, o.order_month
ORDER BY o.order_year, o.order_month;


-- ============================================================
-- QUERY 2: Top 10 product categories by total revenue
-- ============================================================

SELECT
    p.product_category_name_english     AS category,
    COUNT(DISTINCT oi.order_id)         AS total_orders,
    ROUND(SUM(oi.revenue), 2)           AS total_revenue,
    ROUND(AVG(oi.price), 2)             AS avg_price,
    ROUND(SUM(oi.revenue) * 100.0 /
         (SELECT SUM(revenue) FROM order_items), 2) AS revenue_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name_english
ORDER BY total_revenue DESC
LIMIT 10;


-- ============================================================
-- QUERY 3: Revenue and orders by Brazilian state
-- ============================================================

SELECT
    c.customer_state                    AS state,
    COUNT(DISTINCT o.order_id)          AS total_orders,
    COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
    ROUND(SUM(oi.revenue), 2)           AS total_revenue,
    ROUND(AVG(oi.revenue), 2)           AS avg_order_value
FROM orders o
JOIN order_items oi  ON o.order_id  = oi.order_id
JOIN customers c     ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY total_revenue DESC;


-- ============================================================
-- QUERY 4: Average delivery time and late delivery rate
-- ============================================================

SELECT
    c.customer_state                            AS state,
    COUNT(o.order_id)                           AS total_orders,
    ROUND(AVG(
        DATEDIFF(o.order_delivered_customer_date,
                 o.order_purchase_timestamp)
    ), 1)                                       AS avg_delivery_days,
    ROUND(AVG(
        DATEDIFF(o.order_estimated_delivery_date,
                 o.order_purchase_timestamp)
    ), 1)                                       AS avg_estimated_days,
    SUM(CASE
        WHEN o.order_delivered_customer_date >
             o.order_estimated_delivery_date THEN 1
        ELSE 0
    END)                                        AS late_deliveries,
    ROUND(SUM(CASE
        WHEN o.order_delivered_customer_date >
             o.order_estimated_delivery_date THEN 1
        ELSE 0
    END) * 100.0 / COUNT(o.order_id), 1)        AS late_delivery_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY avg_delivery_days DESC;


-- ============================================================
-- QUERY 5: Repeat vs one-time customers (CTE)
-- ============================================================

WITH customer_order_counts AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
customer_segments AS (
    SELECT
        customer_unique_id,
        order_count,
        CASE
            WHEN order_count = 1 THEN 'One-time buyer'
            WHEN order_count BETWEEN 2 AND 3 THEN 'Returning buyer'
            ELSE 'Loyal buyer'
        END AS segment
    FROM customer_order_counts
)
SELECT
    segment,
    COUNT(*)                                AS customer_count,
    ROUND(COUNT(*) * 100.0 /
          SUM(COUNT(*)) OVER (), 1)         AS percentage
FROM customer_segments
GROUP BY segment
ORDER BY customer_count DESC;


-- ============================================================
-- QUERY 6: Top 10 sellers ranked by revenue (Window Function)
-- ============================================================

WITH seller_revenue AS (
    SELECT
        oi.seller_id,
        COUNT(DISTINCT oi.order_id)     AS total_orders,
        ROUND(SUM(oi.revenue), 2)       AS total_revenue,
        ROUND(AVG(oi.price), 2)         AS avg_price,
        COUNT(DISTINCT oi.product_id)   AS unique_products
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi.seller_id
)
SELECT
    RANK() OVER (ORDER BY total_revenue DESC)   AS revenue_rank,
    seller_id,
    total_orders,
    total_revenue,
    avg_price,
    unique_products
FROM seller_revenue
ORDER BY revenue_rank
LIMIT 10;


-- ============================================================
-- QUERY 7: Payment method breakdown
-- ============================================================

SELECT
    payment_type,
    COUNT(DISTINCT order_id)            AS total_orders,
    ROUND(SUM(payment_value), 2)        AS total_value,
    ROUND(AVG(payment_value), 2)        AS avg_payment,
    ROUND(AVG(payment_installments), 1) AS avg_installments,
    ROUND(COUNT(*) * 100.0 /
          SUM(COUNT(*)) OVER (), 1)     AS pct_of_orders
FROM payments
GROUP BY payment_type
ORDER BY total_orders DESC;


-- ============================================================
-- QUERY 8: Peak ordering hours (best hours of the day)
-- ============================================================

SELECT
    order_hour                          AS hour_of_day,
    COUNT(DISTINCT order_id)            AS total_orders,
    RANK() OVER (ORDER BY
        COUNT(DISTINCT order_id) DESC)  AS popularity_rank
FROM orders
GROUP BY order_hour
ORDER BY hour_of_day;


-- ============================================================
-- QUERY 9: Revenue growth month-over-month (Window Function)
-- ============================================================

WITH monthly AS (
    SELECT
        o.order_year,
        o.order_month,
        ROUND(SUM(oi.revenue), 2) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_year IN (2017, 2018)
    GROUP BY o.order_year, o.order_month
)
SELECT
    order_year,
    order_month,
    revenue,
    LAG(revenue) OVER (ORDER BY order_year, order_month) AS prev_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY order_year, order_month))
        * 100.0 /
        NULLIF(LAG(revenue) OVER (ORDER BY order_year, order_month), 0)
    , 1)                                                  AS mom_growth_pct
FROM monthly
ORDER BY order_year, order_month;


-- ============================================================
-- QUERY 10: Full summary export for Power BI
-- ============================================================

SELECT
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_year,
    o.order_month,
    o.order_dayofweek,
    o.order_hour,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    DATEDIFF(o.order_delivered_customer_date,
             o.order_purchase_timestamp)        AS delivery_days,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    p.product_category_name_english             AS category,
    oi.price,
    oi.freight_value,
    oi.revenue,
    pay.payment_type,
    pay.payment_value,
    pay.payment_installments
FROM orders o
JOIN order_items oi  ON o.order_id    = oi.order_id
JOIN customers c     ON o.customer_id = c.customer_id
JOIN products p      ON oi.product_id = p.product_id
LEFT JOIN (
    SELECT order_id,
           MAX(payment_type)         AS payment_type,
           SUM(payment_value)        AS payment_value,
           MAX(payment_installments) AS payment_installments
    FROM payments
    GROUP BY order_id
) pay ON o.order_id = pay.order_id
WHERE o.order_status = 'delivered'
  AND o.order_year IN (2017, 2018);
