#!/usr/bin/env python3
"""
Food Delivery Analytics Dashboard Launcher
Simple script to launch the interactive dashboard
"""

import os
import sys
import subprocess

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        'dash', 'dash-bootstrap-components', 'plotly', 
        'pandas', 'numpy', 'sqlite3'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_database():
    """Check if database exists"""
    db_path = "database/food_delivery.db"
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        print(f"   Expected location: {db_path}")
        print("\n💡 Run the setup script first:")
        print("   python database/setup_database.py")
        return False
    
    print(f"✅ Database found: {db_path}")
    return True

def launch_dashboard():
    """Launch the interactive dashboard"""
    print("🍽️ Food Delivery Analytics Dashboard Launcher")
    print("=" * 50)
    
    # Check requirements
    print("🔍 Checking requirements...")
    if not check_requirements():
        return 1
    
    # Check database
    print("🔍 Checking database...")
    if not check_database():
        return 1
    
    # Launch dashboard
    print("🚀 Launching interactive dashboard...")
    print("📊 Dashboard will open at: http://localhost:8050")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Import and run dashboard
        sys.path.append('python_analytics')
        from interactive_dashboard import FoodDeliveryDashboard
        
        dashboard = FoodDeliveryDashboard()
        dashboard.run_server(debug=False, port=8050)
        
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Dashboard failed to start: {e}")
        print("\n💡 Try running the setup script first:")
        print("   python run_setup.py")
        return 1

if __name__ == "__main__":
    exit(launch_dashboard()) 