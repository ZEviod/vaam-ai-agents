import os
import json
import datetime
import re
from typing import Dict, List, Any, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

"""
# Intelligent Driver Service Agent
# Purpose: AI-powered assistant to help drivers with issues, complaints, and support
# Enhanced Features:
# - Advanced AI reasoning and problem-solving
# - Context-aware responses with memory
# - Intelligent issue analysis and resolution
# - Dynamic knowledge base with learning capabilities
# - Smart escalation with priority assessment
# - Conversation history and pattern recognition
"""

class DriverServiceAgent:
    def __init__(self, model_name_or_path="microsoft/DialoGPT-medium"):
        # Enhanced knowledge base for Vaam (UK ride-hailing)
        self.knowledge_base = {
            "compensation": {
                "info": "For compensation issues, please provide your trip ID and a brief description. Vaam support will review your case.",
                "process": "Go to 'Help' > 'Trip Issues' > Select trip > 'Request Compensation'",
                "timeframe": "Usually processed within 2-3 business days",
                "requirements": ["Trip ID", "Issue description", "Supporting evidence if applicable"]
            },
            "app_bug": {
                "info": "If you encounter an app bug, try restarting the app. If the issue persists, please report the bug with screenshots.",
                "troubleshooting": ["Force close and restart app", "Check for app updates", "Restart phone", "Clear app cache"],
                "reporting": "Help > Report Bug > Include screenshots and steps to reproduce"
            },
            "complaint": {
                "info": "To file a complaint, please provide details of the incident. Vaam takes all complaints seriously and will investigate promptly.",
                "categories": ["Passenger behavior", "Safety concerns", "Discrimination", "App issues", "Payment disputes"],
                "process": "Help > File Complaint > Select category > Provide details"
            },
            "payment": {
                "info": "Payments are processed every Friday. If you have not received your payment, check your bank details in the app or contact support.",
                "schedule": "Every Friday by 5 PM",
                "troubleshooting": ["Verify bank details", "Check for account restrictions", "Contact your bank"],
                "requirements": ["Valid UK bank account", "Correct sort code and account number"]
            },
            "vehicle_requirements": {
                "info": "Vaam requires vehicles to be less than 8 years old, with valid MOT and insurance in the UK.",
                "requirements": ["Vehicle age < 8 years", "Valid MOT certificate", "Private hire insurance", "V5C document"],
                "documents": "Upload via App > Vehicle Management > Documents"
            }
        }
        
        self.conversation_history = []
        self.user_context = {}
        self.model_name_or_path = model_name_or_path
        self.issue_patterns = {
            "urgent": ["accident", "emergency", "unsafe", "danger", "harassment", "assault"],
            "financial": ["payment", "money", "compensation", "refund", "fare", "earning"],
            "technical": ["app", "bug", "error", "crash", "login", "GPS", "location"],
            "service": ["complaint", "passenger", "rating", "rude", "discrimination"]
        }
          # Initialize AI model for reasoning
        try:
            self.local_chatbot = pipeline("conversational", model=self.model_name_or_path)
            self.reasoning_enabled = True
        except Exception as e:
            print(f"Warning: Could not load AI model. Using fallback mode. Error: {e}")
            self.reasoning_enabled = False
    
    def analyze_issue_context(self, message):
        """Analyze the message to understand context and extract key information."""
        message_lower = message.lower()
        analysis = {
            "issue_type": None,
            "urgency": "low",
            "entities": [],
            "sentiment": "neutral",
            "requires_human": False
        }
        
        # Detect issue type
        for issue_type, keywords in self.issue_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                analysis["issue_type"] = issue_type
                break
        
        # Detect urgency
        if any(urgent_word in message_lower for urgent_word in self.issue_patterns["urgent"]):
            analysis["urgency"] = "high"
            analysis["requires_human"] = True
        elif any(word in message_lower for word in ["help", "urgent", "important", "asap"]):
            analysis["urgency"] = "medium"
            
        # Extract entities (trip IDs, amounts, dates)
        trip_id_pattern = r'#[A-Z0-9]{8,12}|trip[:\s]*([A-Z0-9]{8,12})'
        amount_pattern = r'£[\d,]+\.?\d*|\d+[\.\d]*\s*pounds?'
        
        trip_ids = re.findall(trip_id_pattern, message, re.IGNORECASE)
        amounts = re.findall(amount_pattern, message, re.IGNORECASE)
        
        if trip_ids:
            analysis["entities"].extend([f"trip_id:{tid}" for tid in trip_ids])
        if amounts:
            analysis["entities"].extend([f"amount:{amt}" for amt in amounts])
            
        # Basic sentiment analysis
        positive_words = ["good", "great", "thanks", "helpful", "pleased"]
        negative_words = ["bad", "terrible", "awful", "angry", "frustrated", "disappointed"]
        
        if any(word in message_lower for word in negative_words):
            analysis["sentiment"] = "negative"
        elif any(word in message_lower for word in positive_words):
            analysis["sentiment"] = "positive"
            
        return analysis

    def generate_intelligent_response(self, message, context_analysis):
        """Generate an intelligent, context-aware response."""
        # Start with a personalized greeting based on sentiment
        if context_analysis["sentiment"] == "negative":
            response_prefix = "I understand you're having difficulties. Let me help you resolve this issue. "
        elif context_analysis["sentiment"] == "positive":
            response_prefix = "Thank you for reaching out! I'm happy to help. "
        else:
            response_prefix = "I'm here to assist you. "
            
        # Handle urgent issues immediately
        if context_analysis["urgency"] == "high":
            return response_prefix + "This appears to be an urgent matter. I'm escalating this to our priority support team immediately. In the meantime, if this is a safety emergency, please contact emergency services at 999."
            
        # Generate contextual response based on issue type
        if context_analysis["issue_type"] == "financial":
            return self._handle_financial_issue(message, context_analysis, response_prefix)
        elif context_analysis["issue_type"] == "technical":
            return self._handle_technical_issue(message, context_analysis, response_prefix)
        elif context_analysis["issue_type"] == "service":
            return self._handle_service_issue(message, context_analysis, response_prefix)
        else:
            return self._handle_general_inquiry(message, context_analysis, response_prefix)

    def _handle_financial_issue(self, message, context, prefix):
        """Handle payment and compensation related issues."""
        message_lower = message.lower()
        
        if "compensation" in message_lower or "refund" in message_lower:
            response = prefix + "I can help you with compensation requests. "
            
            # Check if they provided trip ID
            trip_ids = [entity for entity in context["entities"] if entity.startswith("trip_id:")]
            if trip_ids:
                response += f"I see you've mentioned trip ID {trip_ids[0].split(':')[1]}. "
                response += "I'll process your compensation request for this trip. Please provide a brief description of what happened during this trip, and I'll escalate it to our finance team for review."
            else:
                response += "To process your compensation request, I'll need your trip ID. You can find this in your trip history. Once you provide it, I can immediately escalate your case."
                
            response += " Compensation requests are typically reviewed within 2-3 business days."
            return response
            
        elif "payment" in message_lower or "money" in message_lower:
            if "missing" in message_lower or "not received" in message_lower:
                return prefix + "I understand you haven't received your payment. Let me check this for you. Payments are processed every Friday by 5 PM. If you haven't received yours, please verify your bank details in the app under 'Account Settings'. If your details are correct, I'll escalate this to our payments team immediately."
            else:
                return prefix + "Regarding payments: We process payments every Friday by 5 PM. The money typically appears in your account within 1-2 business days depending on your bank. Is there a specific payment issue I can help you with?"
                
        return prefix + "I'm here to help with your financial concern. Could you provide more details about the specific issue you're experiencing?"

    def _handle_technical_issue(self, message, context, prefix):
        """Handle app bugs and technical problems."""
        message_lower = message.lower()
        
        if "app" in message_lower and any(word in message_lower for word in ["crash", "freeze", "not working", "bug"]):
            response = prefix + "I can help you resolve this app issue. Let's try these troubleshooting steps:\n\n"
            response += "1. Force close the Vaam app completely\n"
            response += "2. Restart your phone\n"
            response += "3. Open the app again\n\n"
            response += "If the problem persists:\n"
            response += "4. Check if there's an app update available in your app store\n"
            response += "5. Clear the app cache (Android) or reinstall the app\n\n"
            response += "Please try these steps and let me know if the issue continues. If it does, I'll escalate this to our technical team with your device information."
            return response
            
        elif "login" in message_lower or "password" in message_lower:
            return prefix + "For login issues, try resetting your password using the 'Forgot Password' option on the login screen. If you're still unable to access your account, I can help you reset it manually. Please confirm your registered email address."
            
        elif "gps" in message_lower or "location" in message_lower:
            return prefix + "For GPS/location issues, please ensure:\n1. Location permissions are enabled for the Vaam app\n2. Your phone's GPS is turned on\n3. You have a good signal or WiFi connection\n\nIf the problem continues, I'll report this as a technical issue to our development team."
            
        return prefix + "I can help you with this technical issue. Please describe exactly what's happening and when you first noticed the problem."

    def _handle_service_issue(self, message, context, prefix):
        """Handle complaints and service-related issues."""
        message_lower = message.lower()
        
        if "complaint" in message_lower or "complain" in message_lower:
            response = prefix + "I take your complaint very seriously and will ensure it's properly addressed. "
            
            # Check for specific complaint types
            if any(word in message_lower for word in ["rude", "discrimination", "harassment"]):
                response += "This appears to be a serious incident involving passenger behavior. I'm escalating this immediately to our safety and compliance team. "
                
            response += "To file your formal complaint:\n"
            response += "1. Go to 'Help' in your app\n"
            response += "2. Select 'File a Complaint'\n"
            response += "3. Choose the appropriate category\n"
            response += "4. Provide detailed information about the incident\n\n"
            response += "Your complaint will be reviewed within 3 business days, and you'll receive a detailed response."
            return response
            
        elif "rating" in message_lower or "review" in message_lower:
            return prefix + "Regarding ratings, I understand this can be frustrating. If you believe you received an unfair rating, you can dispute it through 'Help' > 'Rating Dispute'. Please provide details about the trip and why you believe the rating was unfair."
            
        return prefix + "I want to ensure you have the best possible experience with Vaam. Please tell me more about your concern so I can assist you properly."

    def _handle_general_inquiry(self, message, context, prefix):
        """Handle general questions and inquiries."""
        return prefix + "I'm here to help with any questions about driving with Vaam. I can assist with compensation requests, app issues, payment questions, vehicle requirements, complaints, and more. What specific area would you like help with?"

    def ai_response(self, message):
        """Get a dynamic response from AI with enhanced reasoning."""
        # Store conversation history
        self.conversation_history.append({"role": "user", "content": message, "timestamp": datetime.datetime.now()})
        
        # Analyze the message context
        context_analysis = self.analyze_issue_context(message)
        
        # Generate intelligent response
        response = self.generate_intelligent_response(message, context_analysis)
        
        # Try to enhance with AI model if available
        if self.reasoning_enabled:
            try:
                from transformers import Conversation
                # Create context for AI model
                context_prompt = f"As a helpful Vaam driver support agent, respond to: {message}"
                conv = Conversation(context_prompt)
                ai_result = self.local_chatbot(conv)
                
                if ai_result.generated_responses:
                    ai_suggestion = ai_result.generated_responses[-1]
                    # Combine our intelligent response with AI enhancement
                    if len(ai_suggestion) > 50 and "vaam" in ai_suggestion.lower():
                        response = ai_suggestion
                        
            except Exception as e:
                print(f"AI enhancement failed: {e}")
                
        # Store response in history
        self.conversation_history.append({"role": "assistant", "content": response, "timestamp": datetime.datetime.now()})
        
        return response

    def chatbot_response(self, message):
        """Respond to driver via in-app chatbot with more intelligent, context-aware answers."""
        ai_reply = self.ai_response(message)
        if ai_reply:
            return ai_reply
        message = message.lower()
        # Compensation
        if any(word in message for word in ["compensation", "refund", "reimburse", "fare adjustment"]):
            if "how" in message or "process" in message:
                return "To request compensation, go to the 'Help' section in your Vaam app, select the relevant trip, and follow the instructions. If you need further help, provide your trip ID."
            elif "status" in message or "when" in message:
                return "Compensation requests are usually reviewed within 2 business days. You will be notified in the app once a decision is made."
            else:
                return self.knowledge_base["compensation"]["info"]
        # App bugs or errors
        elif any(word in message for word in ["bug", "error", "crash", "not working", "issue", "problem"]):
            if "app" in message or "vaam" in message:
                if "update" in message:
                    return "Please ensure your Vaam app is updated to the latest version from the App Store or Google Play."
                elif "screenshot" in message or "report" in message:
                    return "You can report bugs directly in the app by going to 'Help' > 'Report a Problem'. Attach screenshots if possible."
                else:
                    return self.knowledge_base["app_bug"]["info"]
            else:
                return "Could you specify if the issue is with the Vaam app or another part of the service?"
        # Complaints
        elif any(word in message for word in ["complaint", "complain", "bad experience", "rude", "unsafe", "problem with passenger"]):
            if "how" in message or "file" in message or "submit" in message:
                return "To file a complaint, open your Vaam app, go to 'Help', and select 'File a Complaint'. Provide as much detail as possible."
            elif "status" in message:
                return "Complaints are reviewed within 3 business days. You will be updated via the app."
            else:
                return self.knowledge_base["complaint"]["info"]
        # Payment
        elif any(word in message for word in ["payment", "pay", "salary", "deposit", "payout", "bank"]):
            if "when" in message or "date" in message:
                return "Payments are processed every Friday. Depending on your bank, it may take 1-2 days to appear in your account."
            elif "change" in message or "update" in message:
                return "To update your bank details, go to 'Account Settings' in your Vaam app and edit your payment information."
            elif "missing" in message or "not received" in message:
                return "If you haven't received your payment, check your bank details in the app. If correct, contact support with your trip details."
            else:
                return self.knowledge_base["payment"]["info"]
        # Vehicle requirements
        elif any(word in message for word in ["vehicle", "car", "requirements", "mot", "insurance", "age", "register"]):
            if "how" in message or "register" in message:
                return "To register your vehicle with Vaam, upload your vehicle documents (MOT, insurance, V5C) in the app under 'Vehicle Management'."
            elif "age" in message:
                return "Vaam requires vehicles to be less than 8 years old."
            elif "insurance" in message:
                return "You must have valid UK private hire insurance to drive with Vaam."
            else:
                return self.knowledge_base["vehicle_requirements"]["info"]
        # General greetings/help
        elif any(word in message for word in ["hello", "hi", "help", "support", "question"]):
            return "Hello! I'm your Vaam driver assistant. How can I help you today? You can ask about compensation, app issues, payments, vehicle requirements, or anything else."
        # Unknown or unclear
        else:
            return "I'm here to help with any issues related to your work with Vaam. Could you please provide more details about your question or type 'escalate' to contact human support?"

    def access_knowledge_base(self, query):
        """Provide answers from knowledge base."""
        query = query.lower()
        for key, answer in self.knowledge_base.items():
            if key in query:
                return answer
        return "No relevant information found in the knowledge base."

    def log_error(self, error_data):
        """Analyze and log errors reported by drivers."""
        # Simulate error logging
        print(f"[LOG] Error reported: {error_data}")
        if "critical" in error_data.lower():
            return "Critical error logged. Escalating to human support."
        return "Error logged. Our team will review it shortly."

    def escalate_to_human(self, issue):
        """Escalate issue to human support."""
        # Simulate escalation
        print(f"[ESCALATION] Issue escalated: {issue}")
        return "Your issue has been escalated to a Vaam human support agent. You will be contacted soon."

    def advanced_reasoning(self, message, context_analysis):
        """Advanced AI reasoning for complex problem solving."""
        reasoning_steps = []
        
        # Step 1: Problem identification
        problem_type = self.identify_problem_complexity(message, context_analysis)
        reasoning_steps.append(f"Problem identified as: {problem_type}")
        
        # Step 2: Context gathering
        relevant_context = self.gather_relevant_context(message, context_analysis)
        reasoning_steps.append(f"Relevant context: {relevant_context}")
        
        # Step 3: Solution generation
        potential_solutions = self.generate_solutions(message, context_analysis, problem_type)
        reasoning_steps.append(f"Generated {len(potential_solutions)} potential solutions")
        
        # Step 4: Solution ranking
        best_solution = self.rank_solutions(potential_solutions, context_analysis)
        reasoning_steps.append(f"Best solution selected: {best_solution['type']}")
        
        return {
            "reasoning_steps": reasoning_steps,
            "solution": best_solution,
            "confidence": best_solution.get("confidence", 0.8)
        }
    
    def identify_problem_complexity(self, message, context_analysis):
        """Identify the complexity level of the problem."""
        complexity_indicators = {
            "simple": ["when", "what", "how much", "where"],
            "moderate": ["why", "explain", "help me understand"],
            "complex": ["multiple", "several", "both", "combination", "complicated"]
        }
        
        message_lower = message.lower()
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                return complexity
        
        # If urgent or involves multiple issue types, it's complex
        if context_analysis["urgency"] == "high" or len([t for t in self.issue_patterns.keys() if any(keyword in message_lower for keyword in self.issue_patterns[t])]) > 1:
            return "complex"
        
        return "moderate"
    
    def gather_relevant_context(self, message, context_analysis):
        """Gather relevant context from conversation history and knowledge base."""
        relevant_context = {
            "conversation_history": self.conversation_history[-3:],  # Last 3 exchanges
            "issue_type": context_analysis.get("issue_type"),
            "urgency": context_analysis.get("urgency"),
            "entities": context_analysis.get("entities", []),
            "sentiment": context_analysis.get("sentiment")
        }
        
        # Add relevant knowledge base entries
        if context_analysis.get("issue_type"):
            kb_key = context_analysis["issue_type"]
            if kb_key == "financial":
                relevant_context["kb_info"] = [self.knowledge_base.get("compensation"), self.knowledge_base.get("payment")]
            elif kb_key == "technical":
                relevant_context["kb_info"] = [self.knowledge_base.get("app_bug")]
            elif kb_key == "service":
                relevant_context["kb_info"] = [self.knowledge_base.get("complaint")]
        
        return relevant_context
    
    def generate_solutions(self, message, context_analysis, problem_type):
        """Generate multiple potential solutions for the problem."""
        solutions = []
        
        # Solution 1: Direct knowledge base response
        if context_analysis.get("issue_type"):
            direct_solution = self.generate_direct_solution(message, context_analysis)
            solutions.append({
                "type": "direct",
                "response": direct_solution,
                "confidence": 0.9 if problem_type == "simple" else 0.7
            })
        
        # Solution 2: Step-by-step guidance
        if problem_type in ["moderate", "complex"]:
            step_solution = self.generate_step_by_step_solution(message, context_analysis)
            solutions.append({
                "type": "step_by_step",
                "response": step_solution,
                "confidence": 0.8
            })
        
        # Solution 3: Escalation with context
        if context_analysis["urgency"] == "high" or problem_type == "complex":
            escalation_solution = self.generate_escalation_solution(message, context_analysis)
            solutions.append({
                "type": "escalation",
                "response": escalation_solution,
                "confidence": 0.95 if context_analysis["urgency"] == "high" else 0.6
            })
        
        # Solution 4: Educational response
        educational_solution = self.generate_educational_solution(message, context_analysis)
        solutions.append({
            "type": "educational",
            "response": educational_solution,
            "confidence": 0.6
        })
        
        return solutions
    
    def generate_direct_solution(self, message, context_analysis):
        """Generate a direct solution based on knowledge base."""
        issue_type = context_analysis.get("issue_type")
        if issue_type == "financial":
            return self._handle_financial_issue(message, context_analysis, "")
        elif issue_type == "technical":
            return self._handle_technical_issue(message, context_analysis, "")
        elif issue_type == "service":
            return self._handle_service_issue(message, context_analysis, "")
        else:
            return self._handle_general_inquiry(message, context_analysis, "")
    
    def generate_step_by_step_solution(self, message, context_analysis):
        """Generate a step-by-step solution for complex problems."""
        issue_type = context_analysis.get("issue_type")
        
        if issue_type == "financial":
            return """Let me guide you through resolving your financial concern step by step:
            
Step 1: Identify the specific issue (payment missing, compensation needed, fare dispute)
Step 2: Gather required information (trip ID, bank details, incident details)
Step 3: Use the appropriate app feature (Help > Payment Issues or Trip Issues)
Step 4: Submit your request with all details
Step 5: Monitor your app for updates (typically 2-3 business days)

Would you like me to help you with any specific step?"""
        
        elif issue_type == "technical":
            return """Let's troubleshoot your technical issue systematically:
            
Step 1: Basic troubleshooting (restart app, check connection)
Step 2: Device-specific fixes (clear cache, update app)
Step 3: Account-related checks (login credentials, permissions)
Step 4: Report the issue if it persists
Step 5: Follow up with support if needed

Which step would you like to start with?"""
        
        else:
            return """I'll help you resolve this issue step by step:
            
Step 1: Clarify the specific problem you're experiencing
Step 2: Gather any relevant information (trip details, screenshots, etc.)
Step 3: Check if there's an immediate solution in the app
Step 4: Document the issue if it needs escalation
Step 5: Follow up as needed

What's the first thing you'd like to address?"""
    
    def generate_escalation_solution(self, message, context_analysis):
        """Generate an escalation solution with full context."""
        urgency_level = context_analysis.get("urgency", "low")
        issue_type = context_analysis.get("issue_type", "general")
        
        escalation_msg = f"I'm escalating your {issue_type} issue to our specialized support team. "
        
        if urgency_level == "high":
            escalation_msg += "Due to the urgent nature of your concern, this will be prioritized. "
        
        escalation_msg += f"""Here's what happens next:

1. Your case is being logged with reference: VM-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}
2. A specialist will review your issue within {'1 hour' if urgency_level == 'high' else '24 hours'}
3. You'll receive a detailed response via the app
4. If needed, you may receive a phone call for complex issues

In the meantime, if this is a safety emergency, please contact 999 immediately."""
        
        return escalation_msg
    
    def generate_educational_solution(self, message, context_analysis):
        """Generate an educational response to help prevent future issues."""
        issue_type = context_analysis.get("issue_type")
        
        if issue_type == "financial":
            return """Here are some tips to manage your earnings and payments effectively:

• Check your earnings daily in the app
• Ensure your bank details are always up to date
• Screenshot important trip details for potential disputes
• Understand Vaam's compensation policy
• Keep track of unusual passenger behavior or route issues"""
        
        elif issue_type == "technical":
            return """To prevent future app issues:

• Keep the Vaam app updated to the latest version
• Regularly restart your phone to clear memory
• Ensure strong internet connection while driving
• Give the app all necessary permissions
• Report bugs immediately when you notice them"""
        
        else:
            return """General tips for a better Vaam driving experience:

• Read and understand Vaam's driver policies
• Maintain professional communication with passengers
• Document any incidents immediately
• Use the app's help features for quick resolutions
• Stay informed about updates and policy changes"""
    
    def rank_solutions(self, solutions, context_analysis):
        """Rank solutions based on context and confidence scores."""
        urgency_weights = {
            "high": {"escalation": 1.5, "direct": 1.2, "step_by_step": 0.8, "educational": 0.3},
            "medium": {"direct": 1.3, "step_by_step": 1.2, "escalation": 0.9, "educational": 0.7},
            "low": {"educational": 1.2, "direct": 1.1, "step_by_step": 1.0, "escalation": 0.5}
        }
        
        urgency = context_analysis.get("urgency", "low")
        weights = urgency_weights.get(urgency, urgency_weights["low"])
        
        for solution in solutions:
            solution_type = solution["type"]
            base_confidence = solution["confidence"]
            weight = weights.get(solution_type, 1.0)
            solution["weighted_score"] = base_confidence * weight
        
        # Sort by weighted score and return the best solution
        solutions.sort(key=lambda x: x["weighted_score"], reverse=True)
        return solutions[0] if solutions else {"type": "fallback", "response": "I'm here to help. Please provide more details about your issue.", "confidence": 0.5}

    def smart_response_with_reasoning(self, message):
        """Generate a smart response using advanced reasoning."""
        try:
            # Analyze the message context
            context_analysis = self.analyze_issue_context(message)
            
            # Apply advanced reasoning
            reasoning_result = self.advanced_reasoning(message, context_analysis)
            
            # Get the best solution
            best_solution = reasoning_result["solution"]
            
            # Add reasoning transparency if confidence is low
            response = best_solution["response"]
            if reasoning_result["confidence"] < 0.7:
                response += f"\n\n(I'm {int(reasoning_result['confidence']*100)}% confident in this response. If this doesn't fully address your concern, please type 'escalate' for human support.)"
            
            # Store the interaction with reasoning data
            self.conversation_history.append({
                "role": "user", 
                "content": message, 
                "timestamp": datetime.datetime.now(),
                "context_analysis": context_analysis,
                "reasoning": reasoning_result
            })
            
            self.conversation_history.append({
                "role": "assistant", 
                "content": response, 
                "timestamp": datetime.datetime.now(),
                "solution_type": best_solution["type"],
                "confidence": reasoning_result["confidence"]
            })
            
            return response
            
        except Exception as e:
            print(f"Advanced reasoning failed: {e}")
            # Fallback to original method
            return self.generate_intelligent_response(message, self.analyze_issue_context(message))
# Example usage and testing
def main():
    """Test the enhanced Driver Service Agent."""
    agent = DriverServiceAgent()
    
    print("=== Enhanced Vaam Driver Service Agent ===")
    print("This AI agent can help with:")
    print("• Payment and compensation issues")
    print("• App bugs and technical problems") 
    print("• Complaints and service issues")
    print("• Vehicle requirements and documentation")
    print("• General inquiries and support")
    print("\nType 'quit' to exit, 'escalate' for human support")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\nDriver: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Thank you for using Vaam Driver Support. Drive safely!")
                break
            
            if user_input.lower() == 'escalate':
                response = agent.escalate_to_human("User requested escalation")
                print(f"\nVaam Support: {response}")
                continue
            
            if not user_input:
                continue
            
            # Use the smart reasoning response
            response = agent.smart_response_with_reasoning(user_input)
            print(f"\nVaam Support: {response}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! Drive safely!")
            break
        except Exception as e:
            print(f"\nSorry, I encountered an error: {e}")
            print("Please try again or type 'escalate' for human support.")

def test_ai_capabilities():
    """Test various AI capabilities of the agent."""
    agent = DriverServiceAgent()
    
    test_cases = [
        "I haven't received my payment for last week",
        "The app keeps crashing when I try to log in",
        "A passenger was very rude and I want to file a complaint", 
        "How do I update my bank details?",
        "What documents do I need for my vehicle?",
        "URGENT: I had an accident during a trip #ABC12345",
        "The GPS is not working and I'm lost",
        "I need compensation for trip #XYZ67890 - passenger cancelled last minute"
    ]
    
    print("=== Testing AI Agent Capabilities ===\n")
    
    for i, test_message in enumerate(test_cases, 1):
        print(f"Test {i}: {test_message}")
        print("-" * 50)
        
        # Test context analysis
        context = agent.analyze_issue_context(test_message)
        print(f"Context Analysis: {context}")
        
        # Test smart response
        response = agent.smart_response_with_reasoning(test_message)
        print(f"AI Response: {response}")
        print("=" * 50)
        print()

if __name__ == "__main__":
    # Uncomment the test you want to run:
    test_ai_capabilities()  # Test the AI capabilities
    # main()  # Interactive chat mode
