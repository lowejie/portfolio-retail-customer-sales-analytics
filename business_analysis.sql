-- ANALYSIS STAGE: BUSINESS INSIGHTS

-- Total Revenue
SELECT ROUND(SUM(purchase_amount_usd), 2) AS total_revenue
FROM sales_cleaned;

-- Average Spend by Gender
SELECT
    gender,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_spend,
    COUNT(*) AS total_orders
FROM sales_cleaned
GROUP BY gender
ORDER BY avg_spend DESC;

-- Top 5 Categories by Revenue
SELECT
    category,
    ROUND(SUM(purchase_amount_usd), 2) AS total_revenue,
    COUNT(*) AS total_orders
FROM sales_cleaned
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 5;

-- Seasonal Sales Trends
SELECT
    season,
    COUNT(*) AS total_orders,
    ROUND(SUM(purchase_amount_usd), 2) AS total_revenue,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_order_value
FROM sales_cleaned
GROUP BY season
ORDER BY total_revenue DESC;

-- Average Review Rating per Category
SELECT
    category,
    ROUND(AVG(review_rating), 2) AS avg_rating,
    COUNT(*) AS num_reviews
FROM sales_cleaned
GROUP BY category
ORDER BY avg_rating DESC;

-- Payment Method Usage
SELECT
    payment_method,
    COUNT(*) AS total_orders,
    ROUND(SUM(purchase_amount_usd), 2) AS total_revenue
FROM sales_cleaned
GROUP BY payment_method
ORDER BY total_orders DESC;

-- Discount vs Non-Discount Purchases
SELECT
    discount_applied,
    COUNT(*) AS total_orders,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_spend
FROM sales_cleaned
GROUP BY discount_applied;

-- Customer Loyalty – Avg Spend by Purchase Frequency
SELECT
    frequency_of_purchases,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_spend,
    ROUND(SUM(purchase_amount_usd), 2) AS total_revenue
FROM sales_cleaned
GROUP BY frequency_of_purchases
ORDER BY total_revenue DESC;

-- Create summarized view for Power BI or further reporting
CREATE OR REPLACE VIEW sales_summary AS
SELECT
    category,
    season,
    payment_method,
    COUNT(*) AS total_orders,
    ROUND(SUM(purchase_amount_usd), 2) AS total_revenue,
    ROUND(AVG(purchase_amount_usd), 2) AS avg_order_value
FROM sales_cleaned
GROUP BY category, season, payment_method;

SELECT * FROM sales_summary;
