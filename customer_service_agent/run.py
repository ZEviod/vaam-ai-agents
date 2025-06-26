#!/usr/bin/env python3
"""
Vaam Smart Customer Service Agent
Run this file to start the intelligent customer service chatbot.
"""

import os
import sys

def main():
    try:
        # Import and run the customer service agent
        from customer_service_agent import app, socketio
        
        print("🚗 Starting Vaam Smart Customer Service Agent...")
        print("🤖 AI-powered intelligent assistance enabled")
        print("🌐 Web interface will be available at: http://localhost:5000")
        print("📱 Mobile-friendly interface included")
        print("🎫 Automatic ticket creation for complex issues")
        print("\n" + "="*50)
        print("Press Ctrl+C to stop the server")
        print("="*50 + "\n")
        
        # Run the Flask-SocketIO app
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Please install required packages: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
