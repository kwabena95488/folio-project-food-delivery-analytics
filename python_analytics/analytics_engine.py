#!/usr/bin/env python3
"""
Food Delivery Analytics Engine
Advanced Python analytics for SQLite database
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import silhouette_score
from datetime import datetime, timedelta
import warnings
import os
import sys

warnings.filterwarnings('ignore')

class FoodDeliveryAnalytics:
    """
    Comprehensive analytics engine for food delivery data
    """
    
    def __init__(self, db_path="database/food_delivery.db"):
        """Initialize analytics engine with database connection"""
        self.db_path = db_path
        self.connection = None
        self.data_cache = {}
        
        # Ensure database exists
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database not found at {db_path}. Run setup_database.py first.")
        
        self.connect_database()
        
    def connect_database(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            print("✅ Connected to SQLite database")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def execute_query(self, query, params=None):
        """Execute SQL query and return DataFrame"""
        try:
            # Use a fresh connection for thread safety
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            if params:
                result = pd.read_sql_query(query, conn, params=params)
            else:
                result = pd.read_sql_query(query, conn)
            conn.close()
            return result
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            return pd.DataFrame()
    
    def load_sql_file(self, file_path):
        """Load and execute SQL queries from file"""
        try:
            with open(file_path, 'r') as f:
                sql_content = f.read()
            
            # Split by queries (assuming they're separated by comments or empty lines)
            queries = []
            current_query = []
            
            for line in sql_content.split('\n'):
                if line.strip().startswith('--') and current_query:
                    # New query starting
                    if current_query:
                        queries.append('\n'.join(current_query))
                        current_query = []
                elif line.strip() and not line.strip().startswith('--'):
                    current_query.append(line)
            
            # Add the last query
            if current_query:
                queries.append('\n'.join(current_query))
            
            return queries
        except Exception as e:
            print(f"❌ Failed to load SQL file {file_path}: {e}")
            return []
    
    def get_customer_analytics(self):
        """Execute customer analytics queries"""
        print("🔄 Running customer analytics...")
        
        # Customer Lifetime Value Analysis
        clv_query = """
        WITH customer_metrics AS (
            SELECT 
                c.customer_id,
                c.name,
                c.loyalty_tier,
                COUNT(o.order_id) as order_frequency,
                COALESCE(AVG(o.total_amount), 0) as avg_order_value,
                COALESCE(SUM(o.total_amount), 0) as total_spent,
                JULIANDAY('now') - JULIANDAY(MAX(o.order_date)) as days_since_last_order
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
            GROUP BY c.customer_id, c.name, c.loyalty_tier
        )
        SELECT *,
            CASE 
                WHEN order_frequency > 0 THEN order_frequency * avg_order_value * 12.0
                ELSE 0 
            END as estimated_clv,
            CASE 
                WHEN days_since_last_order IS NULL THEN 'Never Ordered'
                WHEN days_since_last_order <= 30 THEN 'Active'
                WHEN days_since_last_order <= 90 THEN 'At Risk'
                ELSE 'Churned'
            END as customer_status
        FROM customer_metrics
        """
        
        customer_data = self.execute_query(clv_query)
        self.data_cache['customer_analytics'] = customer_data
        
        print(f"✅ Loaded {len(customer_data)} customer records")
        return customer_data
    
    def get_restaurant_performance(self):
        """Execute restaurant performance analytics"""
        print("🔄 Running restaurant performance analytics...")
        
        performance_query = """
        WITH restaurant_metrics AS (
            SELECT 
                r.restaurant_id,
                r.name as restaurant_name,
                r.city,
                r.cuisine_type,
                r.rating,
                COUNT(DISTINCT o.order_id) as total_orders,
                COUNT(DISTINCT o.customer_id) as unique_customers,
                COALESCE(SUM(o.total_amount), 0) as total_revenue,
                COALESCE(AVG(o.total_amount), 0) as avg_order_value,
                COALESCE(AVG(o.delivery_time_minutes), 0) as avg_delivery_time
            FROM restaurants r
            LEFT JOIN orders o ON r.restaurant_id = o.restaurant_id AND o.status = 'completed'
            WHERE r.is_active = 1
            GROUP BY r.restaurant_id, r.name, r.city, r.cuisine_type, r.rating
        )
        SELECT *,
            CASE WHEN unique_customers > 0 THEN total_revenue / unique_customers ELSE 0 END as revenue_per_customer
        FROM restaurant_metrics
        ORDER BY total_revenue DESC
        """
        
        restaurant_data = self.execute_query(performance_query)
        self.data_cache['restaurant_performance'] = restaurant_data
        
        print(f"✅ Loaded {len(restaurant_data)} restaurant records")
        return restaurant_data
    
    def get_menu_analytics(self):
        """Execute menu item analytics"""
        print("🔄 Running menu analytics...")
        
        menu_query = """
        SELECT 
            mi.item_id,
            mi.item_name,
            mi.price,
            mi.category,
            r.name as restaurant_name,
            r.cuisine_type,
            COUNT(oi.order_item_id) as times_ordered,
            COALESCE(SUM(oi.quantity), 0) as total_quantity_sold,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_revenue,
            COALESCE(AVG(oi.item_rating), 0) as avg_rating,
            CASE 
                WHEN mi.cost_to_make > 0 THEN 
                    (mi.price - mi.cost_to_make) / mi.price * 100
                ELSE NULL 
            END as profit_margin_pct
        FROM menu_items mi
        JOIN restaurants r ON mi.restaurant_id = r.restaurant_id
        LEFT JOIN order_items oi ON mi.item_id = oi.item_id
        WHERE mi.is_available = 1
        GROUP BY mi.item_id, mi.item_name, mi.price, mi.category, r.name, r.cuisine_type
        ORDER BY total_revenue DESC
        """
        
        menu_data = self.execute_query(menu_query)
        self.data_cache['menu_analytics'] = menu_data
        
        print(f"✅ Loaded {len(menu_data)} menu item records")
        return menu_data
    
    def get_time_series_data(self):
        """Get time series data for trend analysis"""
        print("🔄 Loading time series data...")
        
        time_series_query = """
        SELECT 
            DATE(order_date) as order_date,
            strftime('%H', order_date) as hour_of_day,
            strftime('%w', order_date) as day_of_week,
            COUNT(*) as order_count,
            SUM(total_amount) as daily_revenue,
            AVG(total_amount) as avg_order_value,
            COUNT(DISTINCT customer_id) as unique_customers,
            AVG(delivery_time_minutes) as avg_delivery_time
        FROM orders
        WHERE status = 'completed' AND order_date >= date('now', '-90 days')
        GROUP BY DATE(order_date), strftime('%H', order_date), strftime('%w', order_date)
        ORDER BY order_date, hour_of_day
        """
        
        time_data = self.execute_query(time_series_query)
        time_data['order_date'] = pd.to_datetime(time_data['order_date'])
        self.data_cache['time_series'] = time_data
        
        print(f"✅ Loaded {len(time_data)} time series records")
        return time_data
    
    def customer_segmentation(self, n_clusters=4):
        """Perform customer segmentation using machine learning"""
        print(f"🔄 Performing customer segmentation with {n_clusters} clusters...")
        
        if 'customer_analytics' not in self.data_cache:
            self.get_customer_analytics()
        
        customer_data = self.data_cache['customer_analytics'].copy()
        
        # Prepare features for clustering
        features = ['order_frequency', 'avg_order_value', 'total_spent', 'days_since_last_order']
        
        # Handle missing values
        customer_data['days_since_last_order'] = customer_data['days_since_last_order'].fillna(999)
        
        # Select customers who have made at least one order
        active_customers = customer_data[customer_data['order_frequency'] > 0].copy()
        
        if len(active_customers) < n_clusters:
            print(f"⚠️ Not enough active customers for {n_clusters} clusters")
            return customer_data
        
        X = active_customers[features].values
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        active_customers['cluster'] = kmeans.fit_predict(X_scaled)
        
        # Calculate silhouette score
        silhouette_avg = silhouette_score(X_scaled, active_customers['cluster'])
        print(f"✅ Silhouette Score: {silhouette_avg:.3f}")
        
        # Define segment names based on characteristics
        cluster_summary = active_customers.groupby('cluster')[features].mean()
        
        segment_names = {}
        for cluster in range(n_clusters):
            freq = cluster_summary.loc[cluster, 'order_frequency']
            value = cluster_summary.loc[cluster, 'avg_order_value']
            recency = cluster_summary.loc[cluster, 'days_since_last_order']
            
            if freq >= cluster_summary['order_frequency'].median() and value >= cluster_summary['avg_order_value'].median():
                if recency <= 30:
                    segment_names[cluster] = 'Champions'
                else:
                    segment_names[cluster] = 'Loyal Customers'
            elif freq >= cluster_summary['order_frequency'].median():
                segment_names[cluster] = 'Frequent Customers'
            elif value >= cluster_summary['avg_order_value'].median():
                segment_names[cluster] = 'High Value Customers'
            else:
                segment_names[cluster] = 'Occasional Customers'
        
        active_customers['segment_name'] = active_customers['cluster'].map(segment_names)
        
        # Merge back with original data
        customer_data = customer_data.merge(
            active_customers[['customer_id', 'cluster', 'segment_name']], 
            on='customer_id', 
            how='left'
        )
        customer_data['segment_name'] = customer_data['segment_name'].fillna('Never Ordered')
        
        self.data_cache['customer_segments'] = customer_data
        self.data_cache['customer_analytics'] = customer_data  # Update the main cache too
        
        # Print segment summary
        segment_summary = customer_data.groupby('segment_name').agg({
            'customer_id': 'count',
            'total_spent': ['mean', 'sum'],
            'order_frequency': 'mean',
            'avg_order_value': 'mean'
        }).round(2)
        
        print("📊 Customer Segment Summary:")
        print(segment_summary)
        
        return customer_data
    
    def revenue_forecasting(self, days_ahead=7):
        """Simple revenue forecasting using linear regression"""
        print(f"🔄 Forecasting revenue for next {days_ahead} days...")
        
        if 'time_series' not in self.data_cache:
            self.get_time_series_data()
        
        time_data = self.data_cache['time_series'].copy()
        
        # Aggregate by date
        daily_revenue = time_data.groupby('order_date').agg({
            'daily_revenue': 'sum',
            'order_count': 'sum',
            'unique_customers': 'sum'
        }).reset_index()
        
        # Calculate moving averages
        daily_revenue['revenue_7day_ma'] = daily_revenue['daily_revenue'].rolling(7, min_periods=1).mean()
        daily_revenue['revenue_14day_ma'] = daily_revenue['daily_revenue'].rolling(14, min_periods=1).mean()
        
        # Prepare data for forecasting
        daily_revenue['days_since_start'] = (daily_revenue['order_date'] - daily_revenue['order_date'].min()).dt.days
        
        # Simple linear regression
        model = LinearRegression()
        X = daily_revenue[['days_since_start']].values
        y = daily_revenue['daily_revenue'].values
        
        model.fit(X, y)
        
        # Forecast future days
        last_day = daily_revenue['days_since_start'].max()
        future_days = np.array([[last_day + i] for i in range(1, days_ahead + 1)])
        future_revenue = model.predict(future_days)
        
        # Create forecast DataFrame
        future_dates = [daily_revenue['order_date'].max() + timedelta(days=i) for i in range(1, days_ahead + 1)]
        forecast_df = pd.DataFrame({
            'order_date': future_dates,
            'predicted_revenue': future_revenue,
            'days_since_start': future_days.flatten()
        })
        
        self.data_cache['revenue_forecast'] = {
            'historical': daily_revenue,
            'forecast': forecast_df,
            'model_score': model.score(X, y)
        }
        
        print(f"✅ Revenue forecast completed (R² = {model.score(X, y):.3f})")
        print(f"📈 Predicted total revenue for next {days_ahead} days: ${future_revenue.sum():,.2f}")
        
        return self.data_cache['revenue_forecast']
    
    def peak_hours_analysis(self):
        """Analyze peak hours and operational patterns"""
        print("🔄 Analyzing peak hours and patterns...")
        
        if 'time_series' not in self.data_cache:
            self.get_time_series_data()
        
        time_data = self.data_cache['time_series'].copy()
        
        # Hourly analysis
        hourly_summary = time_data.groupby('hour_of_day').agg({
            'order_count': 'sum',
            'daily_revenue': 'sum',
            'avg_order_value': 'mean',
            'unique_customers': 'sum',
            'avg_delivery_time': 'mean'
        }).reset_index()
        
        # Day of week analysis
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        daily_summary = time_data.groupby('day_of_week').agg({
            'order_count': 'sum',
            'daily_revenue': 'sum',
            'avg_order_value': 'mean',
            'unique_customers': 'sum',
            'avg_delivery_time': 'mean'
        }).reset_index()
        daily_summary['day_name'] = daily_summary['day_of_week'].map(lambda x: day_names[int(x)])
        
        self.data_cache['peak_hours'] = {
            'hourly': hourly_summary,
            'daily': daily_summary
        }
        
        # Identify peak hours
        peak_hours = hourly_summary.nlargest(3, 'order_count')['hour_of_day'].values
        peak_days = daily_summary.nlargest(3, 'order_count')['day_name'].values
        
        print(f"🕐 Peak hours: {', '.join([f'{h}:00' for h in peak_hours])}")
        print(f"📅 Peak days: {', '.join(peak_days)}")
        
        return self.data_cache['peak_hours']
    
    def generate_business_insights(self):
        """Generate automated business insights"""
        print("🔄 Generating business insights...")
        
        insights = []
        
        # Customer insights
        if 'customer_analytics' in self.data_cache:
            customer_data = self.data_cache['customer_analytics']
            avg_clv = customer_data['estimated_clv'].mean()
            top_customer_value = customer_data['total_spent'].max()
            active_customers = len(customer_data[customer_data['customer_status'] == 'Active'])
            at_risk_customers = len(customer_data[customer_data['customer_status'] == 'At Risk'])
            
            insights.extend([
                f"💰 Average customer lifetime value: ${avg_clv:.2f}",
                f"🌟 Highest spending customer: ${top_customer_value:.2f}",
                f"✅ Active customers: {active_customers}",
                f"⚠️ At-risk customers: {at_risk_customers}"
            ])
        
        # Restaurant insights
        if 'restaurant_performance' in self.data_cache:
            restaurant_data = self.data_cache['restaurant_performance']
            top_restaurant = restaurant_data.iloc[0]
            avg_rating = restaurant_data['rating'].mean()
            
            insights.extend([
                f"🏆 Top performing restaurant: {top_restaurant['restaurant_name']} (${top_restaurant['total_revenue']:.2f})",
                f"⭐ Average restaurant rating: {avg_rating:.2f}"
            ])
        
        # Peak hours insights
        if 'peak_hours' in self.data_cache:
            hourly_data = self.data_cache['peak_hours']['hourly']
            peak_hour = hourly_data.loc[hourly_data['order_count'].idxmax(), 'hour_of_day']
            insights.append(f"⏰ Peak ordering hour: {peak_hour}:00")
        
        # Menu insights
        if 'menu_analytics' in self.data_cache:
            menu_data = self.data_cache['menu_analytics']
            top_item = menu_data.iloc[0]
            insights.append(f"🍕 Best selling item: {top_item['item_name']} (${top_item['total_revenue']:.2f} revenue)")
        
        self.data_cache['insights'] = insights
        
        print("💡 Key Business Insights:")
        for insight in insights:
            print(f"  {insight}")
        
        return insights
    
    def create_summary_dashboard(self):
        """Create a comprehensive summary dashboard"""
        print("🔄 Creating summary dashboard...")
        
        # Load all data if not already cached
        if 'customer_analytics' not in self.data_cache:
            self.get_customer_analytics()
        if 'restaurant_performance' not in self.data_cache:
            self.get_restaurant_performance()
        if 'menu_analytics' not in self.data_cache:
            self.get_menu_analytics()
        if 'time_series' not in self.data_cache:
            self.get_time_series_data()
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                'Customer Status Distribution',
                'Daily Revenue Trend',
                'Top Restaurants by Revenue',
                'Peak Hours Analysis',
                'Menu Category Performance',
                'Customer Lifetime Value Distribution'
            ],
            specs=[
                [{"type": "pie"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "histogram"}]
            ]
        )
        
        # Customer status pie chart
        customer_data = self.data_cache['customer_analytics']
        status_counts = customer_data['customer_status'].value_counts()
        fig.add_trace(
            go.Pie(labels=status_counts.index, values=status_counts.values, name="Customer Status"),
            row=1, col=1
        )
        
        # Daily revenue trend
        time_data = self.data_cache['time_series']
        daily_revenue = time_data.groupby('order_date')['daily_revenue'].sum().reset_index()
        fig.add_trace(
            go.Scatter(
                x=daily_revenue['order_date'], 
                y=daily_revenue['daily_revenue'],
                mode='lines+markers',
                name='Daily Revenue'
            ),
            row=1, col=2
        )
        
        # Top restaurants
        restaurant_data = self.data_cache['restaurant_performance'].head(10)
        fig.add_trace(
            go.Bar(
                x=restaurant_data['total_revenue'], 
                y=restaurant_data['restaurant_name'],
                orientation='h',
                name="Restaurant Revenue"
            ),
            row=2, col=1
        )
        
        # Peak hours
        hourly_data = time_data.groupby('hour_of_day')['order_count'].sum().reset_index()
        fig.add_trace(
            go.Bar(x=hourly_data['hour_of_day'], y=hourly_data['order_count'], name="Orders by Hour"),
            row=2, col=2
        )
        
        # Menu categories
        menu_data = self.data_cache['menu_analytics']
        category_revenue = menu_data.groupby('category')['total_revenue'].sum().sort_values(ascending=False).head(10)
        fig.add_trace(
            go.Bar(x=category_revenue.index, y=category_revenue.values, name="Category Revenue"),
            row=3, col=1
        )
        
        # CLV distribution
        clv_data = customer_data[customer_data['estimated_clv'] > 0]['estimated_clv']
        fig.add_trace(
            go.Histogram(x=clv_data, nbinsx=20, name="CLV Distribution"),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text="🍽️ Food Delivery Analytics Dashboard",
            showlegend=False
        )
        
        return fig
    
    def export_analysis_results(self, output_dir="outputs"):
        """Export analysis results to files"""
        print(f"🔄 Exporting analysis results to {output_dir}/...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Export cached data
        for data_name, data in self.data_cache.items():
            if isinstance(data, pd.DataFrame):
                file_path = os.path.join(output_dir, f"{data_name}.csv")
                data.to_csv(file_path, index=False)
                print(f"✅ Exported {data_name} to {file_path}")
        
        # Export insights
        if 'insights' in self.data_cache:
            insights_path = os.path.join(output_dir, "business_insights.txt")
            with open(insights_path, 'w') as f:
                f.write("FOOD DELIVERY ANALYTICS INSIGHTS\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for insight in self.data_cache['insights']:
                    f.write(f"{insight}\n")
            print(f"✅ Exported insights to {insights_path}")
        
        print("🎉 Export completed!")
    
    def run_complete_analysis(self):
        """Run the complete analytics pipeline"""
        print("🚀 Starting complete food delivery analytics pipeline...")
        
        try:
            # Load all data
            self.get_customer_analytics()
            self.get_restaurant_performance()
            self.get_menu_analytics()
            self.get_time_series_data()
            
            # Perform advanced analytics
            self.customer_segmentation()
            self.revenue_forecasting()
            self.peak_hours_analysis()
            
            # Generate insights
            self.generate_business_insights()
            
            # Create dashboard
            dashboard = self.create_summary_dashboard()
            
            # Export results
            self.export_analysis_results()
            
            print("🎉 Complete analytics pipeline finished successfully!")
            
            return {
                'dashboard': dashboard,
                'insights': self.data_cache.get('insights', []),
                'data_cache': self.data_cache
            }
            
        except Exception as e:
            print(f"❌ Analytics pipeline failed: {e}")
            raise
    
    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")

def main():
    """Main execution function"""
    print("🍽️ Food Delivery Analytics Engine")
    print("=" * 40)
    
    # Initialize analytics engine
    try:
        analytics = FoodDeliveryAnalytics()
        
        # Run complete analysis
        results = analytics.run_complete_analysis()
        
        # Display dashboard
        if results['dashboard']:
            results['dashboard'].show()
        
        # Close connection
        analytics.close_connection()
        
    except Exception as e:
        print(f"❌ Analytics failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 