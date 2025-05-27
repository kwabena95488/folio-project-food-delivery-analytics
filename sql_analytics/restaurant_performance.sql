-- Restaurant Performance Analytics
-- Advanced SQL for Restaurant Business Intelligence

-- 1. Multi-Dimensional Restaurant Performance Ranking
WITH restaurant_metrics AS (
    SELECT 
        r.restaurant_id,
        r.name as restaurant_name,
        r.city,
        r.cuisine_type,
        r.rating as base_rating,
        COUNT(DISTINCT o.order_id) as total_orders,
        COUNT(DISTINCT o.customer_id) as unique_customers,
        COUNT(DISTINCT DATE(o.order_date)) as active_days,
        COALESCE(SUM(o.total_amount), 0) as total_revenue,
        COALESCE(AVG(o.total_amount), 0) as avg_order_value,
        COALESCE(AVG(o.delivery_time_minutes), 0) as avg_delivery_time,
        COALESCE(SUM(o.tip_amount), 0) as total_tips,
        -- Customer retention metrics
        COUNT(DISTINCT CASE WHEN o.order_date >= date('now', '-30 days') THEN o.customer_id END) as recent_customers,
        -- Order completion rate
        COUNT(CASE WHEN o.status = 'completed' THEN 1 END) * 100.0 / COUNT(*) as completion_rate
    FROM restaurants r
    LEFT JOIN orders o ON r.restaurant_id = o.restaurant_id
    WHERE r.is_active = 1
    GROUP BY r.restaurant_id, r.name, r.city, r.cuisine_type, r.rating
),
performance_rankings AS (
    SELECT *,
        -- Revenue ranking (higher is better)
        ROW_NUMBER() OVER (ORDER BY total_revenue DESC) as revenue_rank,
        -- Efficiency ranking (lower delivery time is better)
        ROW_NUMBER() OVER (ORDER BY avg_delivery_time ASC) as efficiency_rank,
        -- Customer satisfaction ranking (higher rating is better)
        ROW_NUMBER() OVER (ORDER BY base_rating DESC) as rating_rank,
        -- Volume ranking (more orders is better)
        ROW_NUMBER() OVER (ORDER BY total_orders DESC) as volume_rank,
        -- Customer loyalty ranking (higher retention is better)
        ROW_NUMBER() OVER (ORDER BY recent_customers DESC) as loyalty_rank,
        -- Calculate revenue per customer
        CASE WHEN unique_customers > 0 THEN total_revenue / unique_customers ELSE 0 END as revenue_per_customer,
        -- Calculate orders per active day
        CASE WHEN active_days > 0 THEN total_orders * 1.0 / active_days ELSE 0 END as orders_per_day
    FROM restaurant_metrics
),
overall_scores AS (
    SELECT *,
        -- Weighted overall score (lower is better)
        (revenue_rank * 0.3 + efficiency_rank * 0.2 + rating_rank * 0.2 + 
         volume_rank * 0.15 + loyalty_rank * 0.15) as weighted_score,
        -- Performance tier classification
        CASE 
            WHEN revenue_rank <= 5 AND efficiency_rank <= 10 THEN 'Top Performer'
            WHEN revenue_rank <= 10 AND efficiency_rank <= 15 THEN 'Strong Performer'
            WHEN revenue_rank <= 15 OR efficiency_rank <= 20 THEN 'Average Performer'
            ELSE 'Needs Improvement'
        END as performance_tier
    FROM performance_rankings
)
SELECT 
    restaurant_name,
    city,
    cuisine_type,
    performance_tier,
    total_orders,
    ROUND(total_revenue, 2) as total_revenue,
    ROUND(avg_order_value, 2) as avg_order_value,
    ROUND(avg_delivery_time, 1) as avg_delivery_time_min,
    ROUND(base_rating, 2) as rating,
    ROUND(completion_rate, 1) as completion_rate_pct,
    unique_customers,
    recent_customers,
    ROUND(revenue_per_customer, 2) as revenue_per_customer,
    ROUND(orders_per_day, 1) as orders_per_day,
    revenue_rank,
    efficiency_rank,
    ROUND(weighted_score, 2) as overall_score
FROM overall_scores
ORDER BY weighted_score;

-- 2. Restaurant Revenue Trends and Forecasting
WITH daily_revenue AS (
    SELECT 
        r.restaurant_id,
        r.name as restaurant_name,
        DATE(o.order_date) as order_date,
        COUNT(o.order_id) as daily_orders,
        SUM(o.total_amount) as daily_revenue,
        AVG(o.total_amount) as avg_order_value
    FROM restaurants r
    JOIN orders o ON r.restaurant_id = o.restaurant_id AND o.status = 'completed'
    WHERE o.order_date >= date('now', '-90 days')
    GROUP BY r.restaurant_id, r.name, DATE(o.order_date)
),
revenue_trends AS (
    SELECT *,
        -- 7-day moving average
        AVG(daily_revenue) OVER (
            PARTITION BY restaurant_id 
            ORDER BY order_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as revenue_7day_ma,
        -- 14-day moving average
        AVG(daily_revenue) OVER (
            PARTITION BY restaurant_id 
            ORDER BY order_date 
            ROWS BETWEEN 13 PRECEDING AND CURRENT ROW
        ) as revenue_14day_ma,
        -- Week-over-week growth
        LAG(daily_revenue, 7) OVER (
            PARTITION BY restaurant_id 
            ORDER BY order_date
        ) as revenue_7days_ago,
        -- Month-over-month comparison
        LAG(daily_revenue, 30) OVER (
            PARTITION BY restaurant_id 
            ORDER BY order_date
        ) as revenue_30days_ago
    FROM daily_revenue
),
growth_metrics AS (
    SELECT *,
        CASE 
            WHEN revenue_7days_ago > 0 THEN 
                (daily_revenue - revenue_7days_ago) * 100.0 / revenue_7days_ago
            ELSE NULL 
        END as wow_growth_pct,
        CASE 
            WHEN revenue_30days_ago > 0 THEN 
                (daily_revenue - revenue_30days_ago) * 100.0 / revenue_30days_ago
            ELSE NULL 
        END as mom_growth_pct
    FROM revenue_trends
)
SELECT 
    restaurant_name,
    COUNT(*) as days_with_data,
    ROUND(AVG(daily_revenue), 2) as avg_daily_revenue,
    ROUND(AVG(revenue_7day_ma), 2) as avg_7day_ma,
    ROUND(AVG(revenue_14day_ma), 2) as avg_14day_ma,
    ROUND(AVG(wow_growth_pct), 2) as avg_wow_growth_pct,
    ROUND(AVG(mom_growth_pct), 2) as avg_mom_growth_pct,
    ROUND(MIN(daily_revenue), 2) as min_daily_revenue,
    ROUND(MAX(daily_revenue), 2) as max_daily_revenue,
    ROUND(
        (MAX(daily_revenue) - MIN(daily_revenue)) * 100.0 / 
        NULLIF(MIN(daily_revenue), 0), 2
    ) as revenue_volatility_pct
FROM growth_metrics
GROUP BY restaurant_id, restaurant_name
HAVING COUNT(*) >= 30  -- At least 30 days of data
ORDER BY avg_daily_revenue DESC;

-- 3. Peak Hours and Operational Efficiency Analysis
WITH hourly_patterns AS (
    SELECT 
        r.restaurant_id,
        r.name as restaurant_name,
        r.avg_prep_time_minutes as expected_prep_time,
        strftime('%H', o.order_date) as hour_of_day,
        strftime('%w', o.order_date) as day_of_week,  -- 0=Sunday, 6=Saturday
        COUNT(*) as order_count,
        SUM(o.total_amount) as hourly_revenue,
        AVG(o.delivery_time_minutes) as avg_delivery_time,
        AVG(o.total_amount) as avg_order_value,
        COUNT(CASE WHEN o.status = 'completed' THEN 1 END) * 100.0 / COUNT(*) as completion_rate
    FROM restaurants r
    JOIN orders o ON r.restaurant_id = o.restaurant_id
    WHERE o.order_date >= date('now', '-30 days')
    GROUP BY r.restaurant_id, r.name, r.avg_prep_time_minutes, 
             strftime('%H', o.order_date), strftime('%w', o.order_date)
),
peak_analysis AS (
    SELECT *,
        -- Classify hours as peak/off-peak
        CASE 
            WHEN hour_of_day IN ('11', '12', '13', '18', '19', '20') THEN 'Peak'
            WHEN hour_of_day IN ('14', '15', '16', '17', '21') THEN 'Moderate'
            ELSE 'Off-Peak'
        END as hour_category,
        -- Classify days
        CASE 
            WHEN day_of_week IN ('0', '6') THEN 'Weekend'
            ELSE 'Weekday'
        END as day_category,
        -- Efficiency score (lower delivery time relative to prep time is better)
        CASE 
            WHEN expected_prep_time > 0 THEN 
                avg_delivery_time / expected_prep_time
            ELSE NULL 
        END as efficiency_ratio
    FROM hourly_patterns
)
SELECT 
    restaurant_name,
    hour_category,
    day_category,
    COUNT(*) as time_periods,
    SUM(order_count) as total_orders,
    ROUND(SUM(hourly_revenue), 2) as total_revenue,
    ROUND(AVG(avg_order_value), 2) as avg_order_value,
    ROUND(AVG(avg_delivery_time), 1) as avg_delivery_time,
    ROUND(AVG(completion_rate), 1) as avg_completion_rate,
    ROUND(AVG(efficiency_ratio), 2) as avg_efficiency_ratio,
    -- Peak performance indicators
    CASE 
        WHEN AVG(efficiency_ratio) <= 1.2 THEN 'Excellent'
        WHEN AVG(efficiency_ratio) <= 1.5 THEN 'Good'
        WHEN AVG(efficiency_ratio) <= 2.0 THEN 'Average'
        ELSE 'Needs Improvement'
    END as efficiency_grade
FROM peak_analysis
GROUP BY restaurant_name, hour_category, day_category
ORDER BY restaurant_name, 
         CASE hour_category WHEN 'Peak' THEN 1 WHEN 'Moderate' THEN 2 ELSE 3 END,
         day_category;

-- 4. Menu Performance and Profitability Analysis
WITH menu_performance AS (
    SELECT 
        r.restaurant_id,
        r.name as restaurant_name,
        r.cuisine_type,
        mi.item_id,
        mi.item_name,
        mi.category,
        mi.price,
        mi.cost_to_make,
        COUNT(oi.order_item_id) as times_ordered,
        SUM(oi.quantity) as total_quantity_sold,
        SUM(oi.quantity * oi.unit_price) as total_revenue,
        AVG(oi.item_rating) as avg_rating,
        -- Profitability metrics
        CASE 
            WHEN mi.cost_to_make > 0 THEN 
                (mi.price - mi.cost_to_make) / mi.price * 100
            ELSE NULL 
        END as profit_margin_pct,
        CASE 
            WHEN mi.cost_to_make > 0 THEN 
                SUM(oi.quantity) * (mi.price - mi.cost_to_make)
            ELSE NULL 
        END as total_profit
    FROM restaurants r
    JOIN menu_items mi ON r.restaurant_id = mi.restaurant_id
    LEFT JOIN order_items oi ON mi.item_id = oi.item_id
    WHERE mi.is_available = 1
    GROUP BY r.restaurant_id, r.name, r.cuisine_type, mi.item_id, 
             mi.item_name, mi.category, mi.price, mi.cost_to_make
),
category_benchmarks AS (
    SELECT 
        restaurant_id,
        category,
        AVG(times_ordered) as avg_category_orders,
        AVG(total_revenue) as avg_category_revenue,
        AVG(profit_margin_pct) as avg_category_margin
    FROM menu_performance
    WHERE times_ordered > 0
    GROUP BY restaurant_id, category
),
item_classification AS (
    SELECT 
        mp.*,
        cb.avg_category_orders,
        cb.avg_category_revenue,
        cb.avg_category_margin,
        -- Performance classification
        CASE 
            WHEN mp.times_ordered > cb.avg_category_orders * 1.5 AND 
                 mp.profit_margin_pct > cb.avg_category_margin THEN 'Star'
            WHEN mp.times_ordered > cb.avg_category_orders * 1.2 THEN 'Performer'
            WHEN mp.times_ordered > cb.avg_category_orders * 0.8 THEN 'Average'
            WHEN mp.profit_margin_pct > cb.avg_category_margin * 1.2 THEN 'Profitable Niche'
            ELSE 'Underperformer'
        END as performance_category,
        -- Revenue contribution
        mp.total_revenue * 100.0 / SUM(mp.total_revenue) OVER (PARTITION BY mp.restaurant_id) as revenue_contribution_pct
    FROM menu_performance mp
    LEFT JOIN category_benchmarks cb ON mp.restaurant_id = cb.restaurant_id AND mp.category = cb.category
)
SELECT 
    restaurant_name,
    cuisine_type,
    performance_category,
    COUNT(*) as item_count,
    ROUND(SUM(total_revenue), 2) as category_revenue,
    ROUND(AVG(profit_margin_pct), 2) as avg_profit_margin,
    ROUND(SUM(total_profit), 2) as category_profit,
    ROUND(AVG(avg_rating), 2) as avg_item_rating,
    ROUND(SUM(revenue_contribution_pct), 2) as total_revenue_contribution_pct
FROM item_classification
WHERE times_ordered > 0
GROUP BY restaurant_name, cuisine_type, performance_category
ORDER BY restaurant_name, category_revenue DESC;

-- 5. Customer Satisfaction and Loyalty Analysis
WITH customer_restaurant_metrics AS (
    SELECT 
        r.restaurant_id,
        r.name as restaurant_name,
        r.cuisine_type,
        o.customer_id,
        COUNT(o.order_id) as customer_order_count,
        SUM(o.total_amount) as customer_total_spent,
        AVG(o.total_amount) as customer_avg_order,
        MIN(o.order_date) as first_order_date,
        MAX(o.order_date) as last_order_date,
        AVG(o.delivery_time_minutes) as avg_delivery_time,
        AVG(oi.item_rating) as avg_item_rating,
        -- Customer loyalty indicators
        JULIANDAY('now') - JULIANDAY(MAX(o.order_date)) as days_since_last_order,
        CASE 
            WHEN COUNT(o.order_id) >= 5 THEN 'Loyal'
            WHEN COUNT(o.order_id) >= 3 THEN 'Regular'
            WHEN COUNT(o.order_id) >= 2 THEN 'Repeat'
            ELSE 'One-time'
        END as customer_loyalty_tier
    FROM restaurants r
    JOIN orders o ON r.restaurant_id = o.restaurant_id AND o.status = 'completed'
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY r.restaurant_id, r.name, r.cuisine_type, o.customer_id
),
restaurant_loyalty_summary AS (
    SELECT 
        restaurant_id,
        restaurant_name,
        cuisine_type,
        COUNT(DISTINCT customer_id) as total_customers,
        COUNT(CASE WHEN customer_loyalty_tier = 'Loyal' THEN 1 END) as loyal_customers,
        COUNT(CASE WHEN customer_loyalty_tier = 'Regular' THEN 1 END) as regular_customers,
        COUNT(CASE WHEN customer_loyalty_tier = 'Repeat' THEN 1 END) as repeat_customers,
        COUNT(CASE WHEN customer_loyalty_tier = 'One-time' THEN 1 END) as onetime_customers,
        AVG(customer_order_count) as avg_orders_per_customer,
        AVG(customer_total_spent) as avg_spent_per_customer,
        AVG(avg_item_rating) as overall_avg_rating,
        AVG(avg_delivery_time) as overall_avg_delivery_time,
        -- Retention metrics
        COUNT(CASE WHEN days_since_last_order <= 30 THEN 1 END) * 100.0 / COUNT(*) as retention_30day_pct,
        COUNT(CASE WHEN days_since_last_order <= 60 THEN 1 END) * 100.0 / COUNT(*) as retention_60day_pct
    FROM customer_restaurant_metrics
    GROUP BY restaurant_id, restaurant_name, cuisine_type
)
SELECT 
    restaurant_name,
    cuisine_type,
    total_customers,
    loyal_customers,
    ROUND(loyal_customers * 100.0 / total_customers, 2) as loyal_customer_pct,
    regular_customers,
    ROUND(regular_customers * 100.0 / total_customers, 2) as regular_customer_pct,
    onetime_customers,
    ROUND(onetime_customers * 100.0 / total_customers, 2) as onetime_customer_pct,
    ROUND(avg_orders_per_customer, 2) as avg_orders_per_customer,
    ROUND(avg_spent_per_customer, 2) as avg_spent_per_customer,
    ROUND(overall_avg_rating, 2) as avg_rating,
    ROUND(overall_avg_delivery_time, 1) as avg_delivery_time,
    ROUND(retention_30day_pct, 2) as retention_30day_pct,
    ROUND(retention_60day_pct, 2) as retention_60day_pct,
    -- Overall satisfaction score
    CASE 
        WHEN overall_avg_rating >= 4.5 AND retention_30day_pct >= 70 THEN 'Excellent'
        WHEN overall_avg_rating >= 4.0 AND retention_30day_pct >= 60 THEN 'Good'
        WHEN overall_avg_rating >= 3.5 AND retention_30day_pct >= 50 THEN 'Average'
        ELSE 'Needs Improvement'
    END as satisfaction_grade
FROM restaurant_loyalty_summary
ORDER BY loyal_customer_pct DESC, avg_rating DESC; 