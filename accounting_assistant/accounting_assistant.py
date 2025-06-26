"""
# Automated AI Accounting Assistant
# Purpose: Fully autonomous accounting agent that handles all tasks automatically
# Core Features:
# - Automated invoicing and payroll
# - AI-powered expense categorization
# - Scheduled tax reporting
# - Smart bank feed integration
# - Automated decision making
# - Email notifications
# - Data persistence
"""

import schedule
import time
import sqlite3
import json
import logging
import smtplib
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import requests
import pandas as pd
from threading import Thread

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('accounting_agent.log'),
        logging.StreamHandler()
    ]
)

class AutomatedAccountingAgent:
    def __init__(self):
        """Initialize the automated agent with AI capabilities and database."""
        self.invoices = []
        self.payrolls = []
        self.expenses = []
        self.bank_transactions = []
        self.tax_reports = []
        self.company_name = "Vaam"
        self.currency = "GBP"
        self.tax_rate = 0.20  # 20% VAT (example for UK)
        
        # AI and automation settings
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'email': os.getenv('EMAIL_ADDRESS'),
            'password': os.getenv('EMAIL_PASSWORD')
        }
        self.bank_api_credentials = {
            'api_key': os.getenv('BANK_API_KEY'),
            'base_url': os.getenv('BANK_API_URL')
        }
        
        # Initialize database
        self.init_database()
        
        # Load existing data
        self.load_data()
        
        # Schedule automated tasks
        self.schedule_automated_tasks()
        
        logging.info("Automated Accounting Agent initialized and ready")
    
    def init_database(self):
        """Initialize SQLite database for data persistence."""
        self.db_path = 'accounting_agent.db'
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id TEXT PRIMARY KEY,
                customer TEXT,
                items TEXT,
                due_date TEXT,
                total REAL,
                status TEXT,
                created_date TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                description TEXT,
                amount REAL,
                category TEXT,
                auto_categorized BOOLEAN
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payrolls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pay_period TEXT,
                employees TEXT,
                total_gross REAL,
                total_tax REAL,
                total_net REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bank_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                amount REAL,
                description TEXT,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        self.conn.commit()
        logging.info("Database initialized successfully")
    
    def save_to_database(self, table, data):
        """Save data to database."""
        cursor = self.conn.cursor()
        
        if table == 'invoices':
            cursor.execute('''
                INSERT OR REPLACE INTO invoices (id, customer, items, due_date, total, status, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (data['id'], data['customer'], json.dumps(data['items']), 
                  data['due_date'], data['total'], data['status'], data['created_date']))
        
        elif table == 'expenses':
            cursor.execute('''
                INSERT INTO expenses (date, description, amount, category, auto_categorized)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['date'], data['description'], data['amount'], 
                  data.get('category', 'Uncategorized'), data.get('auto_categorized', False)))
        
        self.conn.commit()
    
    def load_data(self):
        """Load existing data from database."""
        cursor = self.conn.cursor()
        
        # Load invoices
        cursor.execute('SELECT * FROM invoices')
        for row in cursor.fetchall():
            invoice = {
                'id': row[0],
                'customer': row[1],
                'items': json.loads(row[2]),
                'due_date': row[3],
                'total': row[4],
                'status': row[5],
                'created_date': row[6]
            }
            self.invoices.append(invoice)
        
        # Load expenses
        cursor.execute('SELECT * FROM expenses')
        for row in cursor.fetchall():
            expense = {
                'id': row[0],
                'date': row[1],
                'description': row[2],
                'amount': row[3],
                'category': row[4],
                'auto_categorized': row[5]
            }
            self.expenses.append(expense)        
        logging.info(f"Loaded {len(self.invoices)} invoices and {len(self.expenses)} expenses from database")
    
    def schedule_automated_tasks(self):
        """Schedule all automated tasks."""
        # Daily tasks
        schedule.every().day.at("09:00").do(self.automated_bank_sync)
        schedule.every().day.at("10:00").do(self.process_pending_invoices)
        schedule.every().day.at("18:00").do(self.send_daily_summary)
        
        # Weekly tasks
        schedule.every().monday.at("09:00").do(self.automated_payroll_processing)
        schedule.every().friday.at("17:00").do(self.generate_weekly_reports)
        
        # Monthly tasks (using day of month 1)
        schedule.every().day.at("09:00").do(self.check_monthly_tasks)
        
        logging.info("Automated tasks scheduled")
        
        # Start scheduler in separate thread
        self.scheduler_thread = Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def check_monthly_tasks(self):
        """Check if monthly tasks should run (on the 1st of the month)."""
        if datetime.now().day == 1:
            self.generate_monthly_tax_report()
            self.automated_invoice_generation()
    
    def run_scheduler(self):
        """Run the task scheduler."""
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def create_invoice(self, customer, items, due_date):
        """Generate an invoice for a customer (e.g., rider or business client)."""
        invoice_id = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        invoice = {
            'id': invoice_id,
            'company': self.company_name,
            'customer': customer,
            'items': items,
            'due_date': due_date,
            'total': sum(item['amount'] for item in items),
            'currency': self.currency,
            'status': 'pending',
            'created_date': datetime.now().isoformat()
        }
        self.invoices.append(invoice)
        self.save_to_database('invoices', invoice)
        
        # Auto-send invoice email
        self.send_invoice_email(invoice)
        
        logging.info(f"Invoice {invoice_id} created for {customer} with total £{invoice['total']}")
        return invoice

    def process_payroll(self, employees, pay_period):
        """Run payroll for drivers/employees for a given period."""
        payroll_id = f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        payroll_run = {
            'id': payroll_id,
            'pay_period': pay_period,
            'employees': [],
            'currency': self.currency,
            'created_date': datetime.now().isoformat()
        }
        
        total_gross = 0
        total_tax = 0
        total_net = 0
        
        for emp in employees:
            gross = emp['hours'] * emp['rate']
            tax = gross * self.tax_rate
            net = gross - tax
            
            total_gross += gross
            total_tax += tax
            total_net += net
            
            payroll_run['employees'].append({
                'name': emp['name'],
                'hours': emp['hours'],
                'rate': emp['rate'],
                'gross': gross,
                'tax': tax,
                'net': net
            })
        
        payroll_run['total_gross'] = total_gross
        payroll_run['total_tax'] = total_tax
        payroll_run['total_net'] = total_net
        
        self.payrolls.append(payroll_run)
        
        # Send payroll emails
        for emp_data in payroll_run['employees']:
            self.send_payroll_email(emp_data, pay_period)
        
        logging.info(f"Payroll {payroll_id} processed for period {pay_period} - Total: £{total_net}")
        return payroll_run

    def ai_categorize_expense(self, description, amount):
        """Use AI to categorize expenses automatically."""
        # Simplified AI categorization (in production, use OpenAI API)
        keywords = {
            'fuel': ['fuel', 'petrol', 'gas', 'diesel'],
            'office': ['office', 'supplies', 'stationery', 'rent'],
            'marketing': ['marketing', 'advertising', 'promotion'],
            'maintenance': ['maintenance', 'repair', 'service'],
            'insurance': ['insurance', 'coverage'],
            'meals': ['meal', 'restaurant', 'food', 'lunch', 'dinner']
        }
        
        description_lower = description.lower()
        for category, words in keywords.items():
            if any(word in description_lower for word in words):
                return category
        
        return 'miscellaneous'

    def log_expense(self, expense_data):
        """Log an expense entry with AI categorization."""
        # Auto-categorize if not provided
        if 'category' not in expense_data:
            expense_data['category'] = self.ai_categorize_expense(
                expense_data['description'], 
                expense_data['amount']
            )
            expense_data['auto_categorized'] = True
        
        expense_data['date'] = expense_data.get('date', datetime.now().strftime('%Y-%m-%d'))
        self.expenses.append(expense_data)
        self.save_to_database('expenses', expense_data)
        
        logging.info(f"Expense logged: {expense_data['description']} - £{expense_data['amount']} ({expense_data['category']})")
        return expense_data

    def generate_tax_report(self, period):
        """Generate automated tax reports for a period (UK VAT example)."""
        total_income = sum(inv['total'] for inv in self.invoices if inv.get('due_date', '').startswith(period))
        total_expenses = sum(exp['amount'] for exp in self.expenses if exp.get('date', '').startswith(period))
        vat_due = total_income * self.tax_rate - total_expenses * self.tax_rate
        
        report = {
            'period': period,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'vat_due': max(0, vat_due),  # VAT cannot be negative
            'currency': self.currency,
            'generated_date': datetime.now().isoformat()
        }
        
        self.tax_reports.append(report)
        
        # Send tax report email
        self.send_tax_report_email(report)
        
        logging.info(f"Tax report generated for {period}: VAT due £{report['vat_due']}")
        return report

    def automated_bank_sync(self):
        """Automatically sync bank transactions."""
        try:
            # Simulate API call to bank
            new_transactions = self.fetch_bank_transactions()
            
            for transaction in new_transactions:
                # Auto-process transaction
                if transaction['amount'] > 0:
                    # Income - check if it matches pending invoice
                    self.match_payment_to_invoice(transaction)
                else:
                    # Expense - auto-log
                    expense = {
                        'date': transaction['date'],
                        'description': transaction['description'],
                        'amount': abs(transaction['amount'])
                    }
                    self.log_expense(expense)
            
            logging.info(f"Bank sync completed - processed {len(new_transactions)} transactions")
        except Exception as e:
            logging.error(f"Bank sync failed: {e}")

    def fetch_bank_transactions(self):
        """Fetch new transactions from bank API (simulated)."""
        # Simulate fetching new transactions
        today = datetime.now()
        transactions = [
            {
                'date': today.strftime('%Y-%m-%d'),
                'amount': 1500,
                'description': f'Payment from Customer {today.hour}'
            },
            {
                'date': today.strftime('%Y-%m-%d'),
                'amount': -85,
                'description': f'Fuel Station {today.minute}'
            }
        ]
        return transactions

    def match_payment_to_invoice(self, transaction):
        """Match incoming payment to pending invoice."""
        for invoice in self.invoices:
            if (invoice['status'] == 'pending' and 
                abs(transaction['amount'] - invoice['total']) < 0.01):
                invoice['status'] = 'paid'
                invoice['paid_date'] = transaction['date']
                logging.info(f"Invoice {invoice['id']} marked as paid")
                break

    def send_invoice_email(self, invoice):
        """Send invoice via email."""
        try:
            if not self.email_config['email'] or not self.email_config['password']:
                logging.warning("Email credentials not configured")
                return
            
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = invoice['customer']
            msg['Subject'] = f"Invoice {invoice['id']} from {self.company_name}"
            
            body = f"""
            Dear Customer,
            
            Please find your invoice details below:
            
            Invoice ID: {invoice['id']}
            Due Date: {invoice['due_date']}
            Total Amount: £{invoice['total']}
            
            Thank you for your business.
            
            Best regards,
            {self.company_name}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Invoice email sent for {invoice['id']}")
        except Exception as e:
            logging.error(f"Failed to send invoice email: {e}")

    def send_payroll_email(self, employee_data, pay_period):
        """Send payroll slip via email."""
        try:
            if not self.email_config['email']:
                logging.warning("Email credentials not configured")
                return
            
            # In a real implementation, you'd have employee email addresses
            logging.info(f"Payroll slip generated for {employee_data['name']} - £{employee_data['net']}")
        except Exception as e:
            logging.error(f"Failed to send payroll email: {e}")

    def send_tax_report_email(self, report):
        """Send tax report via email."""
        try:
            if not self.email_config['email']:
                logging.warning("Email credentials not configured")
                return
            
            logging.info(f"Tax report for {report['period']} - VAT due: £{report['vat_due']}")
        except Exception as e:
            logging.error(f"Failed to send tax report email: {e}")

    def send_daily_summary(self):
        """Send daily summary email."""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            today_invoices = [inv for inv in self.invoices if inv.get('created_date', '').startswith(today)]
            today_expenses = [exp for exp in self.expenses if exp.get('date', '').startswith(today)]
            
            summary = {
                'date': today,
                'invoices_created': len(today_invoices),
                'total_invoiced': sum(inv['total'] for inv in today_invoices),
                'expenses_logged': len(today_expenses),
                'total_expenses': sum(exp['amount'] for exp in today_expenses)
            }
            
            logging.info(f"Daily summary: {summary}")
        except Exception as e:
            logging.error(f"Failed to generate daily summary: {e}")

    def automated_payroll_processing(self):
        """Automatically process weekly payroll."""
        try:
            # This would typically fetch employee data from a database
            # For demo purposes, using sample data
            sample_employees = [
                {'name': 'Driver 1', 'hours': 40, 'rate': 15},
                {'name': 'Driver 2', 'hours': 35, 'rate': 15},
                {'name': 'Admin Staff', 'hours': 40, 'rate': 20}
            ]
            
            today = datetime.now()
            pay_period = f"{today.strftime('%Y-%m-%d')} to {(today + timedelta(days=6)).strftime('%Y-%m-%d')}"
            
            self.process_payroll(sample_employees, pay_period)
            logging.info("Automated weekly payroll processed")
        except Exception as e:
            logging.error(f"Automated payroll processing failed: {e}")

    def automated_invoice_generation(self):
        """Generate invoices for recurring customers."""
        try:
            # Sample recurring invoice
            recurring_items = [
                {'description': 'Monthly Service Fee', 'amount': 500},
                {'description': 'Platform Usage', 'amount': 200}
            ]
            
            due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            self.create_invoice(
                customer='Recurring Customer Ltd',
                items=recurring_items,
                due_date=due_date
            )
            
            logging.info("Automated monthly invoice generated")
        except Exception as e:
            logging.error(f"Automated invoice generation failed: {e}")

    def generate_weekly_reports(self):
        """Generate weekly financial reports."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            week_invoices = [inv for inv in self.invoices 
                           if start_date.strftime('%Y-%m-%d') <= inv.get('created_date', '')[:10] <= end_date.strftime('%Y-%m-%d')]
            week_expenses = [exp for exp in self.expenses 
                           if start_date.strftime('%Y-%m-%d') <= exp.get('date', '') <= end_date.strftime('%Y-%m-%d')]
            
            report = {
                'week_ending': end_date.strftime('%Y-%m-%d'),
                'total_invoiced': sum(inv['total'] for inv in week_invoices),
                'total_expenses': sum(exp['amount'] for exp in week_expenses),
                'net_income': sum(inv['total'] for inv in week_invoices) - sum(exp['amount'] for exp in week_expenses)
            }
            
            logging.info(f"Weekly report: {report}")
        except Exception as e:
            logging.error(f"Weekly report generation failed: {e}")

    def generate_monthly_tax_report(self):
        """Generate monthly tax report automatically."""
        try:
            current_month = datetime.now().strftime('%Y-%m')
            self.generate_tax_report(current_month)
            logging.info("Automated monthly tax report generated")
        except Exception as e:
            logging.error(f"Automated tax report generation failed: {e}")

    def process_pending_invoices(self):
        """Process pending invoices - send reminders for overdue ones."""
        try:
            today = datetime.now().date()
            
            for invoice in self.invoices:
                if invoice['status'] == 'pending':
                    due_date = datetime.strptime(invoice['due_date'], '%Y-%m-%d').date()
                    days_overdue = (today - due_date).days
                    
                    if days_overdue > 0:
                        logging.info(f"Invoice {invoice['id']} is {days_overdue} days overdue")
                        # Send reminder email (implementation depends on requirements)
        except Exception as e:
            logging.error(f"Processing pending invoices failed: {e}")

    def analytics_dashboard(self):
        """Show comprehensive analytics dashboard."""
        total_invoices = sum(inv['total'] for inv in self.invoices)
        total_expenses = sum(exp['amount'] for exp in self.expenses)
        total_payroll = sum(emp['net'] for payroll in self.payrolls for emp in payroll['employees'])
        
        # Calculate monthly trends
        current_month = datetime.now().strftime('%Y-%m')
        monthly_income = sum(inv['total'] for inv in self.invoices 
                           if inv.get('created_date', '').startswith(current_month))
        monthly_expenses = sum(exp['amount'] for exp in self.expenses 
                             if exp.get('date', '').startswith(current_month))
        
        dashboard = {
            'total_invoiced': total_invoices,
            'total_expenses': total_expenses,
            'total_payroll': total_payroll,
            'net_profit': total_invoices - total_expenses - total_payroll,
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'monthly_profit': monthly_income - monthly_expenses,
            'pending_invoices': len([inv for inv in self.invoices if inv['status'] == 'pending']),
            'bank_transactions': len(self.bank_transactions)
        }
        
        print("=" * 50)
        print("    VAAM AUTOMATED ACCOUNTING DASHBOARD")
        print("=" * 50)
        print(f"Total Invoiced:        £{dashboard['total_invoiced']:,.2f}")
        print(f"Total Expenses:        £{dashboard['total_expenses']:,.2f}")
        print(f"Total Payroll:         £{dashboard['total_payroll']:,.2f}")
        print(f"Net Profit:            £{dashboard['net_profit']:,.2f}")
        print("-" * 50)
        print(f"This Month Income:     £{dashboard['monthly_income']:,.2f}")
        print(f"This Month Expenses:   £{dashboard['monthly_expenses']:,.2f}")
        print(f"This Month Profit:     £{dashboard['monthly_profit']:,.2f}")
        print("-" * 50)
        print(f"Pending Invoices:      {dashboard['pending_invoices']}")
        print(f"Bank Transactions:     {dashboard['bank_transactions']}")
        print("=" * 50)
        
        return dashboard

    def run_continuously(self):
        """Run the agent continuously with all automation enabled."""
        logging.info("🤖 Automated Accounting Agent is now running continuously...")
        logging.info("📊 Dashboard available, automated tasks scheduled")
        logging.info("🔄 Bank sync, payroll, invoicing, and reporting all automated")
        
        try:
            while True:
                # Display dashboard every hour
                if datetime.now().minute == 0:
                    self.analytics_dashboard()
                
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logging.info("Agent stopped by user")
        except Exception as e:
            logging.error(f"Agent error: {e}")
            time.sleep(60)  # Wait before restart


def main():
    """Main function to run the automated agent."""
    agent = AutomatedAccountingAgent()
    
    # Show initial dashboard
    print("\n🚀 Automated Accounting Agent Initialized!")
    agent.analytics_dashboard()
    
    # Example: Create some initial data for demonstration
    sample_invoice_items = [
        {'description': 'Delivery Services - Week 1', 'amount': 850},
        {'description': 'Platform Fee', 'amount': 150}
    ]
    
    due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    agent.create_invoice('Sample Customer Ltd', sample_invoice_items, due_date)
    
    # Log some sample expenses
    sample_expenses = [
        {'description': 'Vehicle Fuel', 'amount': 120},
        {'description': 'Office Supplies', 'amount': 45},
        {'description': 'Insurance Payment', 'amount': 300}
    ]
    
    for expense in sample_expenses:
        agent.log_expense(expense)
    
    print("\n📈 Sample data created. Agent is now running autonomously...")
    print("🔄 All tasks (banking, payroll, invoicing, reporting) are automated")
    print("⏰ Scheduled tasks will run automatically")
    print("📧 Email notifications enabled (configure SMTP settings)")
    
    # Run continuously
    agent.run_continuously()


if __name__ == "__main__":
    main()
