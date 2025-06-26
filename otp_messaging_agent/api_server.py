"""
REST API wrapper for the Intelligent OTP Agent
Provides HTTP endpoints for automated message processing
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json
import threading
from otp_messaging_agent import IntelligentOTPAgent, MessageRequest, Priority

app = Flask(__name__)

# Global agent instance
agent = None

def init_agent():
    """Initialize the agent."""
    global agent
    agent = IntelligentOTPAgent()
    agent.start_processing()
    print("🚀 Intelligent OTP Agent API Server Started")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "agent_running": agent.is_running if agent else False,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to a phone number."""
    try:
        data = request.get_json()
        
        if not data or 'phone_number' not in data:
            return jsonify({"error": "phone_number is required"}), 400
        
        message_id = agent.send_otp(
            phone_number=data['phone_number'],
            user_id=data.get('user_id', ''),
            callback_url=data.get('callback_url', '')
        )
        
        return jsonify({
            "success": True,
            "message_id": message_id,
            "phone_number": data['phone_number']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send-message', methods=['POST'])
def send_message():
    """Send a custom message."""
    try:
        data = request.get_json()
        
        if not data or 'phone_number' not in data:
            return jsonify({"error": "phone_number is required"}), 400
        
        # Parse priority
        priority = Priority.MEDIUM
        if 'priority' in data:
            try:
                priority = Priority[data['priority'].upper()]
            except KeyError:
                return jsonify({"error": "Invalid priority. Use LOW, MEDIUM, HIGH, or CRITICAL"}), 400
        
        # Parse scheduled_for
        scheduled_for = None
        if 'scheduled_for' in data:
            try:
                scheduled_for = datetime.fromisoformat(data['scheduled_for'])
            except ValueError:
                return jsonify({"error": "Invalid scheduled_for format. Use ISO format: 2025-06-23T15:30:00"}), 400
        
        request_obj = MessageRequest(
            phone_number=data['phone_number'],
            message_type=data.get('message_type', 'notification'),
            content=data.get('content', ''),
            priority=priority,
            preferred_channel=data.get('preferred_channel', 'SMS'),
            max_retries=data.get('max_retries', 3),
            scheduled_for=scheduled_for,
            callback_url=data.get('callback_url', ''),
            user_id=data.get('user_id', '')
        )
        
        message_id = agent.send_message(request_obj)
        
        return jsonify({
            "success": True,
            "message_id": message_id,
            "phone_number": data['phone_number'],
            "message_type": data.get('message_type', 'notification')
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send-bulk', methods=['POST'])
def send_bulk():
    """Send multiple messages in bulk."""
    try:
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({"error": "messages array is required"}), 400
        
        messages = []
        for msg_data in data['messages']:
            if 'phone_number' not in msg_data:
                return jsonify({"error": "Each message must have phone_number"}), 400
            
            # Parse priority
            priority = Priority.MEDIUM
            if 'priority' in msg_data:
                try:
                    priority = Priority[msg_data['priority'].upper()]
                except KeyError:
                    return jsonify({"error": f"Invalid priority in message: {msg_data.get('priority')}"}), 400
            
            # Parse scheduled_for
            scheduled_for = None
            if 'scheduled_for' in msg_data:
                try:
                    scheduled_for = datetime.fromisoformat(msg_data['scheduled_for'])
                except ValueError:
                    return jsonify({"error": f"Invalid scheduled_for format in message: {msg_data.get('scheduled_for')}"}), 400
            
            request_obj = MessageRequest(
                phone_number=msg_data['phone_number'],
                message_type=msg_data.get('message_type', 'notification'),
                content=msg_data.get('content', ''),
                priority=priority,
                preferred_channel=msg_data.get('preferred_channel', 'SMS'),
                max_retries=msg_data.get('max_retries', 3),
                scheduled_for=scheduled_for,
                callback_url=msg_data.get('callback_url', ''),
                user_id=msg_data.get('user_id', '')
            )
            messages.append(request_obj)
        
        message_ids = agent.send_bulk_messages(messages)
        
        return jsonify({
            "success": True,
            "message_ids": message_ids,
            "count": len(message_ids)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify an OTP."""
    try:
        data = request.get_json()
        
        if not data or 'phone_number' not in data or 'otp' not in data:
            return jsonify({"error": "phone_number and otp are required"}), 400
        
        success, message = agent.verify_otp(data['phone_number'], data['otp'])
        
        return jsonify({
            "success": success,
            "message": message,
            "phone_number": data['phone_number']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delivery-report/<message_id>', methods=['GET'])
def get_delivery_report(message_id):
    """Get delivery report for a message."""
    try:
        report = agent.get_delivery_report(message_id)
        
        if not report:
            return jsonify({"error": "Message not found"}), 404
        
        return jsonify({
            "message_id": report.message_id,
            "phone_number": report.phone_number,
            "status": report.status.value,
            "channel": report.channel,
            "attempts": report.attempts,
            "last_attempt": report.last_attempt.isoformat(),
            "error_message": report.error_message,
            "delivery_time": report.delivery_time.isoformat() if report.delivery_time else None
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Get agent metrics and statistics."""
    try:
        metrics = agent.get_metrics()
        return jsonify(metrics)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/load-from-json', methods=['POST'])
def load_from_json():
    """Load messages from uploaded JSON data."""
    try:
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({"error": "messages array is required"}), 400
        
        # Save to temporary file and load
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data['messages'], f, indent=2)
            temp_file = f.name
        
        try:
            count = agent.load_messages_from_json(temp_file)
            
            return jsonify({
                "success": True,
                "messages_loaded": count
            })
            
        finally:
            os.unlink(temp_file)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Run cleanup of old records."""
    try:
        data = request.get_json() or {}
        older_than_days = data.get('older_than_days', 30)
        
        result = agent.auto_cleanup(older_than_days)
        
        return jsonify({
            "success": True,
            "cleanup_result": result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Initialize agent in a separate thread
    init_thread = threading.Thread(target=init_agent)
    init_thread.start()
    init_thread.join()
    
    # Start API server
    print("🌐 Starting API server on http://localhost:5000")
    print("\nAvailable endpoints:")
    print("POST /send-otp - Send OTP")
    print("POST /send-message - Send custom message")
    print("POST /send-bulk - Send bulk messages")
    print("POST /verify-otp - Verify OTP")
    print("GET  /delivery-report/<id> - Get delivery report")
    print("GET  /metrics - Get agent metrics")
    print("POST /load-from-json - Load messages from JSON")
    print("POST /cleanup - Clean old records")
    print("GET  /health - Health check")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
