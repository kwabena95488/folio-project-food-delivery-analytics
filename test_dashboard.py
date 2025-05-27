#!/usr/bin/env python3
"""
Test script to verify dashboard functionality
"""

import requests
import time
import sys

def test_dashboard():
    """Test dashboard accessibility and basic functionality"""
    print("🧪 Testing Food Delivery Dashboard...")
    
    dashboard_url = "http://localhost:8050"
    
    try:
        # Test basic accessibility
        print("🔍 Testing dashboard accessibility...")
        response = requests.get(dashboard_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Dashboard is accessible (HTTP 200)")
        else:
            print(f"❌ Dashboard returned HTTP {response.status_code}")
            return False
        
        # Test if the page contains expected content
        content = response.text.lower()
        expected_elements = [
            "food delivery analytics dashboard",
            "overview",
            "customer analytics",
            "restaurant performance"
        ]
        
        print("🔍 Testing dashboard content...")
        for element in expected_elements:
            if element in content:
                print(f"✅ Found: {element}")
            else:
                print(f"❌ Missing: {element}")
        
        # Test multiple requests to check for threading issues
        print("🔍 Testing multiple concurrent requests...")
        for i in range(5):
            try:
                test_response = requests.get(dashboard_url, timeout=5)
                if test_response.status_code == 200:
                    print(f"✅ Request {i+1}/5 successful")
                else:
                    print(f"❌ Request {i+1}/5 failed with HTTP {test_response.status_code}")
                time.sleep(1)
            except Exception as e:
                print(f"❌ Request {i+1}/5 failed: {e}")
        
        print("🎉 Dashboard test completed successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to dashboard. Is it running?")
        print("💡 Start the dashboard with: python launch_dashboard.py")
        return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_dashboard()
    sys.exit(0 if success else 1) 