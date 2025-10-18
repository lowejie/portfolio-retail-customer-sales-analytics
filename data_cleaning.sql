-- TRANSFORM STAGE: DATA CLEANING & PREPARATION

DROP TABLE IF EXISTS sales_cleaned;

CREATE TABLE sales_cleaned AS
SELECT
    transaction_id,
    transaction_time,
    TRIM(customer_id) AS customer_id,
    CASE
        WHEN age BETWEEN 10 AND 100 THEN age
        ELSE NULL
    END AS age,
    INITCAP(gender) AS gender,
    INITCAP(item_purchased) AS item_purchased,
    INITCAP(category) AS category,
    ROUND(purchase_amount_usd::NUMERIC, 2) AS purchase_amount_usd,
    INITCAP(location) AS location,
    UPPER(size) AS size,
    INITCAP(color) AS color,
    INITCAP(season) AS season,
    COALESCE(review_rating, 0) AS review_rating,
    INITCAP(subscription_status) AS subscription_status,
    INITCAP(payment_method) AS payment_method,
    INITCAP(shipping_type) AS shipping_type,
    COALESCE(discount_applied, FALSE) AS discount_applied,
    COALESCE(promo_code_used, FALSE) AS promo_code_used,
    COALESCE(previous_purchases, 0) AS previous_purchases,
    INITCAP(preferred_payment_method) AS preferred_payment_method,
    INITCAP(frequency_of_purchases) AS frequency_of_purchases
FROM public.staging_sales
WHERE purchase_amount_usd IS NOT NULL;

COMMIT;

-- Validation queries
SELECT COUNT(*) AS total_cleaned_rows FROM sales_cleaned;

SELECT COUNT(*) AS null_customer_ids
FROM sales_cleaned
WHERE customer_id IS NULL;

SELECT DISTINCT gender FROM sales_cleaned ORDER BY gender;
