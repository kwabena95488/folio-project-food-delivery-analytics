#!/usr/bin/env python3
"""
Open Food Delivery Dashboard in Browser
"""

import webbrowser
import requests
import time
import sys

def open_dashboard():
    """Open the dashboard in the default web browser"""
    dashboard_url = "http://localhost:8050"
    
    print("🌐 Opening Food Delivery Analytics Dashboard...")
    print(f"📍 URL: {dashboard_url}")
    
    # Check if dashboard is running
    try:
        response = requests.get(dashboard_url, timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard is running and accessible")
            
            # Open in browser
            print("🚀 Opening dashboard in your default web browser...")
            webbrowser.open(dashboard_url)
            
            print("\n" + "="*60)
            print("🎉 DASHBOARD SUCCESSFULLY OPENED!")
            print("="*60)
            print(f"📊 Dashboard URL: {dashboard_url}")
            print("\n🎯 Available Features:")
            print("   📊 Overview - Business KPIs and metrics")
            print("   👥 Customer Analytics - Segmentation & lifetime value")
            print("   🏪 Restaurant Performance - Rankings & efficiency")
            print("   🍕 Menu Analytics - Item performance & profitability")
            print("   📈 Revenue Trends - Forecasting & analysis")
            print("   ⏰ Operational Insights - Peak hours & efficiency")
            print("\n💡 Navigate between tabs to explore different analytics!")
            print("🔄 Dashboard auto-refreshes every 30 seconds")
            print("⏹️  Press Ctrl+C in the terminal to stop the dashboard")
            print("="*60)
            
            return True
        else:
            print(f"❌ Dashboard returned HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Dashboard is not running!")
        print("\n💡 Start the dashboard first:")
        print("   python launch_dashboard.py")
        print("\n   Then run this script again:")
        print("   python open_dashboard.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = open_dashboard()
    if not success:
        sys.exit(1) 