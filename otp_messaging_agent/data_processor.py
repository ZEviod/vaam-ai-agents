"""
Data processing utilities for the Intelligent OTP Agent
Handles data from various sources and formats
"""

import json
import csv
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any
from otp_messaging_agent import IntelligentOTPAgent, MessageRequest, Priority

class DataProcessor:
    """Processes data from various sources for automated messaging."""
    
    def __init__(self, agent: IntelligentOTPAgent):
        self.agent = agent
    
    def process_csv_file(self, csv_file_path: str, phone_column: str = "phone", 
                        message_column: str = "message", priority_column: str = "priority") -> int:
        """Process messages from CSV file."""
        messages_processed = 0
        
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    if phone_column not in row:
                        continue
                    
                    # Parse priority
                    priority = Priority.MEDIUM
                    if priority_column in row and row[priority_column]:
                        try:
                            priority = Priority[row[priority_column].upper()]
                        except KeyError:
                            pass
                    
                    # Create message request
                    message_request = MessageRequest(
                        phone_number=row[phone_column],
                        message_type=row.get('type', 'notification'),
                        content=row.get(message_column, ''),
                        priority=priority,
                        preferred_channel=row.get('channel', 'SMS'),
                        user_id=row.get('user_id', ''),
                        callback_url=row.get('callback_url', '')
                    )
                    
                    self.agent.send_message(message_request)
                    messages_processed += 1
                    
        except Exception as e:
            print(f"Error processing CSV file: {e}")
        
        return messages_processed
    
    def process_database_query(self, db_path: str, query: str, 
                             phone_field: str = "phone", message_field: str = "message") -> int:
        """Process messages from database query results."""
        messages_processed = 0
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                
                columns = [description[0] for description in cursor.description]
                
                for row in cursor.fetchall():
                    row_dict = dict(zip(columns, row))
                    
                    if phone_field not in row_dict:
                        continue
                    
                    # Parse priority
                    priority = Priority.MEDIUM
                    if 'priority' in row_dict and row_dict['priority']:
                        try:
                            priority = Priority[row_dict['priority'].upper()]
                        except (KeyError, AttributeError):
                            pass
                    
                    # Parse scheduled_for
                    scheduled_for = None
                    if 'scheduled_for' in row_dict and row_dict['scheduled_for']:
                        try:
                            scheduled_for = datetime.fromisoformat(row_dict['scheduled_for'])
                        except (ValueError, TypeError):
                            pass
                    
                    message_request = MessageRequest(
                        phone_number=row_dict[phone_field],
                        message_type=row_dict.get('type', 'notification'),
                        content=row_dict.get(message_field, ''),
                        priority=priority,
                        preferred_channel=row_dict.get('channel', 'SMS'),
                        scheduled_for=scheduled_for,
                        user_id=row_dict.get('user_id', ''),
                        callback_url=row_dict.get('callback_url', '')
                    )
                    
                    self.agent.send_message(message_request)
                    messages_processed += 1
                    
        except Exception as e:
            print(f"Error processing database query: {e}")
        
        return messages_processed
    
    def process_api_data(self, api_data: List[Dict[str, Any]]) -> int:
        """Process messages from API response data."""
        messages_processed = 0
        
        for item in api_data:
            try:
                # Parse priority
                priority = Priority.MEDIUM
                if 'priority' in item and item['priority']:
                    try:
                        priority = Priority[item['priority'].upper()]
                    except KeyError:
                        pass
                
                # Parse scheduled_for
                scheduled_for = None
                if 'scheduled_for' in item and item['scheduled_for']:
                    try:
                        scheduled_for = datetime.fromisoformat(item['scheduled_for'])
                    except ValueError:
                        pass
                
                message_request = MessageRequest(
                    phone_number=item['phone_number'],
                    message_type=item.get('message_type', 'notification'),
                    content=item.get('content', ''),
                    priority=priority,
                    preferred_channel=item.get('preferred_channel', 'SMS'),
                    max_retries=item.get('max_retries', 3),
                    scheduled_for=scheduled_for,
                    callback_url=item.get('callback_url', ''),
                    user_id=item.get('user_id', '')
                )
                
                self.agent.send_message(message_request)
                messages_processed += 1
                
            except KeyError:
                print(f"Missing required field 'phone_number' in item: {item}")
                continue
            except Exception as e:
                print(f"Error processing item {item}: {e}")
                continue
        
        return messages_processed
    
    def schedule_recurring_messages(self, template: Dict[str, Any], 
                                  phone_numbers: List[str], 
                                  interval_hours: int = 24) -> List[str]:
        """Schedule recurring messages for multiple recipients."""
        message_ids = []
        
        for i, phone in enumerate(phone_numbers):
            scheduled_time = datetime.now() + timedelta(hours=interval_hours * i)
            
            message_request = MessageRequest(
                phone_number=phone,
                message_type=template.get('message_type', 'notification'),
                content=template.get('content', ''),
                priority=Priority[template.get('priority', 'MEDIUM').upper()],
                preferred_channel=template.get('preferred_channel', 'SMS'),
                scheduled_for=scheduled_time,
                callback_url=template.get('callback_url', ''),
                user_id=template.get('user_id', '')
            )
            
            message_id = self.agent.send_message(message_request)
            message_ids.append(message_id)
        
        return message_ids
    
    def process_webhook_data(self, webhook_payload: Dict[str, Any]) -> bool:
        """Process incoming webhook data for automated responses."""
        try:
            event_type = webhook_payload.get('event_type', '')
            
            if event_type == 'user_signup':
                # Send welcome message
                message_request = MessageRequest(
                    phone_number=webhook_payload['phone_number'],
                    message_type='notification',
                    content='Welcome! Your account has been successfully created.',
                    priority=Priority.MEDIUM,
                    user_id=webhook_payload.get('user_id', '')
                )
                self.agent.send_message(message_request)
                
            elif event_type == 'password_reset':
                # Send OTP for password reset
                self.agent.send_otp(
                    phone_number=webhook_payload['phone_number'],
                    user_id=webhook_payload.get('user_id', '')
                )
                
            elif event_type == 'security_alert':
                # Send critical security alert
                message_request = MessageRequest(
                    phone_number=webhook_payload['phone_number'],
                    message_type='alert',
                    content=webhook_payload.get('message', 'Security alert detected'),
                    priority=Priority.CRITICAL,
                    preferred_channel='Call',
                    user_id=webhook_payload.get('user_id', '')
                )
                self.agent.send_message(message_request)
                
            elif event_type == 'order_shipped':
                # Send shipping notification
                message_request = MessageRequest(
                    phone_number=webhook_payload['phone_number'],
                    message_type='notification',
                    content=f"Your order #{webhook_payload.get('order_id', 'N/A')} has been shipped!",
                    priority=Priority.LOW,
                    preferred_channel='WhatsApp',
                    user_id=webhook_payload.get('user_id', '')
                )
                self.agent.send_message(message_request)
            
            return True
            
        except Exception as e:
            print(f"Error processing webhook data: {e}")
            return False

# Example usage functions
def demo_csv_processing():
    """Demonstrate CSV file processing."""
    # Create sample CSV
    sample_csv = """phone,message,priority,type,channel
+447700900001,Welcome to our service!,MEDIUM,notification,SMS
+447700900002,Your account is ready,HIGH,alert,WhatsApp
+447700900003,Order confirmation,LOW,notification,Email"""
    
    with open('sample_messages.csv', 'w') as f:
        f.write(sample_csv)
    
    # Process with agent
    agent = IntelligentOTPAgent()
    agent.start_processing()
    
    processor = DataProcessor(agent)
    count = processor.process_csv_file('sample_messages.csv')
    
    print(f"Processed {count} messages from CSV")
    
    agent.stop_processing()

def demo_scheduled_messages():
    """Demonstrate scheduled recurring messages."""
    agent = IntelligentOTPAgent()
    agent.start_processing()
    
    processor = DataProcessor(agent)
    
    # Schedule welcome series
    template = {
        'message_type': 'notification',
        'content': 'Day {day}: Welcome to our service! Here are some tips...',
        'priority': 'MEDIUM',
        'preferred_channel': 'WhatsApp'
    }
    
    phone_numbers = ['+447700900001', '+447700900002', '+447700900003']
    
    message_ids = processor.schedule_recurring_messages(template, phone_numbers, interval_hours=24)
    print(f"Scheduled {len(message_ids)} recurring messages")
    
    agent.stop_processing()

def demo_webhook_processing():
    """Demonstrate webhook data processing."""
    agent = IntelligentOTPAgent()
    agent.start_processing()
    
    processor = DataProcessor(agent)
    
    # Simulate various webhook events
    events = [
        {
            'event_type': 'user_signup',
            'phone_number': '+447700900001',
            'user_id': 'user123'
        },
        {
            'event_type': 'password_reset',
            'phone_number': '+447700900002',
            'user_id': 'user456'
        },
        {
            'event_type': 'security_alert',
            'phone_number': '+447700900003',
            'message': 'Suspicious login from new device',
            'user_id': 'user789'
        }
    ]
    
    for event in events:
        success = processor.process_webhook_data(event)
        print(f"Processed {event['event_type']}: {success}")
    
    agent.stop_processing()

if __name__ == "__main__":
    print("🔄 Data Processing Utilities Demo")
    print("=" * 40)
    
    print("\n1. CSV Processing Demo")
    demo_csv_processing()
    
    print("\n2. Scheduled Messages Demo")
    demo_scheduled_messages()
    
    print("\n3. Webhook Processing Demo")
    demo_webhook_processing()
    
    print("\n✅ All demos completed!")
