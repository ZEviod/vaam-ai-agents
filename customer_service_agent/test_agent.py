#!/usr/bin/env python3
"""
Test script for Vaam Smart Customer Service Agent
Run this to test the AI functionality without starting the web server.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_agent():
    try:
        from customer_service_agent import SmartCustomerServiceAgent
        
        print("🤖 Testing Vaam Smart Customer Service Agent...")
        print("=" * 50)
        
        # Create agent instance
        agent = SmartCustomerServiceAgent()
        
        # Test scenarios
        test_messages = [
            "I lost my phone in the car yesterday",
            "The driver was speeding and I felt unsafe", 
            "I was charged twice for the same ride",
            "The app crashed when I tried to book a ride"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n🔍 Test {i}: {message}")
            print("-" * 30)
            
            # Analyze issue
            issue_category = agent.analyze_issue(message)
            context = agent.extract_context(message)
            
            print(f"📋 Issue Category: {issue_category or 'Unknown'}")
            print(f"🎯 Urgency: {context['urgency']}")
            print(f"😊 Emotion: {context['emotion']}")
            
            # Generate response
            try:
                response = agent.generate_intelligent_response(message, f"test_session_{i}")
                print(f"🤖 AI Response: {response[:100]}...")
                
                # Create ticket if needed
                if issue_category and context["emotion"] == "negative":
                    ticket_id = agent.create_complaint_ticket(message, issue_category, context, f"test_session_{i}")
                    print(f"🎫 Ticket Created: {ticket_id}")
                
            except Exception as e:
                print(f"⚠️  Response generation failed: {e}")
                # Test fallback
                fallback = agent.generate_fallback_response(message)
                print(f"🔄 Fallback Response: {fallback[:100]}...")
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("🚀 Run 'python run.py' to start the web server")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Install requirements: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Test Error: {e}")

if __name__ == "__main__":
    test_agent()
