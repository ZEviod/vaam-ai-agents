#!/usr/bin/env python3
"""
Enhanced Driver Service Agent Demo
==================================

This script demonstrates the intelligent AI-powered driver service agent
with advanced reasoning, context awareness, and problem-solving capabilities.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from driver_service_agent import DriverServiceAgent
import json

def demo_intelligent_responses():
    """Demonstrate the AI agent's intelligent response capabilities."""
    print("🚗 Enhanced Vaam Driver Service Agent Demo 🤖")
    print("=" * 60)
    
    agent = DriverServiceAgent()
    
    # Test scenarios with varying complexity
    scenarios = [
        {
            "category": "💰 Financial Issue - Simple",
            "message": "When do I get paid?",
            "description": "Basic payment inquiry"
        },
        {
            "category": "💰 Financial Issue - Complex", 
            "message": "I haven't received my payment for last week and my bank details are correct. Trip #ABC12345 also needs compensation.",
            "description": "Multiple financial issues requiring analysis"
        },
        {
            "category": "🐛 Technical Issue - Urgent",
            "message": "URGENT: The app crashed during a trip and I can't see where the passenger wants to go!",
            "description": "Critical technical issue requiring immediate attention"
        },
        {
            "category": "😤 Service Complaint",
            "message": "A passenger was extremely rude and made discriminatory comments. I want to file a complaint.",
            "description": "Serious service issue requiring escalation"
        },
        {
            "category": "📋 General Inquiry",
            "message": "What documents do I need to register my car?",
            "description": "Standard information request"
        },
        {
            "category": "🆘 Emergency Situation",
            "message": "EMERGENCY: I had an accident during trip #XYZ789 and the passenger is injured!",
            "description": "Emergency requiring immediate human intervention"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['category']}")
        print(f"Description: {scenario['description']}")
        print(f"Driver Message: \"{scenario['message']}\"")
        print("-" * 60)
        
        # Analyze the context
        context = agent.analyze_issue_context(scenario['message'])
        print(f"🔍 AI Analysis:")
        print(f"   • Issue Type: {context.get('issue_type', 'Unknown')}")
        print(f"   • Urgency: {context.get('urgency', 'Low')}")
        print(f"   • Sentiment: {context.get('sentiment', 'Neutral')}")
        print(f"   • Entities Found: {context.get('entities', [])}")
        print(f"   • Requires Human: {context.get('requires_human', False)}")
        
        # Get the AI response
        response = agent.smart_response_with_reasoning(scenario['message'])
        print(f"\n🤖 AI Response:")
        print(f"   {response}")
        
        print("=" * 60)

def demo_conversation_memory():
    """Demonstrate conversation history and context awareness."""
    print("\n🧠 Conversation Memory & Context Demo")
    print("=" * 60)
    
    agent = DriverServiceAgent()
    
    conversation = [
        "Hi, I have a problem with a trip",
        "The passenger didn't show up for trip #ABC123",
        "I waited for 10 minutes as required",
        "How do I get compensation for the waiting time?"
    ]
    
    print("Simulating a multi-turn conversation:")
    
    for i, message in enumerate(conversation, 1):
        print(f"\nTurn {i} - Driver: {message}")
        response = agent.smart_response_with_reasoning(message)
        print(f"AI Agent: {response}")
        print("-" * 40)
    
    print(f"\n📊 Conversation History Stored: {len(agent.conversation_history)} messages")

def demo_reasoning_process():
    """Demonstrate the AI's reasoning process."""
    print("\n🧮 AI Reasoning Process Demo")
    print("=" * 60)
    
    agent = DriverServiceAgent()
    
    complex_message = "I have multiple issues: the app crashed during trip #ABC123, I haven't received payment for last week, and a passenger complained about me unfairly. This is urgent!"
    
    print(f"Complex Message: {complex_message}")
    print("\n🔍 Step-by-step AI Reasoning:")
    
    # Analyze context
    context = agent.analyze_issue_context(complex_message)
    print(f"1. Context Analysis: {json.dumps(context, indent=2)}")
    
    # Advanced reasoning
    reasoning = agent.advanced_reasoning(complex_message, context)
    print(f"\n2. Advanced Reasoning:")
    for step in reasoning['reasoning_steps']:
        print(f"   • {step}")
    
    print(f"\n3. Selected Solution:")
    solution = reasoning['solution']
    print(f"   • Type: {solution['type']}")
    print(f"   • Confidence: {solution.get('confidence', 0):.2f}")
    
    print(f"\n4. Final Response:")
    response = agent.smart_response_with_reasoning(complex_message)
    print(f"   {response}")

def interactive_demo():
    """Interactive demo mode."""
    print("\n💬 Interactive Demo Mode")
    print("=" * 60)
    print("You can now chat with the AI agent!")
    print("Commands:")
    print("  • Type your message normally")
    print("  • 'escalate' - Request human support")
    print("  • 'history' - Show conversation history")
    print("  • 'quit' - Exit demo")
    print("-" * 60)
    
    agent = DriverServiceAgent()
    
    while True:
        try:
            user_input = input("\n🚗 You: ").strip()
            
            if user_input.lower() == 'quit':
                print("\nThank you for trying the Enhanced Driver Service Agent!")
                print("🚗 Drive safely! 🤖")
                break
            
            if user_input.lower() == 'escalate':
                response = agent.escalate_to_human("User requested escalation")
                print(f"🔄 {response}")
                continue
            
            if user_input.lower() == 'history':
                print(f"\n📚 Conversation History ({len(agent.conversation_history)} messages):")
                for msg in agent.conversation_history[-6:]:  # Show last 6 messages
                    role = "🚗" if msg['role'] == 'user' else "🤖"
                    print(f"   {role} {msg['content'][:80]}...")
                continue
            
            if not user_input:
                continue
            
            response = agent.smart_response_with_reasoning(user_input)
            print(f"🤖 AI Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main demo function."""
    print("🚀 Welcome to the Enhanced Driver Service Agent Demo!")
    print("\nThis demo showcases:")
    print("✅ Intelligent context analysis")
    print("✅ Advanced AI reasoning")
    print("✅ Conversation memory")
    print("✅ Multi-turn conversations")
    print("✅ Priority-based responses")
    print("✅ Smart escalation")
    
    while True:
        print("\n" + "=" * 60)
        print("Choose a demo:")
        print("1. 🎯 Intelligent Responses")
        print("2. 🧠 Conversation Memory")
        print("3. 🧮 Reasoning Process")
        print("4. 💬 Interactive Chat")
        print("5. 🚪 Exit")
        print("=" * 60)
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            demo_intelligent_responses()
        elif choice == '2':
            demo_conversation_memory()
        elif choice == '3':
            demo_reasoning_process()
        elif choice == '4':
            interactive_demo()
        elif choice == '5':
            print("\nThank you for exploring the Enhanced Driver Service Agent!")
            print("🚗 Drive safely! 🤖")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
