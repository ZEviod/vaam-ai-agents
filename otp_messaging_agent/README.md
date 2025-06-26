# Intelligent OTP Messaging Agent

A fully automated AI-powered messaging agent that handles OTP delivery, notifications, and alerts with intelligent routing and self-healing capabilities.

## Features

🤖 **Fully Automated Processing**

- Automatic queue processing with priority handling
- Background threading for non-blocking operations
- Intelligent channel selection based on message priority and cost

📱 **Multi-Channel Support**

- SMS (via Twilio)
- WhatsApp (via Twilio)
- Voice Calls (via Twilio)
- Email (via SendGrid)

🧠 **AI-Driven Intelligence**

- Automatic fallback routing when channels fail
- Rate limiting and cost optimization
- Exponential backoff retry logic
- Channel selection based on reliability and cost

🔄 **Robust Processing**

- Persistent SQLite database for reliability
- Automatic cleanup of old records
- Delivery reports and status tracking
- Webhook callbacks for external integrations

📊 **Real-time Monitoring**

- Live metrics and analytics
- Success/failure rate tracking
- Channel performance statistics
- Queue monitoring

## Quick Start

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

2. **Configure the Agent**
   Edit `config.json` with your API credentials:

```json
{
  "channels": {
    "SMS": {
      "api_config": {
        "account_sid": "YOUR_TWILIO_ACCOUNT_SID",
        "auth_token": "YOUR_TWILIO_AUTH_TOKEN"
      }
    }
  }
}
```

3. **Run the Agent**

```python
from otp_messaging_agent import IntelligentOTPAgent, MessageRequest, Priority

# Initialize and start the agent
agent = IntelligentOTPAgent()
agent.start_processing()

# Send an OTP
message_id = agent.send_otp("+447700900123", user_id="user123")

# Send bulk messages
messages = [
    MessageRequest(
        phone_number="+447700900124",
        message_type="alert",
        content="Security alert!",
        priority=Priority.CRITICAL
    )
]
agent.send_bulk_messages(messages)

# Load from JSON file
agent.load_messages_from_json("sample_messages.json")
```

## Automated Data Processing

The agent can automatically process data from various sources:

### From JSON Files

```python
# Automatically load and process messages
count = agent.load_messages_from_json("messages.json")
print(f"Processed {count} messages")
```

### From External APIs

```python
import requests

# Fetch data from external API
response = requests.get("https://api.yourapp.com/pending-messages")
messages = response.json()

# Convert to MessageRequest objects and process
for msg_data in messages:
    request = MessageRequest(
        phone_number=msg_data["phone"],
        message_type=msg_data["type"],
        content=msg_data.get("content", ""),
        priority=Priority[msg_data.get("priority", "MEDIUM")]
    )
    agent.send_message(request)
```

### Scheduled Processing

```python
from datetime import datetime, timedelta

# Schedule messages for future delivery
future_time = datetime.now() + timedelta(hours=2)
request = MessageRequest(
    phone_number="+447700900125",
    message_type="reminder",
    content="Don't forget your appointment!",
    scheduled_for=future_time
)
agent.send_message(request)
```

## Message Types

1. **OTP Messages** - Automatically generates and sends OTP codes
2. **Alerts** - Critical security or system alerts
3. **Notifications** - General user notifications
4. **Reminders** - Scheduled reminder messages

## Priority Levels

- **CRITICAL** - Uses most reliable channel (Call)
- **HIGH** - Uses SMS for fast delivery
- **MEDIUM** - Uses WhatsApp for cost efficiency
- **LOW** - Uses Email for lowest cost

## Intelligent Features

### Automatic Channel Selection

The agent automatically selects the best channel based on:

- Message priority
- Channel reliability
- Cost optimization
- Rate limiting
- Previous success rates

### Self-Healing Delivery

- Automatic retry with exponential backoff
- Fallback to alternative channels
- Real-time status monitoring
- Error tracking and recovery

### Rate Limiting

- Per-channel rate limiting
- Automatic queue management
- Cost optimization
- Load balancing

## Monitoring and Analytics

Get real-time metrics:

```python
metrics = agent.get_metrics()
print(f"Success Rate: {metrics['database_stats']['success_rate']}")
print(f"Queue Size: {metrics['queue_size']}")
```

## Database Schema

The agent uses SQLite with three main tables:

- `messages` - All message records with status tracking
- `otps` - OTP codes with expiry times
- `delivery_reports` - Detailed delivery information

## API Integration

Verify OTPs programmatically:

```python
success, message = agent.verify_otp("+447700900123", "123456")
if success:
    print("OTP verified successfully!")
else:
    print(f"Verification failed: {message}")
```

Get delivery reports:

```python
report = agent.get_delivery_report(message_id)
if report:
    print(f"Status: {report.status}")
    print(f"Channel: {report.channel}")
    print(f"Attempts: {report.attempts}")
```

## Configuration

The agent is highly configurable via `config.json`:

- Channel settings and API credentials
- Rate limits and costs
- Retry strategies
- Fallback logic
- Monitoring settings

## Production Deployment

For production use:

1. Set up proper API credentials in `config.json`
2. Configure webhook endpoints for callbacks
3. Set up monitoring and alerting
4. Consider using PostgreSQL for larger scale
5. Implement proper security measures

## License

MIT License - feel free to use in your projects!
