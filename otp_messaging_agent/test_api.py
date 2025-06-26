# Test script for the Intelligent OTP Agent API
# Demonstrates automated message processing via REST API

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_send_otp():
    """Test sending an OTP via API."""
    print("📱 Testing OTP sending...")
    
    data = {
        "phone_number": "+447700900001",
        "user_id": "test_user_001",
        "callback_url": "https://webhook.site/test"
    }
    
    response = requests.post(f"{BASE_URL}/send-otp", json=data)
    print(f"Response: {response.status_code}")
    print(f"Data: {response.json()}")
    return response.json().get("message_id")

def test_send_bulk():
    """Test bulk message sending."""
    print("\n📦 Testing bulk message sending...")
    
    data = {
        "messages": [
            {
                "phone_number": "+447700900002",
                "message_type": "alert",
                "content": "Security alert: New login detected",
                "priority": "CRITICAL",
                "preferred_channel": "SMS"
            },
            {
                "phone_number": "+447700900003",
                "message_type": "notification",
                "content": "Your order has been shipped",
                "priority": "MEDIUM",
                "preferred_channel": "WhatsApp"
            },
            {
                "phone_number": "+447700900004",
                "message_type": "otp",
                "priority": "HIGH"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/send-bulk", json=data)
    print(f"Response: {response.status_code}")
    print(f"Data: {response.json()}")

def test_load_from_json():
    """Test loading messages from JSON data."""
    print("\n📄 Testing JSON data loading...")
    
    data = {
        "messages": [
            {
                "phone_number": "+447700900005",
                "message_type": "welcome",
                "content": "Welcome to our platform!",
                "priority": "LOW",
                "preferred_channel": "Email"
            },
            {
                "phone_number": "+447700900006",
                "message_type": "reminder",
                "content": "Don't forget your appointment tomorrow",
                "priority": "MEDIUM"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/load-from-json", json=data)
    print(f"Response: {response.status_code}")
    print(f"Data: {response.json()}")

def test_metrics():
    """Test getting agent metrics."""
    print("\n📊 Testing metrics endpoint...")
    
    response = requests.get(f"{BASE_URL}/metrics")
    print(f"Response: {response.status_code}")
    metrics = response.json()
    
    print("Current metrics:")
    print(f"  Total sent: {metrics['runtime_metrics']['total_sent']}")
    print(f"  Total delivered: {metrics['runtime_metrics']['total_delivered']}")
    print(f"  Success rate: {metrics['database_stats']['success_rate']}")
    print(f"  Queue size: {metrics['queue_size']}")

def test_verify_otp():
    """Test OTP verification."""
    print("\n🔐 Testing OTP verification...")
    
    # First send an OTP
    message_id = test_send_otp()
    time.sleep(2)  # Wait for processing
    
    # Try to verify with wrong OTP
    data = {
        "phone_number": "+447700900001",
        "otp": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/verify-otp", json=data)
    print(f"Wrong OTP Response: {response.status_code}")
    print(f"Data: {response.json()}")

if __name__ == "__main__":
    print("🤖 Testing Intelligent OTP Agent API")
    print("=" * 50)
    
    # Wait for API to be ready
    time.sleep(2)
    
    try:
        # Test health
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy")
        else:
            print("❌ API health check failed")
            exit(1)
        
        # Run tests
        test_send_otp()
        test_send_bulk()
        test_load_from_json()
        
        # Wait for processing
        print("\n⏳ Waiting for message processing...")
        time.sleep(5)
        
        test_metrics()
        test_verify_otp()
        
        print("\n✅ All API tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on port 5000")
    except Exception as e:
        print(f"❌ Test error: {e}")
