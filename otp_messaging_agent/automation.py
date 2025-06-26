"""
Automation orchestrator for the Intelligent OTP Agent
Handles scheduled tasks, data integration, and automated workflows
"""

import time
import json
import schedule
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List
import requests
import os

from otp_messaging_agent import IntelligentOTPAgent, MessageRequest, Priority
from data_processor import DataProcessor
from monitor import AgentMonitor

class AutomationOrchestrator:
    """Orchestrates automated workflows for the OTP Agent."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        self.agent = IntelligentOTPAgent(
            db_path=self.config.get('agent_config', {}).get('database_path', 'otp_agent.db'),
            max_workers=self.config.get('agent_config', {}).get('max_workers', 10)
        )
        self.data_processor = DataProcessor(self.agent)
        self.monitor = AgentMonitor(self.agent)
        self.running = False
        self.scheduler_thread = None
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Config file {config_file} not found, using defaults")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing config file: {e}")
            return {}
    
    def start(self):
        """Start the automation orchestrator."""
        if self.running:
            print("⚠️  Orchestrator is already running")
            return
        
        print("🚀 Starting Intelligent OTP Agent Automation Orchestrator")
        
        # Start the agent
        self.agent.start_processing()
        
        # Start monitoring
        self.monitor.start_monitoring()
        
        # Schedule automated tasks
        self._setup_scheduled_tasks()
        
        # Start scheduler thread
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        print("✅ Orchestrator started successfully")
        
    def stop(self):
        """Stop the automation orchestrator."""
        if not self.running:
            print("⚠️  Orchestrator is not running")
            return
        
        print("⏹️ Stopping automation orchestrator...")
        
        self.running = False
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        
        # Stop agent
        self.agent.stop_processing()
        
        # Wait for scheduler thread
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        print("✅ Orchestrator stopped")
    
    def _setup_scheduled_tasks(self):
        """Set up scheduled automated tasks."""
        # Data processing tasks
        schedule.every(5).minutes.do(self._process_pending_data)
        schedule.every(15).minutes.do(self._fetch_external_data)
        schedule.every().hour.do(self._process_scheduled_messages)
        
        # Maintenance tasks
        schedule.every().day.at("02:00").do(self._daily_cleanup)
        schedule.every().day.at("06:00").do(self._export_daily_metrics)
        schedule.every().week.do(self._weekly_maintenance)
        
        # Monitoring tasks
        schedule.every(10).minutes.do(self._check_system_health)
        
        print("📅 Scheduled tasks configured:")
        print("  - Process pending data: Every 5 minutes")
        print("  - Fetch external data: Every 15 minutes")
        print("  - Process scheduled messages: Every hour")
        print("  - Daily cleanup: 02:00")
        print("  - Export metrics: 06:00")
        print("  - Weekly maintenance: Weekly")
        print("  - Health check: Every 10 minutes")
    
    def _run_scheduler(self):
        """Run the task scheduler."""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                time.sleep(5)
    
    def _process_pending_data(self):
        """Process any pending data files or queues."""
        try:
            # Check for JSON files in data directory
            data_dir = "data/incoming"
            if os.path.exists(data_dir):
                for filename in os.listdir(data_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(data_dir, filename)
                        count = self.agent.load_messages_from_json(file_path)
                        
                        if count > 0:
                            print(f"📥 Processed {count} messages from {filename}")
                            # Move processed file
                            processed_dir = "data/processed"
                            os.makedirs(processed_dir, exist_ok=True)
                            os.rename(file_path, os.path.join(processed_dir, filename))
                        
            # Check for CSV files
            if os.path.exists(data_dir):
                for filename in os.listdir(data_dir):
                    if filename.endswith('.csv'):
                        file_path = os.path.join(data_dir, filename)
                        count = self.data_processor.process_csv_file(file_path)
                        
                        if count > 0:
                            print(f"📥 Processed {count} messages from {filename}")
                            # Move processed file
                            processed_dir = "data/processed"
                            os.makedirs(processed_dir, exist_ok=True)
                            os.rename(file_path, os.path.join(processed_dir, filename))
                            
        except Exception as e:
            print(f"❌ Error processing pending data: {e}")
    
    def _fetch_external_data(self):
        """Fetch data from external APIs."""
        try:
            api_configs = self.config.get('external_apis', [])
            
            for api_config in api_configs:
                if not api_config.get('enabled', True):
                    continue
                
                url = api_config['url']
                headers = api_config.get('headers', {})
                
                print(f"🌐 Fetching data from {url}")
                
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # Process the fetched data
                if isinstance(data, list):
                    count = self.data_processor.process_api_data(data)
                    print(f"📥 Processed {count} messages from external API")
                    
        except Exception as e:
            print(f"❌ Error fetching external data: {e}")
    
    def _process_scheduled_messages(self):
        """Process any scheduled messages that are due."""
        try:
            # This is handled automatically by the agent's queue processor
            # But we can add additional logic here if needed
            metrics = self.agent.get_metrics()
            queue_size = metrics['queue_size']
            
            if queue_size > 0:
                print(f"⏰ Processing {queue_size} scheduled messages")
                
        except Exception as e:
            print(f"❌ Error processing scheduled messages: {e}")
    
    def _daily_cleanup(self):
        """Perform daily cleanup tasks."""
        try:
            print("🧹 Performing daily cleanup...")
            
            # Clean old records
            cleanup_days = self.config.get('agent_config', {}).get('auto_cleanup_days', 30)
            result = self.agent.auto_cleanup(older_than_days=cleanup_days)
            
            print(f"🗑️ Cleanup completed: {result}")
            
            # Clean old log files
            self._cleanup_old_files("logs", days=7)
            self._cleanup_old_files("data/processed", days=30)
            
        except Exception as e:
            print(f"❌ Error during daily cleanup: {e}")
    
    def _export_daily_metrics(self):
        """Export daily metrics report."""
        try:
            print("📊 Exporting daily metrics...")
            
            # Export metrics
            filename = self.monitor.export_metrics()
            
            # Get agent metrics
            metrics = self.agent.get_metrics()
            
            # Create daily report
            report = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'summary': {
                    'total_messages': metrics['database_stats']['total_messages'],
                    'success_rate': metrics['database_stats']['success_rate'],
                    'queue_size': metrics['queue_size'],
                    'agent_status': 'running' if self.agent.is_running else 'stopped'
                },
                'channel_performance': metrics['runtime_metrics']['channel_stats']
            }
            
            report_filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"📄 Daily report saved: {report_filename}")
            
        except Exception as e:
            print(f"❌ Error exporting daily metrics: {e}")
    
    def _weekly_maintenance(self):
        """Perform weekly maintenance tasks."""
        try:
            print("🔧 Performing weekly maintenance...")
            
            # Database optimization
            import sqlite3
            with sqlite3.connect(self.agent.db_path) as conn:
                conn.execute('VACUUM')
                conn.execute('ANALYZE')
            
            print("✅ Database optimization completed")
            
            # Generate weekly performance report
            metrics = self.agent.get_metrics()
            
            weekly_report = {
                'week_ending': datetime.now().strftime('%Y-%m-%d'),
                'performance_summary': metrics,
                'recommendations': self._generate_recommendations(metrics)
            }
            
            report_filename = f"weekly_report_{datetime.now().strftime('%Y%W')}.json"
            with open(report_filename, 'w') as f:
                json.dump(weekly_report, f, indent=2)
            
            print(f"📊 Weekly report generated: {report_filename}")
            
        except Exception as e:
            print(f"❌ Error during weekly maintenance: {e}")
    
    def _check_system_health(self):
        """Check system health and alert if needed."""
        try:
            metrics = self.agent.get_metrics()
            
            # Check if agent is running
            if not self.agent.is_running:
                print("🚨 ALERT: Agent is not running!")
                return
            
            # Check success rate
            if 'database_stats' in metrics:
                success_rate_str = metrics['database_stats']['success_rate']
                success_rate = float(success_rate_str.replace('%', '')) / 100
                
                if success_rate < 0.9:  # Alert if success rate < 90%
                    print(f"⚠️  WARNING: Low success rate: {success_rate_str}")
            
            # Check queue size
            queue_size = metrics['queue_size']
            if queue_size > 1000:  # Alert if queue too large
                print(f"⚠️  WARNING: Large queue size: {queue_size}")
            
        except Exception as e:
            print(f"❌ Error during health check: {e}")
    
    def _cleanup_old_files(self, directory: str, days: int = 30):
        """Clean up old files in a directory."""
        if not os.path.exists(directory):
            return
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff_time:
                try:
                    os.remove(filepath)
                    print(f"🗑️ Removed old file: {filepath}")
                except Exception as e:
                    print(f"❌ Error removing file {filepath}: {e}")
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations based on metrics."""
        recommendations = []
        
        # Check channel performance
        channel_stats = metrics['runtime_metrics']['channel_stats']
        for channel, stats in channel_stats.items():
            if stats['sent'] > 0:
                success_rate = stats['delivered'] / stats['sent']
                if success_rate < 0.8:
                    recommendations.append(f"Consider reviewing {channel} channel configuration - low success rate: {success_rate:.1%}")
        
        # Check overall performance
        total_sent = metrics['runtime_metrics']['total_sent']
        total_delivered = metrics['runtime_metrics']['total_delivered']
        
        if total_sent > 0:
            overall_success = total_delivered / total_sent
            if overall_success < 0.9:
                recommendations.append("Overall delivery rate is below 90% - consider reviewing retry strategies")
        
        # Check queue performance
        queue_size = metrics['queue_size']
        if queue_size > 100:
            recommendations.append("Queue size is high - consider increasing worker threads or checking for bottlenecks")
        
        return recommendations
    
    def add_webhook_handler(self, event_type: str, phone_number: str, data: Dict[str, Any]):
        """Handle incoming webhook events."""
        try:
            success = self.data_processor.process_webhook_data({
                'event_type': event_type,
                'phone_number': phone_number,
                **data
            })
            
            if success:
                print(f"✅ Processed webhook event: {event_type} for {phone_number}")
            else:
                print(f"❌ Failed to process webhook event: {event_type}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error handling webhook: {e}")
            return False

def main():
    """Main function to run the automation orchestrator."""
    orchestrator = AutomationOrchestrator()
    
    try:
        # Start the orchestrator
        orchestrator.start()
        
        print("\n🤖 Intelligent OTP Agent is now running in fully automated mode!")
        print("📋 Available operations:")
        print("  - Automatic data processing from files")
        print("  - Scheduled message delivery")
        print("  - Real-time monitoring and alerts")
        print("  - Automated cleanup and maintenance")
        print("  - Performance optimization")
        print("\n💡 To add messages, simply drop JSON/CSV files in the 'data/incoming' directory")
        print("📊 Metrics are automatically exported daily")
        print("🔧 System maintenance runs automatically")
        print("\n⏹️  Press Ctrl+C to stop the orchestrator\n")
        
        # Create directories if they don't exist
        os.makedirs("data/incoming", exist_ok=True)
        os.makedirs("data/processed", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Run indefinitely
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Shutting down orchestrator...")
        orchestrator.stop()
        print("✅ Shutdown complete")

if __name__ == "__main__":
    # Install required package for scheduling
    try:
        import schedule
    except ImportError:
        print("📦 Installing required package: schedule")
        import subprocess
        subprocess.check_call(["pip", "install", "schedule"])
        import schedule
    
    main()
