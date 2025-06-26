#!/usr/bin/env python3
"""
Quick test to show your auto_messages.json being processed
"""

from otp_messaging_agent import IntelligentOTPAgent
import time
import json

print("🤖 Processing your auto_messages.json file...")
print("=" * 50)

# Initialize agent
agent = IntelligentOTPAgent()
agent.start_processing()

# Load your file
count = agent.load_messages_from_json('data/incoming/auto_messages.json')
print(f"📥 Loaded {count} messages from auto_messages.json")

# Wait for processing
print("⏳ Processing messages...")
time.sleep(6)

# Show results
metrics = agent.get_metrics()
print("\n📊 Processing Results:")
print(f"  Messages sent: {metrics['runtime_metrics']['total_sent']}")
print(f"  Messages delivered: {metrics['runtime_metrics']['total_delivered']}")
print(f"  Success rate: {metrics['database_stats']['success_rate']}")
print(f"  Queue size: {metrics['queue_size']}")

# Show channel distribution
print("\n📱 Channel Usage:")
for channel, stats in metrics['runtime_metrics']['channel_stats'].items():
    if stats['sent'] > 0:
        print(f"  {channel}: {stats['sent']} sent, {stats['delivered']} delivered")

# Show what was in your file
print("\n📄 Your Message Data:")
with open('data/incoming/auto_messages.json', 'r') as f:
    data = json.load(f)
    for i, msg in enumerate(data, 1):
        print(f"  Message {i}: {msg['message_type']} to {msg['phone_number']}")

print("\n✅ Your messages have been processed automatically!")
print("💡 In production, this would send real OTPs and notifications")

agent.stop_processing()
