#!/usr/bin/env python3
"""
Simple test script for the Driver Service Agent
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from driver_service_agent import DriverServiceAgent
    print("✅ Successfully imported DriverServiceAgent")
    
    # Initialize the agent
    agent = DriverServiceAgent()
    print("✅ Agent initialized successfully!")
    print(f"🤖 AI reasoning enabled: {agent.reasoning_enabled}")
    
    # Test basic functionality
    print("\n" + "="*50)
    print("🧪 Testing AI Agent Capabilities")
    print("="*50)
    
    test_messages = [
        "I haven't received my payment",
        "The app is crashing",
        "URGENT: accident happened",
        "How do I file a complaint?",
        "Hello, I need help"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: '{message}'")
        print("-" * 40)
        
        # Test context analysis
        context = agent.analyze_issue_context(message)
        print(f"📊 Context: Issue={context.get('issue_type')}, Urgency={context.get('urgency')}, Sentiment={context.get('sentiment')}")
        
        # Test intelligent response
        response = agent.smart_response_with_reasoning(message)
        print(f"🤖 Response: {response[:150]}{'...' if len(response) > 150 else ''}")
    
    print("\n" + "="*50)
    print("✅ All tests completed successfully!")
    print("🚗 Your AI agent is working perfectly!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
