"""
Enterprise Integration Example
Shows how to integrate the Intelligent OTP Agent with external systems
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Simulate external integrations
class ExternalSystemIntegrations:
    """Simulates integration with various external systems."""
    
    def __init__(self, otp_agent):
        self.otp_agent = otp_agent
        self.running = False
    
    def start_integrations(self):
        """Start all integration services."""
        self.running = True
        
        # Start various integration threads
        threading.Thread(target=self.user_registration_monitor, daemon=True).start()
        threading.Thread(target=self.order_system_integration, daemon=True).start()
        threading.Thread(target=self.security_alerts_monitor, daemon=True).start()
        threading.Thread(target=self.payment_system_integration, daemon=True).start()
        
        print("🔗 External system integrations started")
    
    def stop_integrations(self):
        """Stop all integration services."""
        self.running = False
        print("⏹️ External system integrations stopped")
    
    def user_registration_monitor(self):
        """Monitor user registrations and send welcome messages."""
        while self.running:
            try:
                # Simulate fetching new user registrations
                new_users = self.fetch_new_registrations()
                
                for user in new_users:
                    # Send welcome OTP
                    self.otp_agent.send_otp(
                        phone_number=user['phone'],
                        user_id=user['user_id']
                    )
                    
                    # Send welcome message
                    from otp_messaging_agent import MessageRequest, Priority
                    welcome_msg = MessageRequest(
                        phone_number=user['phone'],
                        message_type='notification',
                        content=f"Welcome {user['name']}! Your account is ready.",
                        priority=Priority.MEDIUM,
                        preferred_channel='WhatsApp',
                        user_id=user['user_id']
                    )
                    self.otp_agent.send_message(welcome_msg)
                    
                    print(f"📝 Processed new user registration: {user['name']}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"❌ Error in user registration monitor: {e}")
                time.sleep(60)
    
    def order_system_integration(self):
        """Monitor order updates and send notifications."""
        while self.running:
            try:
                # Simulate fetching order updates
                order_updates = self.fetch_order_updates()
                
                for order in order_updates:
                    from otp_messaging_agent import MessageRequest, Priority
                    
                    if order['status'] == 'shipped':
                        message = f"Great news! Your order #{order['order_id']} has been shipped. Track: {order['tracking_code']}"
                        priority = Priority.MEDIUM
                        channel = 'SMS'
                    elif order['status'] == 'delivered':
                        message = f"Your order #{order['order_id']} has been delivered. Enjoy!"
                        priority = Priority.LOW
                        channel = 'WhatsApp'
                    elif order['status'] == 'delayed':
                        message = f"We apologize - your order #{order['order_id']} is delayed. New ETA: {order['new_eta']}"
                        priority = Priority.HIGH
                        channel = 'SMS'
                    else:
                        continue
                    
                    order_msg = MessageRequest(
                        phone_number=order['customer_phone'],
                        message_type='notification',
                        content=message,
                        priority=priority,
                        preferred_channel=channel,
                        user_id=order['customer_id']
                    )
                    self.otp_agent.send_message(order_msg)
                    
                    print(f"📦 Sent order update for #{order['order_id']}: {order['status']}")
                
                time.sleep(45)  # Check every 45 seconds
                
            except Exception as e:
                print(f"❌ Error in order system integration: {e}")
                time.sleep(60)
    
    def security_alerts_monitor(self):
        """Monitor security events and send alerts."""
        while self.running:
            try:
                # Simulate fetching security alerts
                security_events = self.fetch_security_events()
                
                for event in security_events:
                    from otp_messaging_agent import MessageRequest, Priority
                    
                    if event['type'] == 'suspicious_login':
                        message = f"SECURITY ALERT: Suspicious login attempt from {event['location']} at {event['time']}. If this wasn't you, secure your account immediately."
                        priority = Priority.CRITICAL
                        channel = 'Call'  # Use call for critical security alerts
                    elif event['type'] == 'password_change':
                        message = f"Your password was changed at {event['time']}. If you didn't make this change, contact support immediately."
                        priority = Priority.HIGH
                        channel = 'SMS'
                    elif event['type'] == 'new_device':
                        message = f"New device login detected: {event['device']} from {event['location']}. Was this you?"
                        priority = Priority.HIGH
                        channel = 'SMS'
                    else:
                        continue
                    
                    security_msg = MessageRequest(
                        phone_number=event['user_phone'],
                        message_type='alert',
                        content=message,
                        priority=priority,
                        preferred_channel=channel,
                        user_id=event['user_id']
                    )
                    self.otp_agent.send_message(security_msg)
                    
                    print(f"🚨 Sent security alert for user {event['user_id']}: {event['type']}")
                
                time.sleep(20)  # Check every 20 seconds for security events
                
            except Exception as e:
                print(f"❌ Error in security alerts monitor: {e}")
                time.sleep(60)
    
    def payment_system_integration(self):
        """Monitor payment events and send confirmations."""
        while self.running:
            try:
                # Simulate fetching payment events
                payment_events = self.fetch_payment_events()
                
                for payment in payment_events:
                    from otp_messaging_agent import MessageRequest, Priority
                    
                    if payment['status'] == 'success':
                        message = f"Payment confirmed! ${payment['amount']} charged to your {payment['method']}. Transaction ID: {payment['transaction_id']}"
                        priority = Priority.MEDIUM
                    elif payment['status'] == 'failed':
                        message = f"Payment failed for ${payment['amount']}. Reason: {payment['failure_reason']}. Please try again."
                        priority = Priority.HIGH
                    elif payment['status'] == 'refund':
                        message = f"Refund processed: ${payment['amount']} will appear in your account within 3-5 business days."
                        priority = Priority.MEDIUM
                    else:
                        continue
                    
                    payment_msg = MessageRequest(
                        phone_number=payment['customer_phone'],
                        message_type='notification',
                        content=message,
                        priority=priority,
                        preferred_channel='SMS',
                        user_id=payment['customer_id']
                    )
                    self.otp_agent.send_message(payment_msg)
                    
                    print(f"💳 Sent payment notification for transaction {payment['transaction_id']}: {payment['status']}")
                
                time.sleep(35)  # Check every 35 seconds
                
            except Exception as e:
                print(f"❌ Error in payment system integration: {e}")
                time.sleep(60)
    
    # Simulation methods (in real implementation, these would call actual APIs)
    def fetch_new_registrations(self) -> List[Dict[str, Any]]:
        """Simulate fetching new user registrations."""
        import random
        
        if random.random() < 0.3:  # 30% chance of new registration
            return [{
                'user_id': f'user_{int(time.time())}',
                'name': f'User{random.randint(1000, 9999)}',
                'phone': f'+44770090{random.randint(1000, 9999)}',
                'email': f'user{random.randint(1000, 9999)}@example.com',
                'registration_time': datetime.now().isoformat()
            }]
        return []
    
    def fetch_order_updates(self) -> List[Dict[str, Any]]:
        """Simulate fetching order status updates."""
        import random
        
        if random.random() < 0.4:  # 40% chance of order update
            statuses = ['shipped', 'delivered', 'delayed']
            status = random.choice(statuses)
            
            return [{
                'order_id': f'ORD{random.randint(10000, 99999)}',
                'customer_id': f'user_{random.randint(1000, 9999)}',
                'customer_phone': f'+44770090{random.randint(1000, 9999)}',
                'status': status,
                'tracking_code': f'TRK{random.randint(100000, 999999)}' if status == 'shipped' else None,
                'new_eta': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d') if status == 'delayed' else None,
                'update_time': datetime.now().isoformat()
            }]
        return []
    
    def fetch_security_events(self) -> List[Dict[str, Any]]:
        """Simulate fetching security events."""
        import random
        
        if random.random() < 0.2:  # 20% chance of security event
            event_types = ['suspicious_login', 'password_change', 'new_device']
            event_type = random.choice(event_types)
            
            return [{
                'user_id': f'user_{random.randint(1000, 9999)}',
                'user_phone': f'+44770090{random.randint(1000, 9999)}',
                'type': event_type,
                'location': random.choice(['London, UK', 'New York, US', 'Paris, FR', 'Tokyo, JP']),
                'device': random.choice(['iPhone 15', 'Samsung Galaxy', 'MacBook Pro', 'Windows PC']),
                'time': datetime.now().strftime('%H:%M'),
                'event_time': datetime.now().isoformat()
            }]
        return []
    
    def fetch_payment_events(self) -> List[Dict[str, Any]]:
        """Simulate fetching payment events."""
        import random
        
        if random.random() < 0.25:  # 25% chance of payment event
            statuses = ['success', 'failed', 'refund']
            status = random.choice(statuses)
            
            return [{
                'transaction_id': f'TXN{random.randint(100000, 999999)}',
                'customer_id': f'user_{random.randint(1000, 9999)}',
                'customer_phone': f'+44770090{random.randint(1000, 9999)}',
                'status': status,
                'amount': round(random.uniform(10.0, 500.0), 2),
                'method': random.choice(['Visa ****1234', 'MasterCard ****5678', 'PayPal']),
                'failure_reason': 'Insufficient funds' if status == 'failed' else None,
                'payment_time': datetime.now().isoformat()
            }]
        return []

def demo_enterprise_integration():
    """Demonstrate enterprise-level automated integrations."""
    from otp_messaging_agent import IntelligentOTPAgent
    
    print("🏢 ENTERPRISE INTEGRATION DEMO")
    print("=" * 50)
    
    # Initialize the agent
    agent = IntelligentOTPAgent()
    agent.start_processing()
    
    # Initialize integrations
    integrations = ExternalSystemIntegrations(agent)
    integrations.start_integrations()
    
    print("🚀 All systems are now running in fully automated mode!")
    print("\n📋 Active integrations:")
    print("  🔐 User Registration Monitor - Sends welcome OTPs and messages")
    print("  📦 Order System Integration - Sends shipping and delivery updates")
    print("  🚨 Security Alerts Monitor - Sends critical security notifications")
    print("  💳 Payment System Integration - Sends payment confirmations")
    print("\n💡 The system will now automatically process events from all integrated systems")
    print("⏱️  Demo will run for 2 minutes to show real-time processing...")
    
    try:
        # Let the demo run for 2 minutes
        time.sleep(120)
        
        # Show final metrics
        print("\n📊 Final System Metrics:")
        metrics = agent.get_metrics()
        print(f"  Total messages processed: {metrics['runtime_metrics']['total_sent']}")
        print(f"  Success rate: {metrics['database_stats']['success_rate']}")
        print(f"  Channel distribution:")
        for channel, stats in metrics['runtime_metrics']['channel_stats'].items():
            if stats['sent'] > 0:
                print(f"    {channel}: {stats['sent']} sent, {stats['delivered']} delivered")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    
    finally:
        # Cleanup
        print("\n🧹 Shutting down integrations...")
        integrations.stop_integrations()
        agent.stop_processing()
        
        print("✅ Enterprise integration demo completed!")

if __name__ == "__main__":
    demo_enterprise_integration()
