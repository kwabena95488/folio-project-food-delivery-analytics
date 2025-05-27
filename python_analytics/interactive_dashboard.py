#!/usr/bin/env python3
"""
Interactive Food Delivery Analytics Dashboard
Built with Dash for comprehensive business intelligence
"""

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
from analytics_engine import FoodDeliveryAnalytics
import dash_bootstrap_components as dbc

class FoodDeliveryDashboard:
    def __init__(self, db_path="database/food_delivery.db"):
        """Initialize the dashboard with database connection"""
        self.db_path = db_path
        self.analytics = FoodDeliveryAnalytics(db_path)
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.setup_layout()
        self.setup_callbacks()
        
    def load_data(self):
        """Load all necessary data for the dashboard"""
        print("🔄 Loading data for dashboard...")
        
        # Create a new analytics instance for thread safety
        thread_analytics = FoodDeliveryAnalytics(self.db_path)
        
        # Load analytics data
        thread_analytics.get_customer_analytics()
        thread_analytics.get_restaurant_performance()
        thread_analytics.get_menu_analytics()
        thread_analytics.get_time_series_data()
        
        # Perform advanced analytics
        thread_analytics.customer_segmentation()
        thread_analytics.revenue_forecasting()
        thread_analytics.peak_hours_analysis()
        
        # Cache the data
        self.analytics.data_cache = thread_analytics.data_cache
        
        # Close the thread connection
        thread_analytics.close_connection()
        
        print("✅ Data loaded successfully")
        
    def create_kpi_cards(self):
        """Create KPI summary cards"""
        try:
            # Get summary statistics with thread-safe connection
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            
            # Total revenue
            total_revenue = pd.read_sql("""
                SELECT SUM(total_amount) as total_revenue 
                FROM orders WHERE status = 'completed'
            """, conn).iloc[0]['total_revenue']
            
            # Total orders
            total_orders = pd.read_sql("""
                SELECT COUNT(*) as total_orders 
                FROM orders WHERE status = 'completed'
            """, conn).iloc[0]['total_orders']
            
            # Active customers
            active_customers = pd.read_sql("""
                SELECT COUNT(DISTINCT customer_id) as active_customers
                FROM orders 
                WHERE status = 'completed' 
                AND order_date >= date('now', '-30 days')
            """, conn).iloc[0]['active_customers']
            
            # Average order value
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            
            conn.close()
        except Exception as e:
            print(f"❌ KPI calculation failed: {e}")
            # Fallback values
            total_revenue = 0
            total_orders = 0
            active_customers = 0
            avg_order_value = 0
        
        return dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"${total_revenue:,.2f}", className="card-title text-primary"),
                        html.P("Total Revenue", className="card-text"),
                    ])
                ], className="mb-3")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{total_orders:,}", className="card-title text-success"),
                        html.P("Total Orders", className="card-text"),
                    ])
                ], className="mb-3")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{active_customers:,}", className="card-title text-info"),
                        html.P("Active Customers", className="card-text"),
                    ])
                ], className="mb-3")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"${avg_order_value:.2f}", className="card-title text-warning"),
                        html.P("Avg Order Value", className="card-text"),
                    ])
                ], className="mb-3")
            ], width=3),
        ])
    
    def setup_layout(self):
        """Setup the dashboard layout"""
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("🍽️ Food Delivery Analytics Dashboard", 
                           className="text-center mb-4 text-primary"),
                    html.Hr(),
                ])
            ]),
            
            # KPI Cards
            html.Div(id="kpi-cards"),
            
            # Main Content Tabs
            dbc.Tabs([
                dbc.Tab(label="📊 Overview", tab_id="overview"),
                dbc.Tab(label="👥 Customer Analytics", tab_id="customers"),
                dbc.Tab(label="🏪 Restaurant Performance", tab_id="restaurants"),
                dbc.Tab(label="🍕 Menu Analytics", tab_id="menu"),
                dbc.Tab(label="📈 Revenue Trends", tab_id="revenue"),
                dbc.Tab(label="⏰ Operational Insights", tab_id="operations"),
            ], id="main-tabs", active_tab="overview"),
            
            # Tab Content
            html.Div(id="tab-content", className="mt-4"),
            
            # Auto-refresh interval
            dcc.Interval(
                id='interval-component',
                interval=30*1000,  # Update every 30 seconds
                n_intervals=0
            )
            
        ], fluid=True)
    
    def create_overview_tab(self):
        """Create overview tab content"""
        return dbc.Row([
            dbc.Col([
                dcc.Graph(id="revenue-trend-overview"),
            ], width=6),
            dbc.Col([
                dcc.Graph(id="customer-status-pie"),
            ], width=6),
            dbc.Col([
                dcc.Graph(id="top-restaurants-overview"),
            ], width=6),
            dbc.Col([
                dcc.Graph(id="peak-hours-overview"),
            ], width=6),
        ])
    
    def create_customer_tab(self):
        """Create customer analytics tab content"""
        return dbc.Row([
            dbc.Col([
                html.H4("Customer Segmentation"),
                dcc.Graph(id="customer-segmentation"),
            ], width=6),
            dbc.Col([
                html.H4("Customer Lifetime Value"),
                dcc.Graph(id="customer-clv"),
            ], width=6),
            dbc.Col([
                html.H4("Customer Behavior Patterns"),
                dcc.Graph(id="customer-behavior"),
            ], width=12),
        ])
    
    def create_restaurant_tab(self):
        """Create restaurant performance tab content"""
        return dbc.Row([
            dbc.Col([
                html.H4("Restaurant Performance Ranking"),
                dcc.Graph(id="restaurant-ranking"),
            ], width=12),
            dbc.Col([
                html.H4("Revenue by Restaurant"),
                dcc.Graph(id="restaurant-revenue"),
            ], width=6),
            dbc.Col([
                html.H4("Delivery Efficiency"),
                dcc.Graph(id="delivery-efficiency"),
            ], width=6),
        ])
    
    def create_menu_tab(self):
        """Create menu analytics tab content"""
        return dbc.Row([
            dbc.Col([
                html.H4("Menu Category Performance"),
                dcc.Graph(id="menu-categories"),
            ], width=6),
            dbc.Col([
                html.H4("Top Performing Items"),
                dcc.Graph(id="top-items"),
            ], width=6),
            dbc.Col([
                html.H4("Item Profitability Analysis"),
                dcc.Graph(id="item-profitability"),
            ], width=12),
        ])
    
    def create_revenue_tab(self):
        """Create revenue trends tab content"""
        return dbc.Row([
            dbc.Col([
                html.H4("Revenue Forecasting"),
                dcc.Graph(id="revenue-forecast"),
            ], width=12),
            dbc.Col([
                html.H4("Monthly Revenue Trends"),
                dcc.Graph(id="monthly-revenue"),
            ], width=6),
            dbc.Col([
                html.H4("Revenue by Day of Week"),
                dcc.Graph(id="dow-revenue"),
            ], width=6),
        ])
    
    def create_operations_tab(self):
        """Create operational insights tab content"""
        return dbc.Row([
            dbc.Col([
                html.H4("Peak Hours Analysis"),
                dcc.Graph(id="peak-hours-detailed"),
            ], width=6),
            dbc.Col([
                html.H4("Order Status Distribution"),
                dcc.Graph(id="order-status"),
            ], width=6),
            dbc.Col([
                html.H4("Delivery Time Analysis"),
                dcc.Graph(id="delivery-times"),
            ], width=6),
            dbc.Col([
                html.H4("Payment Method Preferences"),
                dcc.Graph(id="payment-methods"),
            ], width=6),
        ])
    
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            Output('kpi-cards', 'children'),
            Input('interval-component', 'n_intervals')
        )
        def update_kpi_cards(n):
            return self.create_kpi_cards()
        
        @self.app.callback(
            Output('tab-content', 'children'),
            Input('main-tabs', 'active_tab')
        )
        def update_tab_content(active_tab):
            if active_tab == "overview":
                return self.create_overview_tab()
            elif active_tab == "customers":
                return self.create_customer_tab()
            elif active_tab == "restaurants":
                return self.create_restaurant_tab()
            elif active_tab == "menu":
                return self.create_menu_tab()
            elif active_tab == "revenue":
                return self.create_revenue_tab()
            elif active_tab == "operations":
                return self.create_operations_tab()
            return html.Div("Select a tab to view content")
        
        # Overview tab callbacks
        @self.app.callback(
            [Output('revenue-trend-overview', 'figure'),
             Output('customer-status-pie', 'figure'),
             Output('top-restaurants-overview', 'figure'),
             Output('peak-hours-overview', 'figure')],
            Input('main-tabs', 'active_tab')
        )
        def update_overview_charts(active_tab):
            if active_tab != "overview":
                return {}, {}, {}, {}
            
            # Load data
            self.load_data()
            
            # Revenue trend
            time_data = self.analytics.data_cache.get('time_series', pd.DataFrame())
            if not time_data.empty:
                daily_revenue = time_data.groupby('order_date')['daily_revenue'].sum().reset_index()
                revenue_fig = px.line(daily_revenue, x='order_date', y='daily_revenue',
                                    title='Daily Revenue Trend')
            else:
                revenue_fig = {}
            
            # Customer status
            customer_data = self.analytics.data_cache.get('customer_analytics', pd.DataFrame())
            if not customer_data.empty:
                status_counts = customer_data['customer_status'].value_counts()
                status_fig = px.pie(values=status_counts.values, names=status_counts.index,
                                  title='Customer Status Distribution')
            else:
                status_fig = {}
            
            # Top restaurants
            restaurant_data = self.analytics.data_cache.get('restaurant_performance', pd.DataFrame())
            if not restaurant_data.empty:
                top_restaurants = restaurant_data.head(10)
                restaurant_fig = px.bar(top_restaurants, x='total_revenue', y='restaurant_name',
                                      orientation='h', title='Top 10 Restaurants by Revenue')
            else:
                restaurant_fig = {}
            
            # Peak hours
            if not time_data.empty:
                hourly_data = time_data.groupby('hour_of_day')['order_count'].sum().reset_index()
                peak_fig = px.bar(hourly_data, x='hour_of_day', y='order_count',
                                title='Orders by Hour of Day')
            else:
                peak_fig = {}
            
            return revenue_fig, status_fig, restaurant_fig, peak_fig
        
        # Customer analytics callbacks
        @self.app.callback(
            [Output('customer-segmentation', 'figure'),
             Output('customer-clv', 'figure'),
             Output('customer-behavior', 'figure')],
            Input('main-tabs', 'active_tab')
        )
        def update_customer_charts(active_tab):
            if active_tab != "customers":
                return {}, {}, {}
            
            self.load_data()
            customer_data = self.analytics.data_cache.get('customer_analytics', pd.DataFrame())
            
            if customer_data.empty:
                return {}, {}, {}
            
            # Customer segmentation
            if 'cluster' in customer_data.columns:
                seg_fig = px.scatter(customer_data, x='order_frequency', y='avg_order_value',
                                   color='cluster', title='Customer Segmentation',
                                   labels={'order_frequency': 'Order Frequency', 
                                          'avg_order_value': 'Average Order Value'})
            else:
                # Fallback segmentation by customer status
                seg_fig = px.scatter(customer_data, x='order_frequency', y='avg_order_value',
                                   color='customer_status', title='Customer Segmentation by Status',
                                   labels={'order_frequency': 'Order Frequency', 
                                          'avg_order_value': 'Average Order Value'})
            
            # CLV distribution
            clv_data = customer_data[customer_data['estimated_clv'] > 0]
            clv_fig = px.histogram(clv_data, x='estimated_clv', nbins=20,
                                 title='Customer Lifetime Value Distribution')
            
            # Customer behavior (orders over time)
            behavior_fig = px.box(customer_data, y='order_frequency',
                                title='Customer Order Frequency Distribution')
            
            return seg_fig, clv_fig, behavior_fig
        
        # Restaurant performance callbacks
        @self.app.callback(
            [Output('restaurant-ranking', 'figure'),
             Output('restaurant-revenue', 'figure'),
             Output('delivery-efficiency', 'figure')],
            Input('main-tabs', 'active_tab')
        )
        def update_restaurant_charts(active_tab):
            if active_tab != "restaurants":
                return {}, {}, {}
            
            self.load_data()
            restaurant_data = self.analytics.data_cache.get('restaurant_performance', pd.DataFrame())
            
            if restaurant_data.empty:
                return {}, {}, {}
            
            # Restaurant ranking
            ranking_fig = px.scatter(restaurant_data, x='total_orders', y='total_revenue',
                                   size='avg_order_value', hover_name='restaurant_name',
                                   title='Restaurant Performance Matrix')
            
            # Revenue by restaurant
            top_revenue = restaurant_data.head(15)
            revenue_fig = px.bar(top_revenue, x='restaurant_name', y='total_revenue',
                               title='Top 15 Restaurants by Revenue')
            revenue_fig.update_xaxes(tickangle=45)
            
            # Delivery efficiency
            if 'avg_delivery_time' in restaurant_data.columns:
                efficiency_fig = px.scatter(restaurant_data, x='avg_delivery_time', y='total_orders',
                                          hover_name='restaurant_name',
                                          title='Delivery Time vs Order Volume')
            else:
                efficiency_fig = {}
            
            return ranking_fig, revenue_fig, efficiency_fig
        
        # Menu analytics callbacks
        @self.app.callback(
            [Output('menu-categories', 'figure'),
             Output('top-items', 'figure'),
             Output('item-profitability', 'figure')],
            Input('main-tabs', 'active_tab')
        )
        def update_menu_charts(active_tab):
            if active_tab != "menu":
                return {}, {}, {}
            
            self.load_data()
            menu_data = self.analytics.data_cache.get('menu_analytics', pd.DataFrame())
            
            if menu_data.empty:
                return {}, {}, {}
            
            # Category performance
            category_revenue = menu_data.groupby('category')['total_revenue'].sum().sort_values(ascending=False)
            category_fig = px.bar(x=category_revenue.index, y=category_revenue.values,
                                title='Revenue by Menu Category')
            
            # Top items
            top_items = menu_data.nlargest(20, 'total_revenue')
            items_fig = px.bar(top_items, x='item_name', y='total_revenue',
                             title='Top 20 Menu Items by Revenue')
            items_fig.update_xaxes(tickangle=45)
            
            # Profitability analysis
            if 'profit_margin_pct' in menu_data.columns:
                profit_fig = px.scatter(menu_data, x='total_quantity_sold', y='profit_margin_pct',
                                      size='total_revenue', hover_name='item_name',
                                      title='Item Profitability vs Popularity')
            else:
                profit_fig = px.scatter(menu_data, x='total_quantity_sold', y='total_revenue',
                                      hover_name='item_name',
                                      title='Item Revenue vs Quantity Sold')
            
            return category_fig, items_fig, profit_fig
        
        # Revenue trends callbacks
        @self.app.callback(
            [Output('revenue-forecast', 'figure'),
             Output('monthly-revenue', 'figure'),
             Output('dow-revenue', 'figure')],
            Input('main-tabs', 'active_tab')
        )
        def update_revenue_charts(active_tab):
            if active_tab != "revenue":
                return {}, {}, {}
            
            self.load_data()
            
            # Revenue forecast
            if 'revenue_forecast' in self.analytics.data_cache:
                forecast_data = self.analytics.data_cache['revenue_forecast']
                historical = forecast_data['historical']
                forecast = forecast_data['forecast']
                
                forecast_fig = go.Figure()
                forecast_fig.add_trace(go.Scatter(
                    x=historical['order_date'], 
                    y=historical['daily_revenue'],
                    mode='lines',
                    name='Historical Revenue',
                    line=dict(color='blue')
                ))
                forecast_fig.add_trace(go.Scatter(
                    x=forecast['order_date'], 
                    y=forecast['predicted_revenue'],
                    mode='lines+markers',
                    name='Forecast',
                    line=dict(color='red', dash='dash')
                ))
                forecast_fig.update_layout(title='Revenue Forecasting')
            else:
                forecast_fig = {}
            
            # Monthly revenue trends
            time_data = self.analytics.data_cache.get('time_series', pd.DataFrame())
            if not time_data.empty:
                monthly_revenue = time_data.groupby(time_data['order_date'].dt.to_period('M'))['daily_revenue'].sum().reset_index()
                monthly_revenue['order_date'] = monthly_revenue['order_date'].astype(str)
                monthly_fig = px.bar(monthly_revenue, x='order_date', y='daily_revenue',
                                   title='Monthly Revenue Trends')
            else:
                monthly_fig = {}
            
            # Day of week revenue
            if not time_data.empty:
                day_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                dow_revenue = time_data.groupby('day_of_week')['daily_revenue'].sum().reset_index()
                dow_revenue['day_name'] = dow_revenue['day_of_week'].astype(int).map(lambda x: day_names[x])
                dow_fig = px.bar(dow_revenue, x='day_name', y='daily_revenue',
                               title='Revenue by Day of Week')
            else:
                dow_fig = {}
            
            return forecast_fig, monthly_fig, dow_fig
        
        # Operational insights callbacks
        @self.app.callback(
            [Output('peak-hours-detailed', 'figure'),
             Output('order-status', 'figure'),
             Output('delivery-times', 'figure'),
             Output('payment-methods', 'figure')],
            Input('main-tabs', 'active_tab')
        )
        def update_operations_charts(active_tab):
            if active_tab != "operations":
                return {}, {}, {}, {}
            
            self.load_data()
            
            # Peak hours detailed
            if 'peak_hours' in self.analytics.data_cache:
                hourly_data = self.analytics.data_cache['peak_hours']['hourly']
                peak_fig = px.bar(hourly_data, x='hour_of_day', y='order_count',
                                title='Peak Hours Analysis')
            else:
                peak_fig = {}
            
            # Order status distribution
            try:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                status_data = pd.read_sql("""
                    SELECT status, COUNT(*) as count 
                    FROM orders 
                    GROUP BY status
                """, conn)
                conn.close()
                status_fig = px.pie(status_data, values='count', names='status',
                                  title='Order Status Distribution')
            except:
                status_fig = {}
            
            # Delivery times analysis
            try:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                delivery_data = pd.read_sql("""
                    SELECT delivery_time_minutes 
                    FROM orders 
                    WHERE delivery_time_minutes IS NOT NULL
                """, conn)
                conn.close()
                delivery_fig = px.histogram(delivery_data, x='delivery_time_minutes', nbins=20,
                                          title='Delivery Time Distribution')
            except:
                delivery_fig = {}
            
            # Payment methods
            try:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                payment_data = pd.read_sql("""
                    SELECT payment_method, COUNT(*) as count 
                    FROM orders 
                    GROUP BY payment_method
                """, conn)
                conn.close()
                payment_fig = px.pie(payment_data, values='count', names='payment_method',
                                   title='Payment Method Preferences')
            except:
                payment_fig = {}
            
            return peak_fig, status_fig, delivery_fig, payment_fig
    
    def run_server(self, debug=True, port=8050):
        """Run the dashboard server (compatibility method)"""
        self.run(debug=debug, port=port)
    
    def run(self, debug=True, port=8050):
        """Run the dashboard server"""
        print(f"🚀 Starting Food Delivery Dashboard on http://localhost:{port}")
        print("📊 Loading initial data...")
        
        # Load initial data
        self.load_data()
        
        print("✅ Dashboard ready!")
        self.app.run(debug=debug, port=port)

def main():
    """Main function to run the dashboard"""
    dashboard = FoodDeliveryDashboard()
    dashboard.run()

if __name__ == "__main__":
    main() 