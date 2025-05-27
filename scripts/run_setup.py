#!/usr/bin/env python3
"""
Food Delivery Analytics - Setup and Run Script
Executes the complete setup and analytics pipeline
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup and execution function"""
    print("🍽️ Food Delivery Analytics - Setup & Run")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Please run this script from the project root directory")
        return 1
    
    # Install dependencies
    print("📦 Installing dependencies...")
    if not run_command("pip install -r requirements.txt", "Installing Python packages"):
        print("⚠️ Some packages may have failed to install. Continuing anyway...")
    
    # Create database
    print("\n🗄️ Setting up database...")
    if not run_command("python database/setup_database.py", "Database setup"):
        print("❌ Database setup failed. Cannot continue.")
        return 1
    
    # Run analytics
    print("\n📊 Running analytics...")
    if not run_command("python python_analytics/analytics_engine.py", "Analytics execution"):
        print("❌ Analytics failed.")
        return 1
    
    print("\n🎉 Setup and analytics completed successfully!")
    print("\n📁 Check the 'outputs' directory for results")
    print("📊 The interactive dashboard should have opened in your browser")
    
    return 0

if __name__ == "__main__":
    exit(main()) 