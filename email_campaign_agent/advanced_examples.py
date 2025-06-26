"""
Advanced Usage Examples for AI Email Campaign Agent
"""

from email_campaign_agent import AIEmailCampaignAgent, CampaignConfig, AutomationRule, EmailContact
from datetime import datetime, timedelta

def setup_advanced_automation():
    """Setup advanced automation workflows"""
    agent = AIEmailCampaignAgent()
    
    # 1. Welcome series automation
    welcome_series = [
        AutomationRule(
            name="Welcome Email 1 - Immediate",
            trigger_event="new_user",
            conditions={},
            action_template="welcome",
            delay_hours=0
        ),
        AutomationRule(
            name="Welcome Email 2 - Day 3",
            trigger_event="new_user",
            conditions={},
            action_template="onboarding_tips",
            delay_hours=72
        ),
        AutomationRule(
            name="Welcome Email 3 - Week 1",
            trigger_event="new_user",
            conditions={},
            action_template="first_week_check",
            delay_hours=168
        )
    ]
    
    for rule in welcome_series:
        agent.add_automation_rule(rule)
    
    # 2. Engagement-based automation
    engagement_rules = [
        AutomationRule(
            name="High-Value User Rewards",
            trigger_event="high_engagement",
            conditions={"engagement_score_min": 8.0},
            action_template="vip_rewards",
            delay_hours=0
        ),
        AutomationRule(
            name="Low Engagement Re-activation",
            trigger_event="low_engagement",
            conditions={"engagement_score_max": 3.0},
            action_template="reactivation_offer",
            delay_hours=24
        )
    ]
    
    for rule in engagement_rules:
        agent.add_automation_rule(rule)
    
    # 3. Geographic automation
    location_rule = AutomationRule(
        name="London Special Offers",
        trigger_event="location_based",
        conditions={"city": "London"},
        action_template="london_promotions",
        delay_hours=0
    )
    
    agent.add_automation_rule(location_rule)
    
    return agent

def create_advanced_campaigns():
    """Create sophisticated campaigns with A/B testing"""
    agent = AIEmailCampaignAgent()
    
    # A/B Test Campaign
    ab_campaign = CampaignConfig(
        name="Driver Bonus A/B Test",
        template_name="driver_bonus",
        subject_line="🚗 Special Bonus Available!",
        target_segments=["drivers", "active_users"],
        send_time=datetime.now() + timedelta(hours=2),
        frequency="once",
        ab_test=True,
        optimization_goal="clicks",
        auto_optimize=True,
        max_recipients_per_hour=50
    )
    
    campaign_id = agent.create_campaign(ab_campaign)
    
    # Scheduled Newsletter
    newsletter_campaign = CampaignConfig(
        name="Weekly VAAM Update",
        template_name="newsletter",
        subject_line="Your Weekly VAAM Digest - {{date}}",
        target_segments=["active_users", "high_value"],
        send_time=datetime.now().replace(hour=9, minute=0, second=0) + timedelta(days=7),
        frequency="weekly",
        auto_optimize=True,
        max_recipients_per_hour=200
    )
    
    newsletter_id = agent.create_campaign(newsletter_campaign)
    
    # Segmented Rider Campaign
    rider_campaign = CampaignConfig(
        name="Rider Safety Update",
        template_name="safety_update",
        subject_line="🛡️ New Safety Features in Your Area",
        target_segments=["riders", "geographic_london"],
        send_time=datetime.now() + timedelta(days=1),
        frequency="once",
        auto_optimize=False,
        max_recipients_per_hour=100
    )
    
    rider_id = agent.create_campaign(rider_campaign)
    
    return agent, [campaign_id, newsletter_id, rider_id]

def bulk_data_processing():
    """Demonstrate bulk data processing capabilities"""
    agent = AIEmailCampaignAgent()
    
    # Bulk import from CSV
    agent.bulk_import("sample_contacts.csv")
    
    # Add contacts programmatically
    bulk_contacts = [
        {
            'email': f'user{i}@vaam.com',
            'name': f'User {i}',
            'age': 20 + (i % 40),
            'city': 'London' if i % 2 == 0 else 'Manchester',
            'country': 'UK',
            'segment': 'riders' if i % 3 == 0 else 'drivers',
            'engagement_score': (i % 10) + 1.5,
            'preferences': {'notifications': i % 2 == 0}
        }
        for i in range(100, 150)
    ]
    
    for contact_data in bulk_contacts:
        agent.add_contact(contact_data)
    
    return agent

def analytics_and_monitoring():
    """Advanced analytics and monitoring"""
    agent = AIEmailCampaignAgent()
    
    # Get comprehensive analytics
    analytics = agent.get_analytics()
    
    print("=== COMPREHENSIVE ANALYTICS ===")
    print(f"Total Contacts: {analytics['total_contacts']}")
    print(f"Total Campaigns: {analytics['total_campaigns']}")
    print(f"Emails Sent: {analytics['total_emails_sent']}")
    print(f"Open Rate: {analytics['open_rate']:.2f}%")
    print(f"Click Rate: {analytics['click_rate']:.2f}%")
    
    print("\n=== SEGMENT DISTRIBUTION ===")
    for segment, count in analytics['segment_distribution'].items():
        print(f"{segment}: {count} contacts")
    
    print(f"\n=== RECENT ACTIVITY ===")
    for status, count in analytics['recent_activity'].items():
        print(f"{status}: {count}")
    
    return analytics

def real_time_automation_demo():
    """Demonstrate real-time automation capabilities"""
    agent = AIEmailCampaignAgent()
    
    # Start the automation engine
    agent.start_automation()
    
    print("🤖 AI Agent is now running in real-time automation mode!")
    print("✅ Monitoring for new contacts, inactive users, and scheduled campaigns")
    print("📊 AI-powered segmentation active")
    print("🎯 Personalized content generation enabled")
    print("⚡ Real-time trigger-based emails active")
    
    # Simulate adding a new contact (will trigger welcome automation)
    new_contact = {
        'email': 'realtime@vaam.com',
        'name': 'Real Time User',
        'age': 30,
        'city': 'London',
        'segment': 'riders',
        'engagement_score': 0.0
    }
    
    agent.add_contact(new_contact)
    print(f"📧 Added new contact: {new_contact['email']} - Welcome automation triggered!")
    
    return agent

if __name__ == "__main__":
    print("🚀 AI Email Campaign Agent - Advanced Examples")
    print("=" * 50)
    
    # Choose which example to run
    example = input("""
Choose an example to run:
1. Advanced Automation Setup
2. Advanced Campaigns with A/B Testing
3. Bulk Data Processing
4. Analytics and Monitoring
5. Real-time Automation Demo
Enter choice (1-5): """)
    
    if example == "1":
        agent = setup_advanced_automation()
        print("✅ Advanced automation workflows configured!")
        
    elif example == "2":
        agent, campaign_ids = create_advanced_campaigns()
        print(f"✅ Created {len(campaign_ids)} advanced campaigns!")
        
    elif example == "3":
        agent = bulk_data_processing()
        print("✅ Bulk data processing completed!")
        
    elif example == "4":
        analytics_and_monitoring()
        
    elif example == "5":
        agent = real_time_automation_demo()
        try:
            input("Press Enter to stop the automation...")
        finally:
            agent.stop_automation()
    
    else:
        print("Invalid choice. Running basic demo...")
        agent = setup_advanced_automation()
        agent.start_automation()
        print("Basic automation started. Check the logs for activity.")
