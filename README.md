# 🍽️ Food Delivery Analytics - Data Engineering Portfolio

## 🎯 Project Overview

This project demonstrates advanced **data engineering** and **analytics** capabilities through a comprehensive food delivery business intelligence system. Built with **SQLite**, **SQL**, and **Python**, it showcases the complete data lifecycle from database design to actionable business insights.

### 🚀 Key Features

- ⚡ **High-Performance SQLite Database** with optimized schema and strategic indexing
- 🔍 **Advanced SQL Analytics** featuring window functions, CTEs, and complex aggregations  
- 🐍 **Python Data Pipeline** for automated processing and machine learning
- 📊 **Interactive Dashboards** with real-time business intelligence
- 🤖 **Machine Learning** customer segmentation and revenue forecasting
- 📈 **Business Intelligence** with automated insights generation

## 🛠️ Technical Stack

- **Database**: SQLite 3.x with optimized schema design
- **SQL**: Advanced analytical queries with window functions and CTEs
- **Python**: pandas, scikit-learn, plotly, matplotlib, seaborn
- **Analytics**: Customer segmentation, revenue forecasting, RFM analysis
- **Visualization**: Interactive dashboards and business intelligence reports

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation & Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd folio-project-restaurant-food-delivery
```

2. **Run the complete setup**
```bash
python run_setup.py
```

This will:
- Install all required dependencies
- Create and populate the SQLite database with realistic sample data
- Run the complete analytics pipeline
- Generate interactive dashboards and export results

### Manual Setup (Alternative)

```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
python database/setup_database.py

# Run analytics
python python_analytics/analytics_engine.py

# Launch interactive dashboard
python launch_dashboard.py
```

## 🌐 Interactive Dashboard

The project includes a comprehensive **interactive web dashboard** built with Dash and Plotly:

### Dashboard Features
- **📊 Real-time KPI Cards**: Total revenue, orders, active customers, average order value
- **👥 Customer Analytics**: Segmentation, lifetime value, behavior patterns
- **🏪 Restaurant Performance**: Rankings, revenue comparison, delivery efficiency
- **🍕 Menu Analytics**: Category performance, top items, profitability analysis
- **📈 Revenue Trends**: Forecasting, monthly trends, day-of-week patterns
- **⏰ Operational Insights**: Peak hours, order status, delivery times, payment methods

### Launching the Dashboard

```bash
# Quick launch (recommended)
python launch_dashboard.py

# Direct launch
python python_analytics/interactive_dashboard.py
```

The dashboard will be available at: **http://localhost:8050**

> **✅ Status**: Dashboard is fully functional with thread-safe SQLite connections

### Dashboard Tabs
1. **📊 Overview**: High-level business metrics and trends
2. **👥 Customer Analytics**: Deep dive into customer behavior and segmentation
3. **🏪 Restaurant Performance**: Restaurant comparison and efficiency metrics
4. **🍕 Menu Analytics**: Menu optimization and item performance
5. **📈 Revenue Trends**: Financial forecasting and trend analysis
6. **⏰ Operational Insights**: Operational efficiency and peak hour analysis

## 📊 Analytics Capabilities

### Customer Intelligence
- **Customer Lifetime Value (CLV)** calculation and segmentation
- **RFM Analysis** (Recency, Frequency, Monetary) for customer classification
- **Churn Prediction** indicators and at-risk customer identification
- **Customer Journey** analysis and retention metrics
- **Cohort Analysis** for understanding customer behavior over time

### Restaurant Performance
- **Multi-dimensional Performance Ranking** with weighted scoring
- **Revenue Trends** analysis with moving averages and growth metrics
- **Peak Hours Analysis** and operational efficiency metrics
- **Menu Performance** optimization and profitability analysis
- **Customer Satisfaction** and loyalty tracking

### Business Intelligence
- **Revenue Forecasting** using machine learning models
- **Operational Metrics** for delivery efficiency and peak hour optimization
- **Menu Optimization** recommendations based on performance data
- **Market Analysis** across different cuisines and locations

## 📁 Project Structure

```
folio-project-restaurant-food-delivery/
├── 📄 README.md                          # This file
├── 📄 PROJECT_OVERVIEW.md                # Executive summary
├── 📄 PROJECT_ENHANCEMENT_PLAN.md        # Detailed enhancement plan
├── 📄 requirements.txt                   # Python dependencies
├── 📄 run_setup.py                       # One-click setup script
├── 
├── 📁 database/                          # Database layer
│   ├── sqlite_schema.sql                 # Optimized SQLite schema
│   ├── setup_database.py                 # Database setup and data generation
│   └── food_delivery.db                  # SQLite database (generated)
│
├── 📁 sql_analytics/                     # Advanced SQL queries
│   ├── customer_analytics.sql            # Customer intelligence queries
│   └── restaurant_performance.sql        # Restaurant analysis queries
│
├── 📁 python_analytics/                  # Python processing layer
│   └── analytics_engine.py               # Main analytics engine
│
├── 📁 report/                            # Comprehensive project reports
│   └── project_analysis_report.md        # Detailed analytics insights and findings
│
└── 📁 outputs/                           # Generated results (created during execution)
    ├── 📁 charts/                        # Generated analytical charts and visualizations
    │   ├── newplot.png                   # Customer segmentation charts
    │   ├── newplot-2.png                 # Revenue trend visualizations
    │   ├── newplot-3.png                 # Restaurant performance charts
    │   └── ... (additional chart files)
    │
    ├── 📁 dashboards/                    # Interactive dashboard screenshots
    │   ├── Screenshot 2025-05-27 at 7.23.37 AM.png  # Overview dashboard
    │   ├── Screenshot 2025-05-27 at 7.23.54 AM.png  # Customer analytics view
    │   ├── Screenshot 2025-05-27 at 7.24.02 AM.png  # Restaurant performance view
    │   ├── Screenshot 2025-05-27 at 7.24.06 AM.png  # Menu analytics view
    │   ├── Screenshot 2025-05-27 at 7.24.18 AM.png  # Revenue trends view
    │   └── Screenshot 2025-05-27 at 7.24.33 AM.png  # Operational insights view
    │
    ├── customer_analytics.csv            # Customer analysis results
    ├── customer_segments.csv             # ML-based customer segmentation
    ├── restaurant_performance.csv        # Restaurant metrics
    ├── menu_analytics.csv                # Menu performance data
    ├── time_series.csv                   # Time-series data for trend analysis
    └── business_insights.txt             # Automated insights report
```

## 🔍 Advanced SQL Showcase

The project demonstrates sophisticated SQL techniques including:

### Window Functions & Analytics
```sql
-- Customer Lifetime Value with Ranking
SELECT customer_id, total_spent,
       ROW_NUMBER() OVER (ORDER BY total_spent DESC) as value_rank,
       NTILE(5) OVER (ORDER BY total_spent) as value_quintile
FROM customer_metrics;
```

### Common Table Expressions (CTEs)
```sql
-- Multi-level Customer Segmentation
WITH customer_metrics AS (...),
     rfm_scores AS (...),
     final_segments AS (...)
SELECT * FROM final_segments;
```

### Complex Aggregations
```sql
-- Restaurant Performance with Multiple Metrics
SELECT restaurant_name,
       COUNT(DISTINCT order_id) as total_orders,
       AVG(delivery_time_minutes) as avg_delivery_time,
       SUM(total_amount) / COUNT(DISTINCT customer_id) as revenue_per_customer
FROM restaurant_orders_view;
```

## 🐍 Python Analytics Features

### Machine Learning Integration
- **K-Means Clustering** for customer segmentation
- **Linear Regression** for revenue forecasting
- **Silhouette Analysis** for optimal cluster validation

### Data Processing Pipeline
- **Automated ETL** processes for data extraction and transformation
- **Data Quality** validation and consistency checks
- **Performance Monitoring** with execution time tracking

### Interactive Visualizations
- **Plotly Dashboards** with multiple chart types
- **Business Intelligence** reports with automated insights
- **Export Capabilities** for further analysis

## 📈 Sample Insights Generated

The system automatically generates insights such as:

- 💰 **Customer Analysis**: "Top 20% of customers generate 60% of total revenue"
- 🏆 **Restaurant Performance**: "Italiano Pizza leads with $45K revenue and 4.8 rating"
- ⏰ **Operational Efficiency**: "Peak ordering hours are 12:00-13:00 and 19:00-20:00"
- 🍕 **Menu Optimization**: "Margherita Pizza and Pad Thai are star performers"
- 📊 **Business Intelligence**: "15% of customers are at risk of churning"

## 🎯 Portfolio Value

This project demonstrates:

### Technical Skills
- ✅ **Advanced SQL** with window functions, CTEs, and complex joins
- ✅ **Database Design** with optimization and performance tuning
- ✅ **Python Programming** for data analysis and machine learning
- ✅ **Data Visualization** with interactive dashboards
- ✅ **Business Intelligence** with automated insight generation

### Real-World Application
- 📊 **Scalable Architecture** handling large datasets efficiently
- 🔄 **Automated Workflows** reducing manual analysis time
- 💡 **Actionable Insights** directly impacting business decisions
- 📈 **Performance Monitoring** with continuous optimization

## 🔧 Customization

The system is designed to be easily customizable:

- **Database Schema**: Modify `database/sqlite_schema.sql` for different data structures
- **Analytics Queries**: Add new SQL queries in the `sql_analytics/` directory
- **Python Analytics**: Extend the `analytics_engine.py` with new analysis methods
- **Visualizations**: Customize dashboards in the analytics engine

## 📚 Learning Outcomes

This project showcases proficiency in:

1. **Database Engineering**: Schema design, indexing, query optimization
2. **Advanced SQL**: Window functions, CTEs, complex analytical queries
3. **Python Data Science**: pandas, scikit-learn, data visualization
4. **Business Intelligence**: KPI development, automated insights, forecasting
5. **Software Engineering**: Code organization, documentation, testing

---

**This project serves as a comprehensive demonstration of data engineering capabilities, combining technical expertise with business acumen in the food delivery analytics domain.**

Project Overview:

The data analytics project revolves around a sophisticated restaurant management system, designed to capture and process vast amounts of operational data. The system comprises interconnected databases that store information about customers, orders, menu items, restaurants, and revenue. Through a series of carefully crafted SQL queries, the project mines this data to unearth meaningful patterns, trends, and relationships, providing businesses with actionable insights.

Customer Segmentation:

One of the key benefits of this project is customer segmentation. By analyzing data on customer orders, preferences, and spending habits, the system categorizes customers into distinct segments. Each segment represents a group of customers with similar characteristics, such as frequent diners, occasional visitors, or high spenders. This segmentation enables restaurants to personalize marketing strategies, promotions, and loyalty programs, fostering deeper connections with customers and driving repeat business.

Menu Optimization:

The project delves into the realm of menu optimization by identifying popular menu items for each restaurant. Through an analysis of order data, the system pinpoints best-selling dishes and customer favorites. Armed with this knowledge, restaurant owners can tailor their menus to suit customer preferences, remove underperforming items, and introduce new, appealing dishes. Such optimization not only enhances customer satisfaction but also streamlines inventory management and reduces food wastage, leading to cost-effectiveness.

Revenue Maximization:

The data analytics project serves as a beacon for revenue maximization. By analyzing sales and revenue data, the system highlights top-performing restaurants and identifies those with growth potential. Organizations can channel their efforts and resources into high-revenue-generating outlets, replicating successful strategies across other locations. Additionally, the project analyzes revenue trends for specific time periods, providing valuable insights for revenue forecasting and strategic planning.

Operational Efficiency:

The project enhances operational efficiency by analyzing the number of orders placed during specific time periods. This data enables restaurants to optimize staffing levels and resource allocation, ensuring seamless order processing and reducing wait times. Enhanced efficiency translates to improved customer experiences and higher customer satisfaction, resulting in increased customer retention and positive word-of-mouth.

Market Insights and Business Strategy:

With its data-driven approach, the project empowers organizations with invaluable market insights. Revenue trends, popular menu items, and customer preferences become key indicators for assessing market trends and formulating effective business strategies. Armed with this knowledge, businesses can make informed decisions about expansion, pricing, marketing, and other critical aspects of their operations.

Customer Retention Strategies:

Another significant advantage of the project lies in customer retention strategies. By identifying customers who have not placed orders in the current year, restaurants can implement targeted marketing campaigns to re-engage dormant customers. Personalized offers, discounts, and incentives can be extended to foster long-term relationships and loyalty.

Conclusion:

By analyzing critical data related to customers, orders, menu items, and revenue, this project enables organizations to optimize their operations, enhance customer experiences, and drive growth in a competitive industry. As data analytics continues to evolve and become more accessible, its role in driving business success will only become more pronounced. Embracing data-driven insights is no longer a choice but a necessity for organizations seeking to thrive in the dynamic landscape of the 21st century.