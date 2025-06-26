#!/usr/bin/env python3
"""
HOW TO RUN THE INTELLIGENT OTP AGENT
====================================

This script shows you all the different ways to run the agent
"""

import os
import subprocess
import sys

def show_options():
    print("🤖 INTELLIGENT OTP AGENT - HOW TO RUN")
    print("=" * 50)
    print()
    print("Choose how you want to run the agent:")
    print()
    print("1️⃣  REST API Server (for web integration)")
    print("   python api_server.py")
    print("   → Starts HTTP server on localhost:5000")
    print("   → Use with curl, Postman, or web apps")
    print()
    print("2️⃣  Full Automation (file monitoring + scheduled tasks)")
    print("   python automation.py")
    print("   → Monitors data/incoming/ for JSON/CSV files")
    print("   → Automatic cleanup and maintenance")
    print("   → Background processing")
    print()
    print("3️⃣  Interactive Demo")
    print("   python otp_messaging_agent.py")
    print("   → Shows all features with examples")
    print("   → Demonstrates AI routing and processing")
    print()
    print("4️⃣  Process Your Data (what we just did)")
    print("   python demo_your_data.py")
    print("   → Processes your auto_messages.json")
    print("   → Shows real-time results")
    print()
    print("5️⃣  Real-time Monitoring")
    print("   python monitor.py")
    print("   → Live dashboard with metrics")
    print("   → Performance monitoring")
    print()
    print("6️⃣  Enterprise Integration Examples")
    print("   python enterprise_demo.py")
    print("   → Simulates real business integrations")
    print("   → Shows automated workflows")
    print()
    print("7️⃣  Test API Endpoints")
    print("   python test_api.py")
    print("   → Tests all REST API functions")
    print("   → Requires API server to be running")
    print()

def run_choice(choice):
    scripts = {
        "1": "api_server.py",
        "2": "automation.py", 
        "3": "otp_messaging_agent.py",
        "4": "demo_your_data.py",
        "5": "monitor.py",
        "6": "enterprise_demo.py",
        "7": "test_api.py"
    }
    
    if choice in scripts:
        script = scripts[choice]
        print(f"\n🚀 Running: python {script}")
        print("=" * 50)
        
        try:
            subprocess.run([sys.executable, script], check=True)
        except KeyboardInterrupt:
            print(f"\n⏹️  Stopped {script}")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error running {script}: {e}")
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    show_options()
    
    print("\n" + "="*50)
    print("📋 QUICK START RECOMMENDATIONS:")
    print()
    print("🆕 New user? Start with: python otp_messaging_agent.py")
    print("🌐 Want API access? Run: python api_server.py")
    print("📁 Have data files? Use: python automation.py")
    print("📊 Want monitoring? Try: python monitor.py")
    print()
    
    # Show current status
    if os.path.exists("data/incoming/auto_messages.json"):
        print("✅ Your auto_messages.json is ready for processing!")
    
    if os.path.exists("otp_agent.db"):
        print("✅ Database exists with previous messages")
    
    print("\n💡 TIP: You can run multiple scripts simultaneously!")
    print("   For example: API server + automation for full functionality")
    
    while True:
        try:
            choice = input("\n🔢 Enter your choice (1-7) or 'q' to quit: ").strip()
            if choice.lower() == 'q':
                break
            run_choice(choice)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
