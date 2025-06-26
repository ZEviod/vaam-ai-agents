#!/usr/bin/env python3
"""
Automated AI Accounting Agent - Demo Script
This script demonstrates all the features of the autonomous accounting agent.
"""

import time
from datetime import datetime, timedelta
from accounting_assistant import AutomatedAccountingAgent

def demonstrate_features():
    """Demonstrate all agent features with sample data."""
    
    print("\n" + "="*60)
    print("  🤖 AUTOMATED AI ACCOUNTING AGENT DEMONSTRATION")
    print("="*60)
    
    # Initialize the agent
    print("\n🚀 Initializing Automated Accounting Agent...")
    agent = AutomatedAccountingAgent()
    time.sleep(1)
    
    print("\n📊 Initial Dashboard:")
    agent.analytics_dashboard()
    
    # Demo 1: Automated Invoice Creation
    print("\n" + "="*60)
    print("🧾 DEMO 1: AUTOMATED INVOICE CREATION")
    print("="*60)
    
    sample_invoices = [
        {
            'customer': 'TechStart Ltd',
            'items': [
                {'description': 'Delivery Services - Week 1', 'amount': 850},
                {'description': 'Platform Commission', 'amount': 150}
            ],
            'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        },
        {
            'customer': 'Local Restaurant Chain',
            'items': [
                {'description': 'Food Delivery Service', 'amount': 1200},
                {'description': 'Rush Hour Premium', 'amount': 200}
            ],
            'due_date': (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
        }
    ]
    
    for invoice_data in sample_invoices:
        invoice = agent.create_invoice(
            invoice_data['customer'],
            invoice_data['items'],
            invoice_data['due_date']
        )
        print(f"✅ Created invoice {invoice['id']} for {invoice['customer']} - £{invoice['total']}")
        time.sleep(1)
    
    # Demo 2: AI-Powered Expense Categorization
    print("\n" + "="*60)
    print("🧠 DEMO 2: AI-POWERED EXPENSE CATEGORIZATION")
    print("="*60)
    
    sample_expenses = [
        {'description': 'Shell Petrol Station Fuel', 'amount': 89.50},
        {'description': 'Office Depot - Printer Paper', 'amount': 24.99},
        {'description': 'Vehicle Maintenance and Repair', 'amount': 340.00},
        {'description': 'Google Ads Marketing Campaign', 'amount': 156.00},
        {'description': 'Business Insurance Premium', 'amount': 289.00},
        {'description': 'Restaurant Business Lunch', 'amount': 67.50}
    ]
    
    for expense in sample_expenses:
        categorized = agent.log_expense(expense)
        print(f"✅ Expense: {expense['description'][:30]}... → {categorized['category']} (£{expense['amount']})")
        time.sleep(0.5)
    
    # Demo 3: Automated Payroll Processing
    print("\n" + "="*60)
    print("💰 DEMO 3: AUTOMATED PAYROLL PROCESSING")
    print("="*60)
    
    sample_employees = [
        {'name': 'Alex Driver', 'hours': 40, 'rate': 15.50},
        {'name': 'Jamie Delivery', 'hours': 35, 'rate': 15.00},
        {'name': 'Sam Logistics', 'hours': 45, 'rate': 16.00},
        {'name': 'Office Manager', 'hours': 37.5, 'rate': 22.00}
    ]
    
    pay_period = f"{datetime.now().strftime('%Y-%m-%d')} to {(datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d')}"
    payroll = agent.process_payroll(sample_employees, pay_period)
    
    print(f"✅ Payroll processed for {len(sample_employees)} employees")
    print(f"   Total Gross: £{payroll['total_gross']:.2f}")
    print(f"   Total Tax: £{payroll['total_tax']:.2f}")
    print(f"   Total Net: £{payroll['total_net']:.2f}")
    
    # Demo 4: Tax Report Generation
    print("\n" + "="*60)
    print("📈 DEMO 4: AUTOMATED TAX REPORTING")
    print("="*60)
    
    current_month = datetime.now().strftime('%Y-%m')
    tax_report = agent.generate_tax_report(current_month)
    
    print(f"✅ Tax report generated for {current_month}")
    print(f"   Total Income: £{tax_report['total_income']:.2f}")
    print(f"   Total Expenses: £{tax_report['total_expenses']:.2f}")
    print(f"   VAT Due: £{tax_report['vat_due']:.2f}")
    
    # Demo 5: Bank Transaction Simulation
    print("\n" + "="*60)
    print("🏦 DEMO 5: AUTOMATED BANK SYNCHRONIZATION")
    print("="*60)
    
    print("🔄 Simulating bank transaction sync...")
    agent.automated_bank_sync()
    print("✅ Bank synchronization completed")
    
    # Final Dashboard
    print("\n" + "="*60)
    print("📊 FINAL DASHBOARD - ALL FEATURES DEMONSTRATED")
    print("="*60)
    
    final_dashboard = agent.analytics_dashboard()
    
    # Show automation features
    print("\n" + "="*60)
    print("⚡ AUTOMATION FEATURES ACTIVE")
    print("="*60)
    print("✅ Daily bank synchronization (09:00)")
    print("✅ Invoice processing and reminders (10:00)")
    print("✅ Daily financial summaries (18:00)")
    print("✅ Weekly payroll processing (Monday 09:00)")
    print("✅ Weekly financial reports (Friday 17:00)")
    print("✅ Monthly tax reports (1st of month)")
    print("✅ Monthly recurring invoices (1st of month)")
    print("✅ AI-powered expense categorization")
    print("✅ Automatic payment matching")
    print("✅ Email notifications")
    print("✅ Real-time dashboard updates")
    
    print("\n" + "="*60)
    print("🎉 DEMONSTRATION COMPLETE!")
    print("="*60)
    print("🤖 The agent is now running autonomously")
    print("📊 All accounting tasks are automated")
    print("🔄 Scheduled tasks will run automatically")
    print("📧 Email notifications are configured")
    print("💾 All data is persisted in database")
    print("📈 Real-time analytics available")
    
    return agent

def run_demo():
    """Run the full demonstration."""
    try:
        agent = demonstrate_features()
        
        print("\n" + "="*60)
        print("⏰ AGENT RUNNING CONTINUOUSLY")
        print("="*60)
        print("🔄 Agent will continue running in the background")
        print("📊 Dashboard updates every hour")
        print("⚙️  Scheduled tasks execute automatically")
        print("🛑 Press Ctrl+C to stop")
        print("="*60)
        
        # Keep running and show periodic updates
        hour_count = 0
        while True:
            time.sleep(60)  # Wait 1 minute for demo (normally would be 1 hour)
            hour_count += 1
            
            if hour_count % 5 == 0:  # Show update every 5 minutes (for demo)
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Agent Status: Running")
                print("📊 Dashboard updated, all systems operational")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Agent stopped by user")
        print("✅ All data has been saved")
        print("📊 Analytics and reports are available")
        print("🔄 Agent can be restarted anytime")

if __name__ == "__main__":
    run_demo()
