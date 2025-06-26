#!/usr/bin/env python3
"""
Simple startup script for the Intelligent OTP Agent
Run this to get started quickly!
"""

import subprocess
import sys
import time
import os

def main():
    print("🚀 INTELLIGENT OTP AGENT - QUICK START")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("otp_messaging_agent.py"):
        print("❌ Please run this from the otp_messaging_agent directory")
        return
    
    print("🔍 Checking your setup...")
    
    # Check if auto_messages.json exists
    if os.path.exists("data/incoming/auto_messages.json"):
        print("✅ Found your auto_messages.json file")
        
        # Process it immediately
        print("\n📥 Processing your auto_messages.json...")
        try:
            result = subprocess.run([sys.executable, "demo_your_data.py"], 
                                  capture_output=True, text=True, timeout=30)
            print("✅ Your messages have been processed!")
            if result.stdout:
                print("📊 Results:")
                # Extract key info from output
                for line in result.stdout.split('\n'):
                    if 'Loaded' in line or 'sent' in line or 'Success' in line or 'Message' in line:
                        print(f"   {line}")
        except Exception as e:
            print(f"❌ Error processing: {e}")
    
    print("\n" + "="*50)
    print("🎯 WHAT'S NEXT?")
    print()
    print("1️⃣  Start API Server for real-time integration:")
    print("   python api_server.py")
    print("   Then visit: http://localhost:5000/health")
    print()
    print("2️⃣  Add more messages to process:")
    print("   Edit: data/incoming/auto_messages.json")
    print("   Or create new JSON files in data/incoming/")
    print()
    print("3️⃣  Start full automation (monitors files automatically):")
    print("   python automation.py")
    print()
    print("4️⃣  See live monitoring dashboard:")
    print("   python monitor.py")
    print()
    print("📖 For complete documentation, see:")
    print("   - README.md")
    print("   - AUTOMATION_GUIDE.md")
    print()
    print("💡 Your agent is ready to use! 🎉")

if __name__ == "__main__":
    main()
