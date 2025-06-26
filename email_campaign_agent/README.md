# AI-Powered Email Campaign Agent

A fully automated, intelligent email marketing agent that processes data and sends targeted campaigns automatically. Built with AI-powered segmentation, personalized content generation, and real-time automation.

## 🚀 Features

### Core AI Capabilities

- **Intelligent Data Processing**: Automatically imports and processes contact data from CSV/JSON files
- **AI-Powered Segmentation**: Smart contact segmentation based on behavior, demographics, and engagement
- **Automated Content Generation**: Personalized email content based on user preferences and history
- **Real-time Automation**: Event-driven email triggers (new users, inactive users, etc.)
- **Smart Scheduling**: Optimized send times based on user behavior patterns
- **A/B Testing**: Automatic campaign optimization
- **Comprehensive Analytics**: Real-time performance tracking and insights

### Automation Features

- **Event-Driven Triggers**: Welcome series, re-engagement, location-based campaigns
- **Bulk Data Processing**: Handle thousands of contacts efficiently
- **Rate Limiting**: Respect email provider limits
- **Database Persistence**: SQLite database for reliable data storage
- **Background Processing**: Non-blocking campaign execution
- **Error Handling**: Robust error logging and recovery

## 📦 Installation

1. **Install Dependencies**:

```bash
pip install -r requirements.txt
```

2. **Configure SMTP Settings**:
   Update `config.json` with your email provider settings:

```json
{
  "smtp": {
    "server": "smtp.gmail.com",
    "port": 587,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
    "use_tls": true
  }
}
```

## 🤖 Quick Start - Fully Automated

### 1. Basic Setup (Data In → Emails Out)

```python
from email_campaign_agent import AIEmailCampaignAgent

# Initialize the AI agent
agent = AIEmailCampaignAgent()

# Import your contact data (CSV or JSON)
agent.bulk_import("your_contacts.csv")

# Start full automation
agent.start_automation()

# The agent now runs automatically!
# - Segments contacts intelligently
# - Sends welcome emails to new users
# - Re-engages inactive users
# - Personalizes all content
# - Tracks performance
```

### 2. Advanced Automation Setup

```python
from email_campaign_agent import AIEmailCampaignAgent, AutomationRule, CampaignConfig
from datetime import datetime, timedelta

agent = AIEmailCampaignAgent()

# Set up automation rules
welcome_rule = AutomationRule(
    name="Welcome New Users",
    trigger_event="new_user",
    conditions={},
    action_template="welcome",
    delay_hours=1  # Send 1 hour after signup
)

reengagement_rule = AutomationRule(
    name="Re-engage Inactive Users",
    trigger_event="inactive_user",
    conditions={'engagement_score_max': 5.0},
    action_template="engagement",
    delay_hours=0  # Send immediately
)

agent.add_automation_rule(welcome_rule)
agent.add_automation_rule(reengagement_rule)

# Create scheduled campaigns
newsletter = CampaignConfig(
    name="Weekly Newsletter",
    template_name="newsletter",
    subject_line="Your Weekly Update - {{date}}",
    target_segments=["active_users", "high_value"],
    send_time=datetime.now() + timedelta(days=7),
    frequency="weekly",
    auto_optimize=True
)

campaign_id = agent.create_campaign(newsletter)
agent.start_automation()
```

## 📊 Data Formats

### CSV Format (sample_contacts.csv)

```csv
email,name,age,city,country,segment,preferences,engagement_score,custom_fields
user@example.com,John Doe,30,London,UK,drivers,"{""notifications"": true}",8.5,"{""vehicle_type"": ""sedan""}"
```

### JSON Format

```json
{
  "contacts": [
    {
      "email": "user@example.com",
      "name": "John Doe",
      "age": 30,
      "city": "London",
      "segment": "drivers",
      "preferences": { "notifications": true },
      "engagement_score": 8.5
    }
  ]
}
```

### Programmatic Contact Addition

```python
agent.add_contact({
    'email': 'new_user@example.com',
    'name': 'New User',
    'age': 25,
    'city': 'London',
    'segment': 'riders',
    'preferences': {'discounts': True, 'safety': True},
    'engagement_score': 0.0
})
```

## 🎯 AI Segmentation

The agent automatically creates intelligent segments:

- **Behavioral Segments**: `new_users`, `active_users`, `inactive_users`
- **Engagement Segments**: `high_value`, `low_engagement`
- **Geographic Segments**: `geographic_london`, etc.
- **Demographic Segments**: `age_young`, `age_middle`, `age_senior`

## 📧 Email Templates

Templates support dynamic placeholders that are automatically filled with personalized content:

```html
Hi {{name}}, Welcome to {{company_name}}! We're thrilled to have you join our
community. Based on your interests in {{preferences}}, we think you'll love:
{{personalized_recommendations}} {{special_offer}} Best regards, The
{{company_name}} Team
```

Available placeholders:

- `{{name}}`, `{{company_name}}`, `{{city}}`, `{{country}}`
- `{{date}}`, `{{preferences}}`, `{{personalized_recommendations}}`
- `{{special_offer}}`, `{{expiry_date}}`, `{{newsletter_content}}`

## 📈 Analytics & Monitoring

```python
# Get comprehensive analytics
analytics = agent.get_analytics()

print(f"Total Contacts: {analytics['total_contacts']}")
print(f"Open Rate: {analytics['open_rate']:.2f}%")
print(f"Click Rate: {analytics['click_rate']:.2f}%")
print(f"Segment Distribution: {analytics['segment_distribution']}")
```

## 🔧 Configuration Options

### AI Settings

```json
{
  "ai_settings": {
    "auto_segment": true,
    "auto_optimize": true,
    "personalization_level": "high",
    "send_time_optimization": true
  },
  "rate_limits": {
    "emails_per_hour": 100,
    "emails_per_day": 1000
  }
}
```

## 🚦 Usage Examples

### Example 1: E-commerce Store

```python
# For an e-commerce store
agent = AIEmailCampaignAgent()

# Import customer data
agent.bulk_import("customers.csv")

# Set up abandoned cart automation
cart_rule = AutomationRule(
    name="Abandoned Cart Recovery",
    trigger_event="cart_abandoned",
    conditions={'cart_value_min': 50},
    action_template="cart_recovery",
    delay_hours=2
)

agent.add_automation_rule(cart_rule)
agent.start_automation()
```

### Example 2: SaaS Platform

```python
# For a SaaS platform
agent = AIEmailCampaignAgent()

# Set up onboarding sequence
onboarding_rules = [
    AutomationRule("Welcome Email", "new_user", {}, "welcome", 0),
    AutomationRule("Setup Guide", "new_user", {}, "setup", 24),
    AutomationRule("Feature Tour", "new_user", {}, "features", 72),
    AutomationRule("Check-in", "new_user", {}, "checkin", 168)
]

for rule in onboarding_rules:
    agent.add_automation_rule(rule)

agent.start_automation()
```

### Example 3: Ride-sharing Company (VAAM)

```python
# For VAAM ride-sharing
agent = AIEmailCampaignAgent()

# Import drivers and riders
agent.bulk_import("vaam_users.csv")

# Driver-specific automation
driver_bonus = AutomationRule(
    name="Driver Weekly Bonus",
    trigger_event="weekly_summary",
    conditions={'segment': 'drivers', 'trips_min': 10},
    action_template="driver_bonus",
    delay_hours=0
)

# Rider promotion
rider_promo = AutomationRule(
    name="Rider Discount",
    trigger_event="inactive_user",
    conditions={'segment': 'riders', 'days_inactive_min': 14},
    action_template="rider_discount",
    delay_hours=0
)

agent.add_automation_rule(driver_bonus)
agent.add_automation_rule(rider_promo)
agent.start_automation()
```

## 🎮 Running the Agent

### Simple Run

```bash
python email_campaign_agent.py
```

### Advanced Examples

```bash
python advanced_examples.py
```

### Background Service

```python
# For production deployment
agent = AIEmailCampaignAgent()
agent.start_automation()

# The agent now runs continuously in the background
# Processing new data, sending emails, and optimizing campaigns
```

## 🔐 Security & Best Practices

1. **Email Provider Setup**: Use app-specific passwords for Gmail
2. **Rate Limiting**: Configure appropriate sending limits
3. **Data Privacy**: All data stored locally in SQLite
4. **Error Handling**: Comprehensive logging to `email_agent.log`
5. **Testing**: Use test mode before production deployment

## 📋 File Structure

```
email_campaign_agent/
├── email_campaign_agent.py    # Main AI agent
├── advanced_examples.py       # Advanced usage examples
├── config.json               # Configuration file
├── requirements.txt          # Dependencies
├── sample_contacts.csv       # Sample data
├── templates.json           # Email templates (auto-created)
├── email_agent.db          # SQLite database (auto-created)
└── email_agent.log         # Log file (auto-created)
```

## 🤝 Integration

The agent can be easily integrated into existing systems:

```python
# Web application integration
from flask import Flask, request
app = Flask(__name__)
agent = AIEmailCampaignAgent()
agent.start_automation()

@app.route('/add_user', methods=['POST'])
def add_user():
    user_data = request.json
    agent.add_contact(user_data)
    return {'status': 'success'}

# API integration
import requests

def sync_with_crm():
    users = requests.get('https://api.yourcrm.com/users').json()
    for user in users:
        agent.add_contact(user)
```

## 🚀 The agent is designed to be "plug and play" - just provide data and it handles the rest automatically!

### Key Automation Benefits:

- ✅ **Zero Manual Work**: Handles everything from data import to email delivery
- ✅ **AI-Powered Decisions**: Smart segmentation and content personalization
- ✅ **Real-time Processing**: Immediate response to new data and events
- ✅ **Scalable**: Handles thousands of contacts and campaigns
- ✅ **Reliable**: Database persistence and error recovery
- ✅ **Analytics-Driven**: Continuous optimization based on performance data

Give it your contact data, configure your email settings, and let the AI handle your entire email marketing strategy!
