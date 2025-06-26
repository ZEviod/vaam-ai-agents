"""
Quick Demo of AI Email Campaign Agent
"""

from email_campaign_agent import AIEmailCampaignAgent, CampaignConfig, AutomationRule
from datetime import datetime, timedelta
import time

def quick_demo():
    print("🚀 AI Email Campaign Agent - Quick Demo")
    print("=" * 50)
    
    # Initialize the AI agent
    print("1. Initializing AI Email Agent...")
    agent = AIEmailCampaignAgent()
    
    # Add sample contacts
    print("2. Adding sample contacts...")
    sample_contacts = [
        {
            'email': 'driver@demo.com',
            'name': 'Demo Driver',
            'age': 30,
            'city': 'London',
            'segment': 'drivers',
            'preferences': {'bonuses': True, 'notifications': True},
            'engagement_score': 8.5
        },
        {
            'email': 'rider@demo.com',
            'name': 'Demo Rider',
            'age': 25,
            'city': 'London',
            'segment': 'riders',
            'preferences': {'discounts': True, 'safety': True},
            'engagement_score': 7.2
        },
        {
            'email': 'inactive@demo.com',
            'name': 'Inactive User',
            'age': 35,
            'city': 'London',
            'segment': 'riders',
            'engagement_score': 2.1,
            'last_interaction': datetime.now() - timedelta(days=45)
        }
    ]
    
    for contact in sample_contacts:
        agent.add_contact(contact)
        print(f"   ✅ Added: {contact['email']}")
    
    # Set up automation rules
    print("3. Setting up AI automation rules...")
    
    welcome_rule = AutomationRule(
        name="Welcome New Users",
        trigger_event="new_user",
        conditions={},
        action_template="welcome",
        delay_hours=0
    )
    
    reengagement_rule = AutomationRule(
        name="Re-engage Inactive Users",
        trigger_event="inactive_user",
        conditions={'engagement_score_max': 5.0},
        action_template="engagement",
        delay_hours=0
    )
    
    agent.add_automation_rule(welcome_rule)
    agent.add_automation_rule(reengagement_rule)
    print("   ✅ Welcome automation configured")
    print("   ✅ Re-engagement automation configured")
    
    # Create a campaign
    print("4. Creating AI-powered campaign...")
    
    campaign_config = CampaignConfig(
        name="Demo Newsletter",
        template_name="newsletter",
        subject_line="🚗 Your Weekly VAAM Update",
        target_segments=["active_users", "high_value"],
        send_time=datetime.now() + timedelta(minutes=1),
        frequency="weekly",
        auto_optimize=True,
        max_recipients_per_hour=50
    )
    
    campaign_id = agent.create_campaign(campaign_config)
    print(f"   ✅ Campaign created: {campaign_id}")
    
    # Show AI segmentation
    print("5. AI-powered contact segmentation:")
    segments = agent.ai_segment_contacts()
    for segment_name, contacts in segments.items():
        if contacts:
            print(f"   📊 {segment_name}: {len(contacts)} contacts")
    
    # Show analytics
    print("6. Current analytics:")
    analytics = agent.get_analytics()
    print(f"   📈 Total Contacts: {analytics['total_contacts']}")
    print(f"   📈 Total Campaigns: {analytics['total_campaigns']}")
    print(f"   📈 Automation Rules: {analytics['automation_rules']}")
    
    # Demonstrate automation trigger
    print("7. Testing automation triggers...")
    agent.check_automation_triggers()
    print("   ✅ Automation triggers checked")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed successfully!")
    print("\n💡 To send real emails:")
    print("   1. Update config.json with your SMTP settings")
    print("   2. Run: agent.start_automation()")
    print("   3. The agent will run continuously, processing data and sending emails")
    
    print("\n📚 For advanced features, check:")
    print("   - advanced_examples.py")
    print("   - README.md")
    
    return agent

if __name__ == "__main__":
    agent = quick_demo()
    
    # Optional: Start automation for real-time demo
    choice = input("\n🤖 Start real-time automation? (y/n): ").lower()
    if choice == 'y':
        print("Starting automation engine...")
        agent.start_automation()
        print("✅ Automation running! Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(5)
                analytics = agent.get_analytics()
                print(f"Live: {analytics['total_contacts']} contacts, {analytics['total_campaigns']} campaigns")
        except KeyboardInterrupt:
            print("\nStopping automation...")
            agent.stop_automation()
            print("✅ Automation stopped.")
    else:
        print("Demo completed. Run with automation for full experience!")
