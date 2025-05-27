#!/usr/bin/env python3
"""
Test script to verify all dashboard charts are working
"""

import sys
import os
sys.path.append('python_analytics')

from analytics_engine import FoodDeliveryAnalytics
import pandas as pd

def test_data_availability():
    """Test if all required data is available for charts"""
    print("🧪 Testing Data Availability for Dashboard Charts...")
    
    try:
        # Initialize analytics engine
        analytics = FoodDeliveryAnalytics()
        
        # Load all data
        print("🔄 Loading analytics data...")
        customer_data = analytics.get_customer_analytics()
        restaurant_data = analytics.get_restaurant_performance()
        menu_data = analytics.get_menu_analytics()
        time_data = analytics.get_time_series_data()
        
        # Perform advanced analytics
        print("🔄 Running advanced analytics...")
        analytics.customer_segmentation()
        analytics.revenue_forecasting()
        analytics.peak_hours_analysis()
        
        print("\n📊 Data Summary:")
        print(f"✅ Customer records: {len(customer_data)}")
        print(f"✅ Restaurant records: {len(restaurant_data)}")
        print(f"✅ Menu item records: {len(menu_data)}")
        print(f"✅ Time series records: {len(time_data)}")
        
        # Test Customer Analytics data
        print("\n👥 Customer Analytics Data:")
        if not customer_data.empty:
            print(f"   ✅ Customer data columns: {list(customer_data.columns)}")
            if 'cluster' in customer_data.columns:
                print(f"   ✅ Customer segmentation: {customer_data['cluster'].nunique()} clusters")
            else:
                print("   ⚠️ No cluster column found")
            print(f"   ✅ CLV data: {len(customer_data[customer_data['estimated_clv'] > 0])} customers with CLV")
        else:
            print("   ❌ No customer data")
        
        # Test Restaurant Performance data
        print("\n🏪 Restaurant Performance Data:")
        if not restaurant_data.empty:
            print(f"   ✅ Restaurant columns: {list(restaurant_data.columns)}")
            print(f"   ✅ Top restaurant: {restaurant_data.iloc[0]['restaurant_name']}")
        else:
            print("   ❌ No restaurant data")
        
        # Test Menu Analytics data
        print("\n🍕 Menu Analytics Data:")
        if not menu_data.empty:
            print(f"   ✅ Menu columns: {list(menu_data.columns)}")
            print(f"   ✅ Categories: {menu_data['category'].nunique()}")
            print(f"   ✅ Top item: {menu_data.iloc[0]['item_name']}")
        else:
            print("   ❌ No menu data")
        
        # Test Revenue Forecasting data
        print("\n📈 Revenue Forecasting Data:")
        if 'revenue_forecast' in analytics.data_cache:
            forecast_data = analytics.data_cache['revenue_forecast']
            print(f"   ✅ Historical data points: {len(forecast_data['historical'])}")
            print(f"   ✅ Forecast data points: {len(forecast_data['forecast'])}")
            print(f"   ✅ Model R² score: {forecast_data['model_score']:.3f}")
        else:
            print("   ❌ No forecast data")
        
        # Test Peak Hours data
        print("\n⏰ Peak Hours Data:")
        if 'peak_hours' in analytics.data_cache:
            peak_data = analytics.data_cache['peak_hours']
            print(f"   ✅ Hourly data points: {len(peak_data['hourly'])}")
            print(f"   ✅ Daily data points: {len(peak_data['daily'])}")
        else:
            print("   ❌ No peak hours data")
        
        # Test time series data
        print("\n📊 Time Series Data:")
        if not time_data.empty:
            print(f"   ✅ Date range: {time_data['order_date'].min()} to {time_data['order_date'].max()}")
            print(f"   ✅ Hours covered: {time_data['hour_of_day'].nunique()}")
            print(f"   ✅ Days of week: {time_data['day_of_week'].nunique()}")
        else:
            print("   ❌ No time series data")
        
        analytics.close_connection()
        
        print("\n🎉 Data availability test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Data test failed: {e}")
        return False

def test_chart_data_structure():
    """Test the specific data structures needed for charts"""
    print("\n🔍 Testing Chart Data Structures...")
    
    try:
        analytics = FoodDeliveryAnalytics()
        
        # Load data
        analytics.get_customer_analytics()
        analytics.get_restaurant_performance()
        analytics.get_menu_analytics()
        analytics.get_time_series_data()
        analytics.customer_segmentation()
        analytics.revenue_forecasting()
        analytics.peak_hours_analysis()
        
        # Test specific chart requirements
        customer_data = analytics.data_cache.get('customer_analytics', pd.DataFrame())
        
        print("\n📊 Chart Data Structure Tests:")
        
        # Customer segmentation chart
        if not customer_data.empty and 'order_frequency' in customer_data.columns and 'avg_order_value' in customer_data.columns:
            print("   ✅ Customer segmentation chart data: OK")
        else:
            print("   ❌ Customer segmentation chart data: Missing columns")
        
        # CLV histogram
        if not customer_data.empty and 'estimated_clv' in customer_data.columns:
            clv_data = customer_data[customer_data['estimated_clv'] > 0]
            print(f"   ✅ CLV histogram data: {len(clv_data)} records")
        else:
            print("   ❌ CLV histogram data: Missing")
        
        # Menu analytics
        menu_data = analytics.data_cache.get('menu_analytics', pd.DataFrame())
        if not menu_data.empty and 'total_quantity_sold' in menu_data.columns:
            print("   ✅ Menu analytics chart data: OK")
        else:
            print("   ❌ Menu analytics chart data: Missing columns")
        
        analytics.close_connection()
        return True
        
    except Exception as e:
        print(f"❌ Chart structure test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Dashboard Charts Test Suite")
    print("=" * 50)
    
    success1 = test_data_availability()
    success2 = test_chart_data_structure()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Charts should be working.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Charts may have issues.")
        sys.exit(1) 