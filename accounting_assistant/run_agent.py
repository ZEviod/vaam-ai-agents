#!/usr/bin/env python3
"""
Automated AI Accounting Agent Launcher
This script initializes and runs the fully automated accounting agent.
"""

import sys
import os
import subprocess
import time

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import schedule
        import requests
        import dotenv
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def check_environment():
    """Check environment configuration."""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        print("📋 Creating .env file from template...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ .env file created from template")
            print("🔧 Please edit .env file with your credentials")
        else:
            print("❌ .env.example template not found")
        return False
    
    print("✅ Environment file found")
    return True

def main():
    """Main launcher function."""
    print("🚀 AUTOMATED AI ACCOUNTING AGENT LAUNCHER")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    env_ready = check_environment()
    
    print("\n🤖 Starting Automated Accounting Agent...")
    print("📊 Features enabled:")
    print("   • Automated bank synchronization")
    print("   • AI-powered expense categorization")
    print("   • Scheduled payroll processing")
    print("   • Automatic invoice generation")
    print("   • Tax report automation")
    print("   • Email notifications")
    print("   • Real-time dashboard")
    
    if not env_ready:
        print("\n⚠️  Please configure .env file before running")
        print("📝 Edit .env file with your email and API credentials")
        return
    
    # Import and run the agent
    try:
        from accounting_assistant import AutomatedAccountingAgent
        
        print("\n🔄 Initializing agent...")
        agent = AutomatedAccountingAgent()
        
        print("✅ Agent initialized successfully!")
        print("🌐 Agent is now running continuously...")
        print("🛑 Press Ctrl+C to stop\n")
        
        # Run the agent
        agent.run_continuously()
        
    except KeyboardInterrupt:
        print("\n🛑 Agent stopped by user")
    except Exception as e:
        print(f"\n❌ Error running agent: {e}")
        print("🔧 Check your configuration and try again")

if __name__ == "__main__":
    main()
