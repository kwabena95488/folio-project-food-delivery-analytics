-- Customer Analytics Queries
-- Advanced SQL for Customer Intelligence and Segmentation

-- 1. Customer Lifetime Value (CLV) Analysis with Segmentation
WITH customer_metrics AS (
    SELECT 
        c.customer_id,
        c.name,
        c.email,
        c.loyalty_tier,
        c.registration_date,
        COUNT(o.order_id) as order_frequency,
        COALESCE(AVG(o.total_amount), 0) as avg_order_value,
        COALESCE(SUM(o.total_amount), 0) as total_spent,
        MIN(o.order_date) as first_order_date,
        MAX(o.order_date) as last_order_date,
        JULIANDAY('now') - JULIANDAY(MAX(o.order_date)) as days_since_last_order
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
    GROUP BY c.customer_id, c.name, c.email, c.loyalty_tier, c.registration_date
),
clv_calculation AS (
    SELECT *,
        -- Estimated CLV: frequency * avg_order_value * estimated_lifespan_months
        CASE 
            WHEN order_frequency > 0 THEN 
                order_frequency * avg_order_value * 12.0  -- Annualized estimate
            ELSE 0 
        END as estimated_clv,
        CASE 
            WHEN days_since_last_order IS NULL THEN 'Never Ordered'
            WHEN days_since_last_order <= 30 THEN 'Active'
            WHEN days_since_last_order <= 90 THEN 'At Risk'
            ELSE 'Churned'
        END as customer_status,
        -- Customer value tier based on total spent
        CASE 
            WHEN total_spent >= 500 THEN 'High Value'
            WHEN total_spent >= 200 THEN 'Medium Value'
            WHEN total_spent > 0 THEN 'Low Value'
            ELSE 'No Value'
        END as value_tier
    FROM customer_metrics
)
SELECT 
    customer_status,
    value_tier,
    COUNT(*) as customer_count,
    ROUND(AVG(estimated_clv), 2) as avg_clv,
    ROUND(SUM(total_spent), 2) as total_revenue,
    ROUND(AVG(total_spent), 2) as avg_total_spent,
    ROUND(AVG(order_frequency), 2) as avg_order_frequency,
    ROUND(AVG(avg_order_value), 2) as avg_order_value
FROM clv_calculation
GROUP BY customer_status, value_tier
ORDER BY customer_status, value_tier;

-- 2. RFM Analysis (Recency, Frequency, Monetary)
WITH rfm_metrics AS (
    SELECT 
        c.customer_id,
        c.name,
        -- Recency: Days since last order
        COALESCE(JULIANDAY('now') - JULIANDAY(MAX(o.order_date)), 999) as recency_days,
        -- Frequency: Number of orders
        COUNT(o.order_id) as frequency,
        -- Monetary: Total amount spent
        COALESCE(SUM(o.total_amount), 0) as monetary
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
    GROUP BY c.customer_id, c.name
),
rfm_scores AS (
    SELECT *,
        -- Recency Score (1-5, where 5 is most recent)
        CASE 
            WHEN recency_days <= 30 THEN 5
            WHEN recency_days <= 60 THEN 4
            WHEN recency_days <= 90 THEN 3
            WHEN recency_days <= 180 THEN 2
            ELSE 1
        END as recency_score,
        -- Frequency Score (1-5, based on quintiles)
        NTILE(5) OVER (ORDER BY frequency) as frequency_score,
        -- Monetary Score (1-5, based on quintiles)
        NTILE(5) OVER (ORDER BY monetary) as monetary_score
    FROM rfm_metrics
),
rfm_segments AS (
    SELECT *,
        (recency_score * 100 + frequency_score * 10 + monetary_score) as rfm_combined,
        CASE 
            WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
            WHEN recency_score >= 3 AND frequency_score >= 3 AND monetary_score >= 3 THEN 'Loyal Customers'
            WHEN recency_score >= 4 AND frequency_score <= 2 THEN 'New Customers'
            WHEN recency_score >= 3 AND frequency_score <= 2 AND monetary_score >= 3 THEN 'Potential Loyalists'
            WHEN recency_score >= 3 AND frequency_score >= 3 AND monetary_score <= 2 THEN 'Need Attention'
            WHEN recency_score <= 2 AND frequency_score >= 3 AND monetary_score >= 3 THEN 'At Risk'
            WHEN recency_score <= 2 AND frequency_score >= 2 AND monetary_score >= 2 THEN 'Cannot Lose Them'
            WHEN recency_score <= 2 AND frequency_score <= 2 AND monetary_score >= 3 THEN 'Hibernating'
            ELSE 'Lost'
        END as rfm_segment
    FROM rfm_scores
)
SELECT 
    rfm_segment,
    COUNT(*) as customer_count,
    ROUND(AVG(recency_days), 1) as avg_recency_days,
    ROUND(AVG(frequency), 1) as avg_frequency,
    ROUND(AVG(monetary), 2) as avg_monetary,
    ROUND(SUM(monetary), 2) as total_revenue,
    ROUND(AVG(recency_score), 2) as avg_recency_score,
    ROUND(AVG(frequency_score), 2) as avg_frequency_score,
    ROUND(AVG(monetary_score), 2) as avg_monetary_score
FROM rfm_segments
GROUP BY rfm_segment
ORDER BY total_revenue DESC;

-- 3. Customer Cohort Analysis
WITH customer_cohorts AS (
    SELECT 
        c.customer_id,
        c.name,
        DATE(c.registration_date, 'start of month') as cohort_month,
        DATE(o.order_date, 'start of month') as order_month,
        o.total_amount
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
),
cohort_data AS (
    SELECT 
        cohort_month,
        order_month,
        COUNT(DISTINCT customer_id) as customers,
        SUM(total_amount) as revenue,
        -- Calculate months since cohort start
        (strftime('%Y', order_month) - strftime('%Y', cohort_month)) * 12 + 
        (strftime('%m', order_month) - strftime('%m', cohort_month)) as months_since_cohort
    FROM customer_cohorts
    GROUP BY cohort_month, order_month
),
cohort_sizes AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) as cohort_size
    FROM customer_cohorts
    GROUP BY cohort_month
)
SELECT 
    cd.cohort_month,
    cs.cohort_size,
    cd.months_since_cohort,
    cd.customers,
    ROUND(cd.customers * 100.0 / cs.cohort_size, 2) as retention_rate,
    ROUND(cd.revenue, 2) as cohort_revenue,
    ROUND(cd.revenue / cd.customers, 2) as revenue_per_customer
FROM cohort_data cd
JOIN cohort_sizes cs ON cd.cohort_month = cs.cohort_month
WHERE cd.months_since_cohort <= 12  -- First 12 months
ORDER BY cd.cohort_month, cd.months_since_cohort;

-- 4. Customer Churn Prediction Indicators
WITH customer_behavior AS (
    SELECT 
        c.customer_id,
        c.name,
        c.registration_date,
        COUNT(o.order_id) as total_orders,
        MAX(o.order_date) as last_order_date,
        MIN(o.order_date) as first_order_date,
        AVG(o.total_amount) as avg_order_value,
        SUM(o.total_amount) as total_spent,
        -- Calculate average days between orders
        CASE 
            WHEN COUNT(o.order_id) > 1 THEN 
                (JULIANDAY(MAX(o.order_date)) - JULIANDAY(MIN(o.order_date))) / (COUNT(o.order_id) - 1)
            ELSE NULL 
        END as avg_days_between_orders,
        JULIANDAY('now') - JULIANDAY(MAX(o.order_date)) as days_since_last_order
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
    GROUP BY c.customer_id, c.name, c.registration_date
),
churn_indicators AS (
    SELECT *,
        CASE 
            WHEN days_since_last_order IS NULL THEN 'Never Ordered'
            WHEN days_since_last_order > (avg_days_between_orders * 2) AND avg_days_between_orders IS NOT NULL THEN 'High Risk'
            WHEN days_since_last_order > avg_days_between_orders AND avg_days_between_orders IS NOT NULL THEN 'Medium Risk'
            WHEN days_since_last_order <= 30 THEN 'Low Risk'
            WHEN days_since_last_order <= 60 THEN 'Medium Risk'
            ELSE 'High Risk'
        END as churn_risk,
        -- Customer lifetime in days
        JULIANDAY('now') - JULIANDAY(registration_date) as customer_lifetime_days,
        -- Order frequency (orders per month)
        CASE 
            WHEN total_orders > 0 AND customer_lifetime_days > 0 THEN 
                total_orders * 30.0 / (JULIANDAY('now') - JULIANDAY(registration_date))
            ELSE 0 
        END as orders_per_month
    FROM customer_behavior
)
SELECT 
    churn_risk,
    COUNT(*) as customer_count,
    ROUND(AVG(total_orders), 2) as avg_total_orders,
    ROUND(AVG(days_since_last_order), 1) as avg_days_since_last_order,
    ROUND(AVG(avg_order_value), 2) as avg_order_value,
    ROUND(SUM(total_spent), 2) as total_revenue,
    ROUND(AVG(orders_per_month), 2) as avg_orders_per_month,
    ROUND(AVG(customer_lifetime_days), 1) as avg_customer_lifetime_days
FROM churn_indicators
GROUP BY churn_risk
ORDER BY 
    CASE churn_risk 
        WHEN 'Never Ordered' THEN 1
        WHEN 'High Risk' THEN 2
        WHEN 'Medium Risk' THEN 3
        WHEN 'Low Risk' THEN 4
    END;

-- 5. Customer Journey Analysis
WITH customer_journey AS (
    SELECT 
        c.customer_id,
        c.name,
        c.registration_date,
        o.order_id,
        o.order_date,
        o.total_amount,
        ROW_NUMBER() OVER (PARTITION BY c.customer_id ORDER BY o.order_date) as order_sequence,
        LAG(o.order_date) OVER (PARTITION BY c.customer_id ORDER BY o.order_date) as prev_order_date,
        LAG(o.total_amount) OVER (PARTITION BY c.customer_id ORDER BY o.order_date) as prev_order_amount
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
),
journey_metrics AS (
    SELECT *,
        CASE 
            WHEN prev_order_date IS NOT NULL THEN 
                JULIANDAY(order_date) - JULIANDAY(prev_order_date)
            ELSE NULL 
        END as days_between_orders,
        CASE 
            WHEN prev_order_amount IS NOT NULL THEN 
                total_amount - prev_order_amount
            ELSE NULL 
        END as order_value_change
    FROM customer_journey
)
SELECT 
    order_sequence,
    COUNT(*) as customers_at_stage,
    ROUND(AVG(total_amount), 2) as avg_order_value,
    ROUND(AVG(days_between_orders), 1) as avg_days_between_orders,
    ROUND(AVG(order_value_change), 2) as avg_order_value_change,
    -- Retention rate to next order
    ROUND(
        COUNT(CASE WHEN order_sequence < (SELECT MAX(order_sequence) FROM journey_metrics) THEN 1 END) * 100.0 / 
        COUNT(*), 2
    ) as retention_to_next_order
FROM journey_metrics
WHERE order_sequence <= 10  -- First 10 orders
GROUP BY order_sequence
ORDER BY order_sequence;

-- 6. Customer Preference Analysis
WITH customer_preferences AS (
    SELECT 
        c.customer_id,
        c.name,
        c.preferred_cuisine,
        r.cuisine_type as ordered_cuisine,
        mi.category,
        COUNT(*) as order_count,
        SUM(oi.quantity * oi.unit_price) as total_spent_category,
        AVG(oi.item_rating) as avg_rating
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN menu_items mi ON oi.item_id = mi.item_id
    JOIN restaurants r ON o.restaurant_id = r.restaurant_id
    GROUP BY c.customer_id, c.name, c.preferred_cuisine, r.cuisine_type, mi.category
),
preference_rankings AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY total_spent_category DESC) as preference_rank
    FROM customer_preferences
)
SELECT 
    preferred_cuisine,
    ordered_cuisine,
    category,
    COUNT(DISTINCT customer_id) as customers,
    SUM(order_count) as total_orders,
    ROUND(SUM(total_spent_category), 2) as total_revenue,
    ROUND(AVG(avg_rating), 2) as avg_item_rating,
    -- Preference alignment
    CASE 
        WHEN preferred_cuisine = ordered_cuisine THEN 'Aligned'
        ELSE 'Cross-Cuisine'
    END as preference_alignment
FROM preference_rankings
WHERE preference_rank <= 3  -- Top 3 preferences per customer
GROUP BY preferred_cuisine, ordered_cuisine, category
ORDER BY total_revenue DESC
LIMIT 20; 