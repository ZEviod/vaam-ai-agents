"""
# AI-Powered Email Campaign Agent
# Purpose: Fully automated email marketing agent that intelligently processes data and sends targeted campaigns
# AI Features:
# - Intelligent data processing and segmentation
# - AI-powered email content generation
# - Automated campaign optimization
# - Smart scheduling based on user behavior
# - Real-time analytics and performance tracking
# - Event-driven automation (triggers, workflows)
# - A/B testing and optimization
"""

import smtplib
import json
import csv
import threading
import time
import schedule
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import sqlite3
from pathlib import Path

# AI-powered data models and configurations
@dataclass
class EmailContact:
    """Contact data model with enhanced fields for AI segmentation"""
    email: str
    name: str = ""
    age: int = 0
    city: str = ""
    country: str = ""
    segment: str = ""
    preferences: Dict[str, Any] = None
    engagement_score: float = 0.0
    last_interaction: Optional[datetime] = None
    custom_fields: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}
        if self.custom_fields is None:
            self.custom_fields = {}

@dataclass
class CampaignConfig:
    """Campaign configuration with AI optimization settings"""
    name: str
    template_name: str
    subject_line: str
    target_segments: List[str]
    send_time: Optional[datetime] = None
    frequency: str = "once"  # once, daily, weekly, monthly
    ab_test: bool = False
    optimization_goal: str = "engagement"  # engagement, clicks, conversions
    auto_optimize: bool = True
    max_recipients_per_hour: int = 100

@dataclass
class AutomationRule:
    """Event-driven automation rules"""
    name: str
    trigger_event: str  # new_user, inactive_user, purchase, etc.
    conditions: Dict[str, Any]
    action_template: str
    delay_hours: int = 0
    active: bool = True

class AIEmailCampaignAgent:
    def __init__(self, config_file: str = "config.json"):
        """Initialize the AI Email Campaign Agent with configuration"""
        self.config_file = config_file
        self.setup_logging()
        self.load_configuration()
        self.init_database()
        self.contacts: Dict[str, EmailContact] = {}
        self.campaigns: Dict[str, CampaignConfig] = {}
        self.automation_rules: List[AutomationRule] = []
        self.running = False
        self.scheduler_thread = None
        
        # Initialize AI-powered templates first
        self.init_ai_templates()
        self.templates = self.load_templates()
        
        # Load initial data
        self.load_contacts_from_data()
        
    def init_ai_templates(self):
        self.ai_templates = {
            'welcome': {
                'subject': 'Welcome to {{company_name}}, {{name}}!',
                'content': '''
                Hi {{name}},
                
                Welcome to {{company_name}}! We're thrilled to have you join our community.
                
                Based on your interests in {{preferences}}, we think you'll love:
                {{personalized_recommendations}}
                
                Get started today and enjoy your journey with us!
                
                Best regards,
                The {{company_name}} Team
                '''
            },
            'engagement': {
                'subject': "We miss you, {{name}}! Here's something special",
                'content': '''
                Hi {{name}},
                
                We noticed you haven't been active lately. Here's a special offer just for you:
                
                {{special_offer}}
                
                Valid until {{expiry_date}}. Don't miss out!
                
                Come back and see what's new!
                
                Best regards,
                The {{company_name}} Team
                '''
            },
            'newsletter': {
                'subject': '{{company_name}} Weekly Update - {{date}}',
                'content': '''
                Hi {{name}},
                
                Here's what's happening this week:
                
                {{newsletter_content}}
                
                {{personalized_section}}
                
                Stay tuned for more updates!
                
                Best regards,
                The {{company_name}} Team
                '''
            }
        }
        
        # Load initial data
        self.load_contacts_from_data()
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('email_agent.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_configuration(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Create default configuration
            self.config = {
                "smtp": {
                    "server": "smtp.gmail.com",
                    "port": 587,
                    "username": "",
                    "password": "",
                    "use_tls": True
                },
                "company": {
                    "name": "Your Company",
                    "email": "noreply@company.com",
                    "website": "https://company.com"
                },
                "ai_settings": {
                    "auto_segment": True,
                    "auto_optimize": True,
                    "personalization_level": "high",
                    "send_time_optimization": True
                },
                "rate_limits": {
                    "emails_per_hour": 100,
                    "emails_per_day": 1000
                }
            }
            self.save_configuration()
            
    def save_configuration(self):
        """Save configuration to JSON file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def init_database(self):
        """Initialize SQLite database for persistent storage"""
        self.db_path = "email_agent.db"
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_tables()
        
    def create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        # Contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                email TEXT PRIMARY KEY,
                name TEXT,
                age INTEGER,
                city TEXT,
                country TEXT,
                segment TEXT,
                preferences TEXT,
                engagement_score REAL,
                last_interaction TEXT,
                custom_fields TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                name TEXT,
                template_name TEXT,
                subject_line TEXT,
                target_segments TEXT,
                send_time TEXT,
                frequency TEXT,
                ab_test BOOLEAN,
                optimization_goal TEXT,
                auto_optimize BOOLEAN,
                status TEXT,
                created_at TEXT,
                sent_count INTEGER DEFAULT 0,
                opened_count INTEGER DEFAULT 0,
                clicked_count INTEGER DEFAULT 0
            )
        ''')
        
        # Automation rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_rules (
                id TEXT PRIMARY KEY,
                name TEXT,
                trigger_event TEXT,
                conditions TEXT,
                action_template TEXT,
                delay_hours INTEGER,
                active BOOLEAN,
                created_at TEXT
            )
        ''')
        
        # Email logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT,
                recipient_email TEXT,
                subject TEXT,
                sent_at TEXT,
                opened_at TEXT,
                clicked_at TEXT,
                status TEXT
            )
        ''')
        
        self.conn.commit()
        
    def load_templates(self):
        """Load email templates from file or use defaults"""
        templates_file = "templates.json"
        try:
            with open(templates_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.ai_templates.copy()
            
    def load_contacts_from_data(self):
        """Load contacts from various data sources"""
        # Try to load from CSV file
        csv_files = list(Path('.').glob('*.csv'))
        for csv_file in csv_files:
            try:
                self.import_contacts_from_csv(str(csv_file))
                break
            except Exception as e:
                self.logger.warning(f"Could not load {csv_file}: {e}")
                
        # Try to load from JSON file
        json_files = [f for f in Path('.').glob('*.json') if f.name != self.config_file]
        for json_file in json_files:
            try:
                self.import_contacts_from_json(str(json_file))
                break
            except Exception as e:
                self.logger.warning(f"Could not load {json_file}: {e}")
                
        # Load from database
        self.load_contacts_from_db()
        
    def import_contacts_from_csv(self, file_path: str):
        """Import contacts from CSV file"""
        df = pd.read_csv(file_path)
        
        for _, row in df.iterrows():
            contact = EmailContact(
                email=row.get('email', ''),
                name=row.get('name', ''),
                age=int(row.get('age', 0)),
                city=row.get('city', ''),
                country=row.get('country', ''),
                segment=row.get('segment', ''),
                preferences=json.loads(row.get('preferences', '{}')) if row.get('preferences') else {},
                engagement_score=float(row.get('engagement_score', 0.0)),
                custom_fields=json.loads(row.get('custom_fields', '{}')) if row.get('custom_fields') else {}
            )
            
            if contact.email:
                self.contacts[contact.email] = contact
                self.save_contact_to_db(contact)
                
        self.logger.info(f"Imported {len(df)} contacts from {file_path}")
        
    def import_contacts_from_json(self, file_path: str):
        """Import contacts from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        if isinstance(data, list):
            contacts_data = data
        elif isinstance(data, dict) and 'contacts' in data:
            contacts_data = data['contacts']
        else:
            contacts_data = [data]
            
        for contact_data in contacts_data:
            contact = EmailContact(**contact_data)
            if contact.email:
                self.contacts[contact.email] = contact
                self.save_contact_to_db(contact)
                
        self.logger.info(f"Imported {len(contacts_data)} contacts from {file_path}")
        
    def save_contact_to_db(self, contact: EmailContact):
        """Save contact to database"""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO contacts 
            (email, name, age, city, country, segment, preferences, engagement_score, 
             last_interaction, custom_fields, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            contact.email, contact.name, contact.age, contact.city, contact.country,
            contact.segment, json.dumps(contact.preferences), contact.engagement_score,
            contact.last_interaction.isoformat() if contact.last_interaction else None,
            json.dumps(contact.custom_fields), now, now
        ))
        
        self.conn.commit()
        
    def load_contacts_from_db(self):
        """Load contacts from database"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM contacts')
        
        for row in cursor.fetchall():
            contact = EmailContact(
                email=row[0],
                name=row[1],
                age=row[2],
                city=row[3],
                country=row[4],
                segment=row[5],
                preferences=json.loads(row[6]) if row[6] else {},
                engagement_score=row[7],
                last_interaction=datetime.fromisoformat(row[8]) if row[8] else None,
                custom_fields=json.loads(row[9]) if row[9] else {}
            )
            self.contacts[contact.email] = contact
            
    def ai_segment_contacts(self) -> Dict[str, List[EmailContact]]:
        """AI-powered contact segmentation"""
        segments = {
            'new_users': [],
            'active_users': [],
            'inactive_users': [],
            'high_value': [],
            'low_engagement': [],
            'geographic_london': [],
            'age_young': [],
            'age_middle': [],
            'age_senior': []
        }
        
        now = datetime.now()
        
        for contact in self.contacts.values():
            # New users (no last interaction or very recent)
            if not contact.last_interaction or (now - contact.last_interaction).days <= 7:
                segments['new_users'].append(contact)
                
            # Active vs inactive users
            if contact.last_interaction and (now - contact.last_interaction).days <= 30:
                segments['active_users'].append(contact)
            elif contact.last_interaction and (now - contact.last_interaction).days > 60:
                segments['inactive_users'].append(contact)
                
            # Engagement-based segmentation
            if contact.engagement_score >= 7.0:
                segments['high_value'].append(contact)
            elif contact.engagement_score <= 3.0:
                segments['low_engagement'].append(contact)
                
            # Geographic segmentation
            if contact.city.lower() == 'london':
                segments['geographic_london'].append(contact)
                
            # Age-based segmentation
            if contact.age <= 25:
                segments['age_young'].append(contact)
            elif 26 <= contact.age <= 45:
                segments['age_middle'].append(contact)
            elif contact.age > 45:
                segments['age_senior'].append(contact)
                
        return segments
        
    def generate_personalized_content(self, template: str, contact: EmailContact) -> Dict[str, str]:
        """AI-powered content personalization"""
        placeholders = {
            'name': contact.name or contact.email.split('@')[0],
            'company_name': self.config['company']['name'],
            'city': contact.city,
            'country': contact.country,
            'date': datetime.now().strftime('%B %d, %Y')
        }
        
        # Generate personalized recommendations based on preferences
        if contact.preferences:
            prefs = ", ".join(contact.preferences.keys())
            placeholders['preferences'] = prefs
            placeholders['personalized_recommendations'] = f"Services tailored to your interests in {prefs}"
        else:
            placeholders['preferences'] = "your interests"
            placeholders['personalized_recommendations'] = "Our most popular services"
            
        # Generate special offers based on engagement score
        if contact.engagement_score < 5.0:
            placeholders['special_offer'] = "50% off your next booking - We want you back!"
        else:
            placeholders['special_offer'] = "20% off premium services - For our valued customers"
            
        placeholders['expiry_date'] = (datetime.now() + timedelta(days=7)).strftime('%B %d, %Y')
        
        # Generate personalized newsletter content
        if contact.segment == 'drivers':
            placeholders['newsletter_content'] = "• New driver bonuses available\n• Traffic updates for your routes\n• Driver community highlights"
            placeholders['personalized_section'] = f"Tips for drivers in {contact.city}"
        elif contact.segment == 'riders':
            placeholders['newsletter_content'] = "• New ride options in your area\n• Exclusive rider discounts\n• Safety updates"
            placeholders['personalized_section'] = f"Popular destinations from {contact.city}"
        else:
            placeholders['newsletter_content'] = "• Platform updates\n• New features\n• Community highlights"
            placeholders['personalized_section'] = "Personalized updates for you"
            
        return placeholders
        
    def create_campaign(self, config: CampaignConfig) -> str:
        """Create a new email campaign"""
        campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.campaigns[campaign_id] = config
        
        # Save to database
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO campaigns 
            (id, name, template_name, subject_line, target_segments, send_time, 
             frequency, ab_test, optimization_goal, auto_optimize, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            campaign_id, config.name, config.template_name, config.subject_line,
            json.dumps(config.target_segments), 
            config.send_time.isoformat() if config.send_time else None,
            config.frequency, config.ab_test, config.optimization_goal,
            config.auto_optimize, 'created', datetime.now().isoformat()
                ))        
        self.conn.commit()
        self.logger.info(f"Created campaign: {campaign_id}")
        return campaign_id
    
        def add_automation_rule(self, rule: AutomationRule):
            """Add automation rule"""
            rule_id = f"rule_{uuid.uuid4().hex[:8]}"
            self.automation_rules.append(rule)
            
            # Save to database
            cursor = self.conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO automation_rules 
                    (id, name, trigger_event, conditions, action_template, delay_hours, active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    rule_id, rule.name, rule.trigger_event, json.dumps(rule.conditions),
                    rule.action_template, rule.delay_hours, rule.active, datetime.now().isoformat()
                ))
                
                self.conn.commit()
                self.logger.info(f"Added automation rule: {rule.name}")
            except sqlite3.IntegrityError:
                self.logger.warning(f"Automation rule already exists: {rule.name}")
                return None
        
    def send_email(self, contact: EmailContact, subject: str, content: str, campaign_id: str = None):
        """Send individual email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['smtp']['username']
            msg['To'] = contact.email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(content, 'html'))
            
            with smtplib.SMTP(self.config['smtp']['server'], self.config['smtp']['port']) as server:
                if self.config['smtp']['use_tls']:
                    server.starttls()
                server.login(self.config['smtp']['username'], self.config['smtp']['password'])
                server.send_message(msg)
                
            # Log the email
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO email_logs (campaign_id, recipient_email, subject, sent_at, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (campaign_id, contact.email, subject, datetime.now().isoformat(), 'sent'))
            
            self.conn.commit()
            self.logger.info(f"Email sent successfully to {contact.email}")
            
            # Update contact interaction
            contact.last_interaction = datetime.now()
            self.save_contact_to_db(contact)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email to {contact.email}: {e}")
            
            # Log the failure
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO email_logs (campaign_id, recipient_email, subject, sent_at, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (campaign_id, contact.email, subject, datetime.now().isoformat(), f'failed: {str(e)}'))
            
            self.conn.commit()
            return False
            
    def execute_campaign(self, campaign_id: str):
        """Execute a campaign"""
        if campaign_id not in self.campaigns:
            self.logger.error(f"Campaign {campaign_id} not found")
            return
            
        campaign = self.campaigns[campaign_id]
        segments = self.ai_segment_contacts()
        
        # Get target contacts
        target_contacts = []
        for segment_name in campaign.target_segments:
            if segment_name in segments:
                target_contacts.extend(segments[segment_name])
                
        if not target_contacts:
            self.logger.warning(f"No contacts found for campaign {campaign_id}")
            return
            
        # Get template
        if campaign.template_name not in self.templates:
            self.logger.error(f"Template {campaign.template_name} not found")
            return
            
        template = self.templates[campaign.template_name]
        sent_count = 0
        
        for contact in target_contacts:
            # Rate limiting
            if sent_count >= campaign.max_recipients_per_hour:
                self.logger.info(f"Rate limit reached for campaign {campaign_id}")
                break
                
            # Generate personalized content
            placeholders = self.generate_personalized_content(campaign.template_name, contact)
            
            # Replace placeholders in subject and content
            subject = campaign.subject_line
            content = template['content']
            
            for key, value in placeholders.items():
                subject = subject.replace(f'{{{{{key}}}}}', str(value))
                content = content.replace(f'{{{{{key}}}}}', str(value))
                
            # Send email
            if self.send_email(contact, subject, content, campaign_id):
                sent_count += 1
                
            # Small delay to avoid overwhelming the SMTP server
            time.sleep(0.1)
            
        # Update campaign stats
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE campaigns SET sent_count = ?, status = ? WHERE id = ?
        ''', (sent_count, 'completed', campaign_id))
        
        self.conn.commit()
        self.logger.info(f"Campaign {campaign_id} completed. Sent {sent_count} emails.")
        
    def check_automation_triggers(self):
        """Check and execute automation rules"""
        for rule in self.automation_rules:
            if not rule.active:
                continue
                
            # Check trigger conditions
            if rule.trigger_event == 'new_user':
                # Find new users (added in last 24 hours)
                new_contacts = [
                    contact for contact in self.contacts.values()
                    if not contact.last_interaction or 
                    (datetime.now() - contact.last_interaction).days <= 1
                ]
                
                for contact in new_contacts:
                    if self.matches_conditions(contact, rule.conditions):
                        self.execute_automation(contact, rule)
                        
            elif rule.trigger_event == 'inactive_user':
                # Find inactive users
                inactive_contacts = [
                    contact for contact in self.contacts.values()
                    if contact.last_interaction and 
                    (datetime.now() - contact.last_interaction).days > 30
                ]
                
                for contact in inactive_contacts:
                    if self.matches_conditions(contact, rule.conditions):
                        self.execute_automation(contact, rule)
                        
    def matches_conditions(self, contact: EmailContact, conditions: Dict[str, Any]) -> bool:
        """Check if contact matches automation conditions"""
        for key, value in conditions.items():
            if key == 'segment' and contact.segment != value:
                return False
            elif key == 'city' and contact.city.lower() != value.lower():
                return False
            elif key == 'engagement_score_min' and contact.engagement_score < value:
                return False
            elif key == 'engagement_score_max' and contact.engagement_score > value:
                return False
                
        return True
        
    def execute_automation(self, contact: EmailContact, rule: AutomationRule):
        """Execute automation rule for a contact"""
        if rule.delay_hours > 0:
            # Schedule for later
            threading.Timer(
                rule.delay_hours * 3600,
                self.send_automation_email,
                args=[contact, rule.action_template]
            ).start()
        else:
            # Send immediately
            self.send_automation_email(contact, rule.action_template)
            
    def send_automation_email(self, contact: EmailContact, template_name: str):
        """Send automation email"""
        if template_name not in self.templates:
            self.logger.error(f"Automation template {template_name} not found")
            return
            
        template = self.templates[template_name]
        placeholders = self.generate_personalized_content(template_name, contact)
        
        subject = template['subject']
        content = template['content']
        
        for key, value in placeholders.items():
            subject = subject.replace(f'{{{{{key}}}}}', str(value))
            content = content.replace(f'{{{{{key}}}}}', str(value))
            
        self.send_email(contact, subject, content, f"automation_{template_name}")
        
    def start_automation(self):
        """Start the automation engine"""
        self.running = True
        
        def automation_loop():
            while self.running:
                try:
                    self.check_automation_triggers()
                    
                    # Check for scheduled campaigns
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        SELECT id, send_time FROM campaigns 
                        WHERE status = 'created' AND send_time <= ?
                    ''', (datetime.now().isoformat(),))
                    
                    for campaign_id, send_time in cursor.fetchall():
                        self.execute_campaign(campaign_id)
                        
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    self.logger.error(f"Error in automation loop: {e}")
                    time.sleep(60)
                    
        self.scheduler_thread = threading.Thread(target=automation_loop, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("Automation engine started")
        
    def stop_automation(self):
        """Stop the automation engine"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        self.logger.info("Automation engine stopped")
        
    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics"""
        cursor = self.conn.cursor()
        
        # Campaign statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_campaigns,
                SUM(sent_count) as total_emails_sent,
                SUM(opened_count) as total_opens,
                SUM(clicked_count) as total_clicks
            FROM campaigns
        ''')
        
        campaign_stats = cursor.fetchone()
        
        # Recent activity
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM email_logs
            WHERE sent_at > datetime('now', '-7 days')
            GROUP BY status
        ''')
        
        recent_activity = dict(cursor.fetchall())
        
        # Segment distribution
        segments = self.ai_segment_contacts()
        segment_stats = {name: len(contacts) for name, contacts in segments.items()}
        
        return {
            'total_contacts': len(self.contacts),
            'total_campaigns': campaign_stats[0] or 0,
            'total_emails_sent': campaign_stats[1] or 0,
            'total_opens': campaign_stats[2] or 0,
            'total_clicks': campaign_stats[3] or 0,
            'open_rate': (campaign_stats[2] / campaign_stats[1] * 100) if campaign_stats[1] else 0,
            'click_rate': (campaign_stats[3] / campaign_stats[1] * 100) if campaign_stats[1] else 0,
            'recent_activity': recent_activity,
            'segment_distribution': segment_stats,
            'automation_rules': len(self.automation_rules)
        }
        
    def add_contact(self, contact_data: Dict[str, Any]):
        """Add a new contact"""
        contact = EmailContact(**contact_data)
        self.contacts[contact.email] = contact
        self.save_contact_to_db(contact)
        self.logger.info(f"Added new contact: {contact.email}")
        
        # Trigger new user automation
        self.check_automation_triggers()
        
    def bulk_import(self, file_path: str):
        """Bulk import contacts from file"""
        if file_path.endswith('.csv'):
            self.import_contacts_from_csv(file_path)
        elif file_path.endswith('.json'):
            self.import_contacts_from_json(file_path)
        else:
            raise ValueError("Unsupported file format. Use CSV or JSON.")

def main():
    """Main function demonstrating the AI Email Campaign Agent"""
    agent = AIEmailCampaignAgent()
    
    # Example: Add some sample data
    sample_contacts = [
        {
            'email': 'driver1@vaam.com',
            'name': 'John Driver',
            'age': 30,
            'city': 'London',
            'segment': 'drivers',
            'preferences': {'notifications': True, 'bonuses': True},
            'engagement_score': 8.5
        },
        {
            'email': 'rider1@vaam.com',
            'name': 'Sarah Rider',
            'age': 25,
            'city': 'London',
            'segment': 'riders',
            'preferences': {'discounts': True, 'safety': True},
            'engagement_score': 7.2
        },
        {
            'email': 'inactive@vaam.com',
            'name': 'Tom Inactive',
            'age': 35,
            'city': 'London',
            'segment': 'riders',
            'engagement_score': 2.1,
            'last_interaction': datetime.now() - timedelta(days=45)
        }
    ]
    
    # Add contacts
    for contact_data in sample_contacts:
        agent.add_contact(contact_data)
    
    # Create automation rules
    welcome_rule = AutomationRule(
        name="Welcome New Users",
        trigger_event="new_user",
        conditions={},
        action_template="welcome",
        delay_hours=1
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
    
    # Create a campaign
    campaign_config = CampaignConfig(
        name="Weekly Newsletter",
        template_name="newsletter",
        subject_line="Your Weekly VAAM Update",
        target_segments=["active_users", "high_value"],
        send_time=datetime.now() + timedelta(minutes=1),
        frequency="weekly",
        auto_optimize=True
    )
    
    campaign_id = agent.create_campaign(campaign_config)
    
    # Start automation
    agent.start_automation()
    
    # Print analytics
    print("\n=== AI Email Campaign Agent Analytics ===")
    analytics = agent.get_analytics()
    for key, value in analytics.items():
        print(f"{key}: {value}")
    
    print("\n=== Available Commands ===")
    print("1. Add contact: agent.add_contact({'email': 'test@example.com', 'name': 'Test User'})")
    print("2. Create campaign: agent.create_campaign(campaign_config)")
    print("3. Bulk import: agent.bulk_import('contacts.csv')")
    print("4. Get analytics: agent.get_analytics()")
    print("5. Start automation: agent.start_automation()")
    print("6. Stop automation: agent.stop_automation()")
    
    print("\n=== Configuration Setup ===")
    print("To send real emails, update config.json with your SMTP settings:")
    config_example = {
        "smtp": {
            "server": "smtp.gmail.com",
            "port": 587,
            "username": "your-email@gmail.com",
            "password": "your-app-password",
            "use_tls": True
        }
    }
    print(json.dumps(config_example, indent=2))
    
    # Keep running for demonstration
    try:
        print("\nAgent is running... Press Ctrl+C to stop.")
        while True:
            time.sleep(10)
            # Show live stats every 10 seconds
            stats = agent.get_analytics()
            print(f"Live Stats - Contacts: {stats['total_contacts']}, "
                  f"Campaigns: {stats['total_campaigns']}, "
                  f"Emails Sent: {stats['total_emails_sent']}")
    except KeyboardInterrupt:
        print("\nStopping agent...")
        agent.stop_automation()
        print("Agent stopped.")

if __name__ == "__main__":
    main()
