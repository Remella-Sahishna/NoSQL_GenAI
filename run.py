#!/usr/bin/env python3
"""
NoSQL Library Management System
Startup Script

This script provides a better startup experience with error handling
and helpful information for running the library system.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ['flask', 'flask_pymongo', 'google.generativeai']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('.', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install dependencies with: pip install -r requirements.txt")
        sys.exit(1)
    
    print("✅ All required packages are installed")

def check_mongodb():
    """Check if MongoDB is running."""
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.server_info()
        print("✅ MongoDB is running and accessible")
        client.close()
    except Exception as e:
        print("⚠️  Warning: MongoDB connection failed")
        print(f"   Error: {e}")
        print("   Make sure MongoDB is running on localhost:27017")
        print("   You can still start the app, but database operations will fail")

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = ['logs', 'uploads']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def main():
    """Main startup function."""
    print("🚀 Starting NoSQL Library Management System...")
    print("=" * 50)
    
    # Pre-flight checks
    check_python_version()
    check_dependencies()
    check_mongodb()
    create_directories()
    
    print("\n" + "=" * 50)
    print("🎯 Starting Flask application...")
    print("📚 Library system will be available at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Import and run the Flask app
        from chatbot import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down NoSQL Library System...")
        print("Thank you for using our library management system!")
    except Exception as e:
        print(f"\n❌ Error starting the application: {e}")
        print("Please check the error message above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()

