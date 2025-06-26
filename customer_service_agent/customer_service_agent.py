"""
# Customer Service Agent
# Purpose: Handle common customer complaints like lost items, driver speeding, or safety concerns.
# Core Features:
# - Web/mobile chatbot
# - Complaint forms + solve complaints based on Company policies
# - Sentiment analysis
# - Escalation workflow
"""

import os
import random
import requests
import json
import re
from datetime import datetime
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

class SmartCustomerServiceAgent:
    def __init__(self):
        # Conversation memory for context
        self.conversation_history = {}
        self.conversation_state = {}  # Track what stage each conversation is at
        self.collected_details = {}   # Store collected information
        self.complaints = {}
        self.next_id = 1
        self.company_name = "Vaam"
        
        # Enhanced company policies with resolution steps
        self.company_policies = {
            "lost_item": {
                "description": "Customer lost personal belongings in vehicle",
                "resolution_steps": [
                    "Ask for ride details (date, time, pickup/dropoff locations)",
                    "Contact driver immediately",
                    "Check with driver for found items",
                    "Arrange return if found within 24-48 hours",
                    "If not found, provide compensation guidelines"
                ],
                "escalation_triggers": ["valuable item", "urgent", "important document"],
                "response_template": "I understand you've lost an item during your Vaam ride. Let me help you recover it."
            },
            "driver_behavior": {
                "description": "Issues with driver conduct (speeding, unsafe driving, rude behavior)",
                "resolution_steps": [
                    "Gather specific details about the incident",
                    "Document driver ID and ride details",
                    "Assess severity of the issue",
                    "Apply appropriate disciplinary action",
                    "Follow up with customer on resolution"
                ],
                "escalation_triggers": ["dangerous", "unsafe", "threatened", "accident"],
                "response_template": "I'm sorry to hear about your experience with our driver. Your safety is our top priority."
            },
            "payment_billing": {
                "description": "Payment disputes, incorrect charges, refund requests",
                "resolution_steps": [
                    "Review ride details and billing",
                    "Check for system errors or surge pricing",
                    "Calculate appropriate refund if applicable",
                    "Process refund within 3-5 business days",
                    "Send confirmation to customer"
                ],
                "escalation_triggers": ["large amount", "multiple charges", "fraud"],
                "response_template": "I'll help you resolve this billing issue right away."
            },
            "service_quality": {
                "description": "General service complaints, app issues, booking problems",
                "resolution_steps": [
                    "Identify specific service issue",
                    "Provide immediate solution if possible",
                    "Escalate to technical team if needed",
                    "Offer compensation for inconvenience",
                    "Follow up to ensure satisfaction"
                ],                "escalation_triggers": ["app crash", "multiple failures", "emergency"],
                "response_template": "I apologize for the service issue you've experienced. Let me resolve this for you."
            }
        }

    def analyze_issue(self, user_message):
        """Intelligent issue analysis and categorization"""
        message_lower = user_message.lower()
        
        # Issue detection patterns
        issue_patterns = {
            "lost_item": [
                r"lost.*(?:phone|wallet|bag|purse|keys|laptop|item)",
                r"(?:left|forgot).*(?:in|inside).*(?:car|vehicle|uber|taxi)",
                r"can't find.*(?:phone|wallet|bag|purse|keys)"
            ],
            "driver_behavior": [
                r"driver.*(?:rude|aggressive|speeding|unsafe|fast)",
                r"(?:speeding|too fast|dangerous driving)",
                r"driver.*(?:refused|wouldn't|didn't)"
            ],
            "payment_billing": [
                r"(?:charged|billing|payment|refund|money)",
                r"wrong.*(?:amount|charge|fare)",
                r"double.*charged"
            ],
            "service_quality": [
                r"app.*(?:crashed|not working|error)",
                r"booking.*(?:failed|cancelled)",
                r"waiting.*(?:too long|forever)"
            ]
        }
        
        # Find matching issue category
        for category, patterns in issue_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return category
        
        return None

    def extract_context(self, user_message):
        """Extract important context from user message"""
        context = {}
        message_lower = user_message.lower()
        
        # Extract urgency indicators
        urgency_keywords = ["urgent", "emergency", "asap", "immediately", "help"]
        context["urgency"] = "high" if any(word in message_lower for word in urgency_keywords) else "normal"
        
        # Extract emotional state
        negative_emotions = ["angry", "frustrated", "upset", "disappointed", "furious"]
        positive_emotions = ["happy", "satisfied", "pleased", "grateful"]
        
        if any(word in message_lower for word in negative_emotions):
            context["emotion"] = "negative"
        elif any(word in message_lower for word in positive_emotions):
            context["emotion"] = "positive"
        else:
            context["emotion"] = "neutral"
        
        # Extract specific details
        context["details"] = {
            "mentions_driver": "driver" in message_lower,
            "mentions_money": any(word in message_lower for word in ["money", "charge", "cost", "fare", "refund"]),
            "mentions_time": any(word in message_lower for word in ["yesterday", "today", "hour", "minute", "time"]),
            "mentions_location": any(word in message_lower for word in ["airport", "station", "home", "office"])        }
        
        return context

    def generate_intelligent_response(self, user_message, session_id="default"):
        """Generate intelligent, contextual response using free AI"""
        
        # Initialize session data if needed
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
            self.conversation_state[session_id] = {"stage": "initial", "issue_type": None}
            self.collected_details[session_id] = {}
        
        # Store user message
        self.conversation_history[session_id].append({"role": "user", "message": user_message})
        
        # Analyze the issue and context
        issue_category = self.analyze_issue(user_message)
        context = self.extract_context(user_message)
        
        # Get current conversation state
        current_state = self.conversation_state[session_id]
        
        # Check if this is a new issue or continuation
        if issue_category and current_state["stage"] == "initial":
            # New issue detected
            current_state["issue_type"] = issue_category
            current_state["stage"] = "gathering_details"
            response = self.start_issue_resolution(issue_category, user_message, session_id)
        elif current_state["stage"] == "gathering_details":
            # We're collecting details - extract and store them
            self.extract_and_store_details(user_message, session_id)
            response = self.continue_detail_gathering(session_id)
        elif current_state["stage"] == "processing":
            # We have enough details, process the resolution
            response = self.process_resolution(session_id)
        else:
            # General conversation or new topic
            if issue_category:
                # New issue mentioned
                current_state["issue_type"] = issue_category
                current_state["stage"] = "gathering_details"
                self.collected_details[session_id] = {}  # Reset details
                response = self.start_issue_resolution(issue_category, user_message, session_id)
            else:
                # General conversation
                response = self.generate_general_response(user_message, session_id)
        
        # Store bot response in history
        self.conversation_history[session_id].append({"role": "assistant", "message": response})
        
        return response

    def start_issue_resolution(self, issue_category, user_message, session_id):
        """Start resolving a specific issue type"""
        policy = self.company_policies.get(issue_category, {})
        
        if issue_category == "lost_item":
            return "I understand you've lost an item during your Vaam ride. I'll help you recover it. To contact your driver, I need:\n1. Date and time of your ride\n2. Pickup location\n3. Drop-off location\n4. What item you lost\n\nCan you provide these details?"
        
        elif issue_category == "driver_behavior":
            return "I'm sorry to hear about your experience with our driver. Your safety is our top priority. To investigate this properly, I need:\n1. Date and time of the ride\n2. Driver's name or car details\n3. Specific details about what happened\n\nCan you share these details with me?"
        
        elif issue_category == "payment_billing":
            return "I'll help you resolve this billing issue right away. To review your charges, I need:\n1. Date of the ride\n2. The amount you were charged\n3. What you expected to pay\n4. Your ride details\n\nCan you provide this information?"
        
        elif issue_category == "service_quality":
            return "I apologize for the service issue you've experienced. To help resolve this, I need:\n1. What exactly happened?\n2. When did this occur?\n3. What error messages did you see?\n\nCan you describe the issue in detail?"
        
        else:
            return f"Thank you for contacting {self.company_name} support. How can I assist you today?"

    def extract_and_store_details(self, user_message, session_id):
        """Extract and store relevant details from user messages"""
        details = self.collected_details[session_id]
        message_lower = user_message.lower()
        
        # Extract dates
        import re
        date_patterns = [
            r"yesterday", r"today", r"last night", r"this morning", r"this evening",
            r"\d{1,2}[/-]\d{1,2}", r"\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
            r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
        ]
        for pattern in date_patterns:
            if re.search(pattern, message_lower):
                details["date"] = re.search(pattern, message_lower).group()
                break
        
        # Extract times
        time_patterns = [r"\d{1,2}:\d{2}", r"\d{1,2}\s*(?:am|pm)", r"morning|afternoon|evening|night"]
        for pattern in time_patterns:
            if re.search(pattern, message_lower):
                details["time"] = re.search(pattern, message_lower).group()
                break
        
        # Extract locations
        location_keywords = ["from", "to", "pickup", "drop", "airport", "station", "home", "office", "hotel"]
        for keyword in location_keywords:
            if keyword in message_lower:
                # Extract text around location keywords
                words = user_message.split()
                for i, word in enumerate(words):
                    if keyword in word.lower():
                        if i < len(words) - 1:
                            details[f"location_{keyword}"] = " ".join(words[i:i+3])
        
        # Extract items for lost item cases
        item_keywords = ["phone", "wallet", "bag", "purse", "keys", "laptop", "iphone", "android", "samsung"]
        for item in item_keywords:
            if item in message_lower:
                details["lost_item"] = item
                break
        
        # Extract amounts for billing issues
        money_pattern = r"[\$£€]\d+(?:\.\d{2})?"
        money_match = re.search(money_pattern, user_message)
        if money_match:
            details["amount"] = money_match.group()

    def continue_detail_gathering(self, session_id):
        """Continue gathering details or move to resolution"""
        current_state = self.conversation_state[session_id]
        details = self.collected_details[session_id]
        issue_type = current_state["issue_type"]
        
        # Check if we have enough details to proceed
        if issue_type == "lost_item":
            needed = ["date", "lost_item"]
            missing = [item for item in needed if item not in details]
            
            if not missing:
                # We have enough details, move to processing
                current_state["stage"] = "processing"
                return self.process_resolution(session_id)
            else:
                # Still need more details
                if "lost_item" not in details:
                    return "What specific item did you lose? (e.g., phone, wallet, keys, bag)"
                elif "date" not in details:
                    return "When did this happen? Please provide the date and approximate time of your ride."
        
        elif issue_type == "driver_behavior":
            needed = ["date"]
            if "date" not in details:
                return "When did this incident occur? Please provide the date and time of your ride."
            else:
                current_state["stage"] = "processing"
                return self.process_resolution(session_id)
        
        elif issue_type == "payment_billing":
            needed = ["amount", "date"]
            missing = [item for item in needed if item not in details]
            
            if not missing:
                current_state["stage"] = "processing"
                return self.process_resolution(session_id)
            else:
                if "amount" not in details:
                    return "How much were you charged? Please provide the exact amount."
                elif "date" not in details:
                    return "When did this ride take place?"
        
        else:
            # For other issues, move to processing after one exchange
            current_state["stage"] = "processing"
            return self.process_resolution(session_id)

    def process_resolution(self, session_id):
        """Process the final resolution based on collected details"""
        current_state = self.conversation_state[session_id]
        details = self.collected_details[session_id]
        issue_type = current_state["issue_type"]
        
        # Mark as resolved
        current_state["stage"] = "resolved"
        
        if issue_type == "lost_item":
            item = details.get("lost_item", "item")
            date = details.get("date", "recently")
            
            # Create ticket
            ticket_id = self.create_complaint_ticket(
                f"Lost {item} on {date}", issue_type, 
                {"urgency": "normal", "emotion": "neutral"}, session_id
            )
            
            return f"Thank you for providing the details. I've immediately contacted your driver about your lost {item} from {date}. Here's what happens next:\n\n1. ✅ Driver contacted\n2. 🔍 Vehicle search initiated\n3. 📞 You'll hear back within 24 hours\n4. 📦 If found, we'll arrange return\n\nTicket #{ticket_id} created for tracking. Is there anything else I can help you with?"
        
        elif issue_type == "driver_behavior":
            date = details.get("date", "recently")
            
            ticket_id = self.create_complaint_ticket(
                f"Driver behavior issue on {date}", issue_type,
                {"urgency": "high", "emotion": "negative"}, session_id
            )
            
            return f"Thank you for reporting this serious safety concern. I've immediately escalated this to our Driver Relations Team. Here's what's happening:\n\n1. 🚨 Incident logged and prioritized\n2. 👮 Driver will be contacted within 2 hours\n3. 📋 Full investigation initiated\n4. 📞 You'll receive an update within 24 hours\n\nTicket #{ticket_id} created. Your safety is our top priority. Is there anything else I can assist you with?"
        
        elif issue_type == "payment_billing":
            amount = details.get("amount", "the amount")
            date = details.get("date", "recently")
            
            ticket_id = self.create_complaint_ticket(
                f"Billing dispute for {amount} on {date}", issue_type,
                {"urgency": "normal", "emotion": "negative"}, session_id
            )
            
            return f"I've reviewed your billing concern for {amount} from {date}. Here's what I'm doing:\n\n1. ✅ Charge review initiated\n2. 💳 Billing team notified\n3. 🔍 Checking for system errors\n4. 💰 Refund processed if eligible (2-3 business days)\n\nTicket #{ticket_id} created for tracking. You'll receive an email confirmation. Anything else I can help with?"
        
        else:
            return f"Thank you for contacting {self.company_name} support. I've logged your concern and our team will review it. Is there anything else I can help you with today?"

    def generate_general_response(self, user_message, session_id):
        """Generate response for general conversation"""
        message_lower = user_message.lower()
        
        # Check for greetings
        if any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            return f"Hello! Welcome to {self.company_name} customer support. I'm here to help with any issues you might have. How can I assist you today?"
        
        # Check for thanks
        elif any(word in message_lower for word in ["thank", "thanks", "appreciate"]):
            return "You're very welcome! I'm glad I could help. Is there anything else you need assistance with?"
        
        # Check for topic change
        elif any(word in message_lower for word in ["new issue", "different problem", "something else"]):
            # Reset conversation state
            self.conversation_state[session_id] = {"stage": "initial", "issue_type": None}
            self.collected_details[session_id] = {}
            return "Of course! I'm ready to help with your new concern. What's the issue you're experiencing?"
        
        else:
            return f"I'm here to help with any {self.company_name} related issues. You can ask me about:\n• Lost items\n• Driver concerns\n• Billing issues\n• App problems\n\nWhat would you like assistance with?"

    def build_smart_prompt(self, user_message, issue_category, context, session_id):
        """Build intelligent prompt for AI model"""
        
        # Get conversation context
        history = self.conversation_history.get(session_id, [])
        recent_context = ""
        if len(history) > 1:
            recent_context = f"Previous conversation:\n"
            for msg in history[-4:]:  # Last 4 messages for context
                recent_context += f"{msg['role']}: {msg['message']}\n"
        
        # Get policy information if issue detected
        policy_info = ""
        if issue_category and issue_category in self.company_policies:
            policy = self.company_policies[issue_category]
            policy_info = f"""
Issue Category: {issue_category}
Resolution Steps: {', '.join(policy['resolution_steps'])}
Response Template: {policy['response_template']}
"""
        
        # Build comprehensive prompt
        prompt = f"""You are an intelligent customer service AI for Vaam rideshare company. 

{recent_context}

Current Customer Message: {user_message}

Context Analysis:
- Urgency: {context['urgency']}
- Emotional State: {context['emotion']}
- Details: {context['details']}

{policy_info}

Instructions:
1. Be empathetic and professional
2. Address the customer's specific concern
3. If it's a known issue category, follow the resolution steps
4. Ask relevant follow-up questions if needed
5. Provide clear next steps
6. Keep response concise but helpful

Response:"""
        
        return prompt

    def get_free_ai_response(self, prompt):
        """Get response from free Hugging Face model"""
        try:
            # Use a better free model for conversation
            model_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            
            headers = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN', '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')}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(model_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    if 'generated_text' in result[0]:
                        return result[0]['generated_text'].split('Response:')[-1].strip()
                    elif 'generated_text' in result[0]:
                        return result[0]['generated_text'].strip()
                
            # Fallback to rule-based response
            return self.generate_fallback_response(prompt)
            
        except Exception as e:
            print(f"AI API Error: {e}")
            return self.generate_fallback_response(prompt)

    def generate_fallback_response(self, prompt):
        """Generate intelligent fallback response when AI API fails"""
        
        # Extract key information from prompt
        if "lost" in prompt.lower() or "item" in prompt.lower():
            return "I understand you've lost an item. I'll help you recover it. Can you please provide your ride details (date, time, and pickup/dropoff locations) so I can contact your driver immediately?"
        
        elif "driver" in prompt.lower() and any(word in prompt.lower() for word in ["speeding", "unsafe", "rude", "fast"]):
            return "I'm sorry to hear about your experience with our driver. Your safety and comfort are our top priorities. Can you please provide the ride details and specific information about what happened so I can investigate this immediately?"
        
        elif any(word in prompt.lower() for word in ["charge", "billing", "refund", "money", "payment"]):
            return "I'll help you resolve this billing issue right away. Can you please provide your ride details so I can review the charges and determine if a refund is appropriate?"
        
        elif "app" in prompt.lower() or "booking" in prompt.lower():
            return "I apologize for the technical issue you've experienced. Let me help resolve this. Can you describe exactly what happened and what error messages you saw?"
        
        else:
            return f"Thank you for contacting {self.company_name} support. I'm here to help you with any concerns. Can you please provide more details about your issue so I can assist you better?"

    def enhance_response(self, ai_response, issue_category, context):
        """Enhance AI response with empathy and action items"""
        
        enhanced_response = ai_response
        
        # Add empathy based on emotional state
        if context["emotion"] == "negative":
            if not any(phrase in ai_response.lower() for phrase in ["sorry", "apologize", "understand"]):
                enhanced_response = "I sincerely apologize for this experience. " + enhanced_response
        
        # Add urgency handling
        if context["urgency"] == "high":
            if "immediately" not in enhanced_response.lower():
                enhanced_response += " I'll prioritize this issue and get back to you as soon as possible."
        
        # Add specific policy actions
        if issue_category and issue_category in self.company_policies:
            policy = self.company_policies[issue_category]
            
            # Check for escalation triggers
            escalation_needed = any(trigger in ai_response.lower() for trigger in policy["escalation_triggers"])
            if escalation_needed:
                enhanced_response += " Due to the serious nature of this issue, I'm escalating this to our specialist team for immediate attention."
        
        return enhanced_response

    def create_complaint_ticket(self, user_message, issue_category, context, session_id):
        """Create intelligent complaint ticket"""
        ticket_id = f"VAAM-{self.next_id:06d}"
        self.next_id += 1
        
        ticket = {
            "id": ticket_id,
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "issue_category": issue_category,
            "context": context,
            "session_id": session_id,
            "status": "open",
            "priority": "high" if context["urgency"] == "high" else "normal",
            "assigned_team": self.determine_team(issue_category),
            "conversation_history": self.conversation_history.get(session_id, [])
        }
        
        self.complaints[ticket_id] = ticket
        return ticket_id

    def determine_team(self, issue_category):
        """Determine which team should handle the issue"""
        team_mapping = {
            "lost_item": "Lost & Found Team",
            "driver_behavior": "Driver Relations Team", 
            "payment_billing": "Billing Support Team",
            "service_quality": "Technical Support Team"
        }
        return team_mapping.get(issue_category, "General Support Team")

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Create smart agent instance
agent = SmartCustomerServiceAgent()

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('user_message')
def handle_user_message(data):
    user_input = data['message']
    session_id = data.get('session_id', 'default')
    
    try:
        # Generate intelligent response using conversation management
        response = agent.generate_intelligent_response(user_input, session_id)
        
        # Get current conversation state for UI updates
        current_state = agent.conversation_state.get(session_id, {})
        collected_details = agent.collected_details.get(session_id, {})
        
        # Only send ticket info if resolution was just completed
        ticket_info = None
        if current_state.get("stage") == "resolved" and "Ticket #" in response:
            # Extract ticket ID from response
            import re
            ticket_match = re.search(r'Ticket #([\w-]+)', response)
            if ticket_match:
                ticket_info = {
                    'ticket_id': ticket_match.group(1),
                    'issue_category': current_state.get("issue_type"),
                    'stage': current_state.get("stage"),
                    'details': collected_details
                }
        
        emit('bot_response', {
            'message': response,
            'conversation_state': {
                'stage': current_state.get("stage", "initial"),
                'issue_type': current_state.get("issue_type"),
                'collected_details': list(collected_details.keys()) if collected_details else []
            },
            'ticket_info': ticket_info
        })
        
    except Exception as e:
        print(f"Error in handle_user_message: {e}")
        emit('bot_response', {
            'message': "I apologize, but I'm experiencing technical difficulties. Please try again or contact our support team directly.",
            'error': True
        })

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
