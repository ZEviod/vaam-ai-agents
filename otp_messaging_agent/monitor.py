"""
Real-time monitoring dashboard for the Intelligent OTP Agent
Provides live metrics, alerts, and performance monitoring
"""

import time
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List
import threading
from otp_messaging_agent import IntelligentOTPAgent

class AgentMonitor:
    """Real-time monitoring for the OTP Agent."""
    
    def __init__(self, agent: IntelligentOTPAgent, update_interval: int = 30):
        self.agent = agent
        self.update_interval = update_interval
        self.monitoring = False
        self.alert_thresholds = {
            'failure_rate': 0.1,  # Alert if >10% failure rate
            'queue_size': 100,    # Alert if queue >100 messages
            'response_time': 5.0  # Alert if avg response time >5s
        }
        self.alerts = []
        self.historical_data = []
    
    def start_monitoring(self):
        """Start the monitoring process."""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        print("📊 Agent monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring process."""
        self.monitoring = False
        print("⏹️ Agent monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                metrics = self._collect_metrics()
                self._check_alerts(metrics)
                self._store_historical_data(metrics)
                self._display_dashboard(metrics)
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(self.update_interval)
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current metrics from the agent."""
        base_metrics = self.agent.get_metrics()
        
        # Additional computed metrics
        total_sent = base_metrics['runtime_metrics']['total_sent']
        total_failed = base_metrics['runtime_metrics']['total_failed']
        
        failure_rate = (total_failed / total_sent) if total_sent > 0 else 0
        success_rate = 1 - failure_rate
        
        # Channel performance
        channel_performance = {}
        for channel, stats in base_metrics['runtime_metrics']['channel_stats'].items():
            sent = stats['sent']
            delivered = stats['delivered']
            channel_success_rate = (delivered / sent) if sent > 0 else 0
            channel_performance[channel] = {
                'success_rate': channel_success_rate,
                'total_sent': sent,
                'total_delivered': delivered,
                'total_failed': stats['failed']
            }
        
        # Database performance metrics
        db_metrics = self._get_database_metrics()
        
        enhanced_metrics = {
            **base_metrics,
            'computed_metrics': {
                'failure_rate': failure_rate,
                'success_rate': success_rate,
                'channel_performance': channel_performance,
                'avg_processing_time': self._get_avg_processing_time(),
                'messages_per_minute': self._get_messages_per_minute()
            },
            'database_metrics': db_metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        return enhanced_metrics
    
    def _get_database_metrics(self) -> Dict[str, Any]:
        """Get database performance metrics."""
        try:
            with sqlite3.connect(self.agent.db_path) as conn:
                cursor = conn.cursor()
                
                # Recent activity (last 24 hours)
                since = datetime.now() - timedelta(hours=24)
                
                cursor.execute('''
                    SELECT COUNT(*) FROM messages 
                    WHERE created_at > ?
                ''', (since,))
                recent_messages = cursor.fetchone()[0]
                
                cursor.execute('''
                    SELECT COUNT(*) FROM messages 
                    WHERE created_at > ? AND status = 'delivered'
                ''', (since,))
                recent_delivered = cursor.fetchone()[0]
                
                cursor.execute('''
                    SELECT COUNT(*) FROM messages 
                    WHERE created_at > ? AND status = 'failed'
                ''', (since,))
                recent_failed = cursor.fetchone()[0]
                
                # Pending messages
                cursor.execute('''
                    SELECT COUNT(*) FROM messages 
                    WHERE status = 'pending'
                ''')
                pending_messages = cursor.fetchone()[0]
                
                # Active OTPs
                cursor.execute('''
                    SELECT COUNT(*) FROM otps 
                    WHERE expiry > ?
                ''', (datetime.now(),))
                active_otps = cursor.fetchone()[0]
                
                return {
                    'recent_24h': {
                        'total_messages': recent_messages,
                        'delivered': recent_delivered,
                        'failed': recent_failed,
                        'success_rate': (recent_delivered / recent_messages) if recent_messages > 0 else 0
                    },
                    'pending_messages': pending_messages,
                    'active_otps': active_otps
                }
                
        except Exception as e:
            print(f"Error getting database metrics: {e}")
            return {}
    
    def _get_avg_processing_time(self) -> float:
        """Calculate average message processing time."""
        try:
            with sqlite3.connect(self.agent.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT AVG(
                        (julianday(delivered_at) - julianday(created_at)) * 24 * 60 * 60
                    ) as avg_seconds
                    FROM messages 
                    WHERE delivered_at IS NOT NULL 
                    AND created_at > ?
                ''', (datetime.now() - timedelta(hours=1),))
                
                result = cursor.fetchone()[0]
                return result if result else 0.0
                
        except Exception:
            return 0.0
    
    def _get_messages_per_minute(self) -> float:
        """Calculate current messages per minute rate."""
        try:
            with sqlite3.connect(self.agent.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM messages 
                    WHERE created_at > ?
                ''', (datetime.now() - timedelta(minutes=5),))
                
                count = cursor.fetchone()[0]
                return count / 5.0  # Average per minute over last 5 minutes
                
        except Exception:
            return 0.0
    
    def _check_alerts(self, metrics: Dict[str, Any]):
        """Check for alert conditions."""
        current_time = datetime.now()
        
        # Failure rate alert
        failure_rate = metrics['computed_metrics']['failure_rate']
        if failure_rate > self.alert_thresholds['failure_rate']:
            alert = {
                'type': 'HIGH_FAILURE_RATE',
                'message': f'Failure rate {failure_rate:.1%} exceeds threshold {self.alert_thresholds["failure_rate"]:.1%}',
                'severity': 'HIGH',
                'timestamp': current_time.isoformat(),
                'value': failure_rate
            }
            self.alerts.append(alert)
            print(f"🚨 ALERT: {alert['message']}")
        
        # Queue size alert
        queue_size = metrics['queue_size']
        if queue_size > self.alert_thresholds['queue_size']:
            alert = {
                'type': 'HIGH_QUEUE_SIZE',
                'message': f'Queue size {queue_size} exceeds threshold {self.alert_thresholds["queue_size"]}',
                'severity': 'MEDIUM',
                'timestamp': current_time.isoformat(),
                'value': queue_size
            }
            self.alerts.append(alert)
            print(f"⚠️  ALERT: {alert['message']}")
        
        # Processing time alert
        avg_time = metrics['computed_metrics']['avg_processing_time']
        if avg_time > self.alert_thresholds['response_time']:
            alert = {
                'type': 'SLOW_PROCESSING',
                'message': f'Average processing time {avg_time:.1f}s exceeds threshold {self.alert_thresholds["response_time"]}s',
                'severity': 'MEDIUM',
                'timestamp': current_time.isoformat(),
                'value': avg_time
            }
            self.alerts.append(alert)
            print(f"⚠️  ALERT: {alert['message']}")
        
        # Clean old alerts (keep last 100)
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def _store_historical_data(self, metrics: Dict[str, Any]):
        """Store metrics for historical analysis."""
        self.historical_data.append(metrics)
        
        # Keep only last 24 hours of data (assuming 30-second intervals)
        max_entries = 24 * 60 * 2  # 2880 entries
        if len(self.historical_data) > max_entries:
            self.historical_data = self.historical_data[-max_entries:]
    
    def _display_dashboard(self, metrics: Dict[str, Any]):
        """Display the monitoring dashboard."""
        # Clear screen (works on most terminals)
        print('\033[2J\033[H')
        
        print("🤖 INTELLIGENT OTP AGENT - MONITORING DASHBOARD")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🟢 Agent Status: {'RUNNING' if self.agent.is_running else 'STOPPED'}")
        print()
        
        # Core metrics
        runtime = metrics['runtime_metrics']
        computed = metrics['computed_metrics']
        db_stats = metrics['database_stats']
        
        print("📊 CORE METRICS")
        print("-" * 30)
        print(f"Total Messages Sent: {runtime['total_sent']:,}")
        print(f"Total Delivered: {runtime['total_delivered']:,}")
        print(f"Total Failed: {runtime['total_failed']:,}")
        print(f"Success Rate: {computed['success_rate']:.1%}")
        print(f"Queue Size: {metrics['queue_size']}")
        print(f"Avg Processing Time: {computed['avg_processing_time']:.2f}s")
        print(f"Messages/Minute: {computed['messages_per_minute']:.1f}")
        print()
        
        # Channel performance
        print("📱 CHANNEL PERFORMANCE")
        print("-" * 30)
        for channel, perf in computed['channel_performance'].items():
            print(f"{channel:10} | Success: {perf['success_rate']:.1%} | Sent: {perf['total_sent']:,}")
        print()
        
        # Recent activity (24h)
        if 'database_metrics' in metrics and 'recent_24h' in metrics['database_metrics']:
            recent = metrics['database_metrics']['recent_24h']
            print("📈 RECENT ACTIVITY (24H)")
            print("-" * 30)
            print(f"Messages: {recent['total_messages']:,}")
            print(f"Delivered: {recent['delivered']:,}")
            print(f"Failed: {recent['failed']:,}")
            print(f"Success Rate: {recent['success_rate']:.1%}")
            print()
        
        # Alerts
        if self.alerts:
            recent_alerts = [a for a in self.alerts 
                           if datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(hours=1)]
            if recent_alerts:
                print("🚨 RECENT ALERTS (1H)")
                print("-" * 30)
                for alert in recent_alerts[-5:]:  # Show last 5 alerts
                    time_str = datetime.fromisoformat(alert['timestamp']).strftime('%H:%M:%S')
                    print(f"[{time_str}] {alert['type']}: {alert['message']}")
                print()
        
        print(f"🔄 Next update in {self.update_interval} seconds...")
    
    def get_historical_data(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get historical data for the specified time period."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            data for data in self.historical_data
            if datetime.fromisoformat(data['timestamp']) > cutoff
        ]
    
    def export_metrics(self, filename: str = None) -> str:
        """Export current metrics to JSON file."""
        if not filename:
            filename = f"agent_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'current_metrics': self._collect_metrics(),
            'recent_alerts': self.alerts[-50:],  # Last 50 alerts
            'historical_data': self.historical_data[-100:]  # Last 100 data points
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📁 Metrics exported to {filename}")
        return filename

def demo_monitoring():
    """Demonstrate the monitoring system."""
    # Initialize agent and start processing
    agent = IntelligentOTPAgent()
    agent.start_processing()
    
    # Create monitor
    monitor = AgentMonitor(agent, update_interval=10)  # Update every 10 seconds for demo
    
    # Start monitoring
    monitor.start_monitoring()
    
    print("🚀 Starting monitoring demo...")
    print("📝 Generating some test messages...")
    
    # Generate some test messages to monitor
    from otp_messaging_agent import MessageRequest, Priority
    
    test_messages = [
        MessageRequest(
            phone_number="+447700900001",
            message_type="otp",
            priority=Priority.HIGH
        ),
        MessageRequest(
            phone_number="+447700900002",
            message_type="alert",
            content="Test alert message",
            priority=Priority.CRITICAL
        ),
        MessageRequest(
            phone_number="+447700900003",
            message_type="notification",
            content="Test notification",
            priority=Priority.MEDIUM
        )
    ]
    
    # Send test messages
    for msg in test_messages:
        agent.send_message(msg)
        time.sleep(1)
    
    # Let monitoring run for a while
    try:
        print("⏱️  Monitoring for 60 seconds... (Press Ctrl+C to stop)")
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n⏹️ Stopping monitoring demo...")
    
    # Export metrics
    filename = monitor.export_metrics()
    
    # Stop everything
    monitor.stop_monitoring()
    agent.stop_processing()
    
    print(f"✅ Demo completed! Metrics saved to {filename}")

if __name__ == "__main__":
    demo_monitoring()
