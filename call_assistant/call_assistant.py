"""
# Call Assistant
# Purpose: Replace human call center with an AI voice model to answer inbound calls.
# Core Features:
# - Voice-to-text + intent detection
# - Answer FAQs
# - Flag unclosed calls for human intervention
# - Escalate to human when needed (take note of issue in email format)
# - Send summaries post-call
"""

import random
import time

class CallAssistant:
    def __init__(self):
        self.faq_answers = {
            "how do i book a ride": "To book a ride with Vaam, open the app, enter your destination, and confirm your pickup location.",
            "what are your prices": "Vaam prices vary based on distance, time, and demand. You can see an estimate before booking.",
            "how do i contact support": "You can contact Vaam support via the app or by emailing support@vaam.co.uk.",
            "where is my driver": "You can track your driver in real-time on the Vaam app after booking.",
            "how do i cancel a ride": "To cancel a ride, go to your trip in the app and tap 'Cancel'. Cancellation fees may apply."
        }
        self.unclosed_calls = set()

    def voice_to_text(self, audio_data):
        """Simulate voice-to-text and intent detection for Vaam."""
        # For demo, treat audio_data as text input
        text = audio_data.lower()
        if any(q in text for q in self.faq_answers):
            intent = "faq"
        elif "complaint" in text or "lost" in text:
            intent = "escalate"
        else:
            intent = "general"
        return {"text": text, "intent": intent}

    def answer_faq(self, question):
        """Answer frequently asked questions for Vaam."""
        question = question.lower()
        for q, a in self.faq_answers.items():
            if q in question:
                return a
        return "I'm sorry, I don't have an answer for that. Please contact Vaam support."

    def flag_unclosed_call(self, call_id):
        """Flag calls that need human intervention."""
        self.unclosed_calls.add(call_id)
        print(f"Call {call_id} flagged for human intervention.")

    def escalate_to_human(self, call_id, issue):
        """Escalate call and send issue summary in email format."""
        email = f"""To: support@vaam.co.uk\nSubject: Escalation Required for Call {call_id}\n\nIssue: {issue}\nPlease review and respond as soon as possible.\n"""
        print(email)
        self.flag_unclosed_call(call_id)
        return email

    def send_post_call_summary(self, call_id):
        """Send summary after call ends."""
        summary = f"Call {call_id} completed. Summary sent to user and logged for Vaam records."
        print(summary)
        return summary

def main():
    assistant = CallAssistant()
    call_count = 0
    max_calls = 5  # You can set this to None for infinite loop
    user_inputs_bank = [
        ["How do I book a ride?", "Where is my driver?", "I lost my wallet in the car.", "Thank you!"],
        ["What are your prices?", "How do I cancel a ride?", "I have a complaint about my last trip.", "Thanks!"],
        ["How do I contact support?", "I lost my phone in the car.", "Thank you!"],
        ["Where is my driver?", "How do I book a ride?", "Thank you!"],
        ["How do I cancel a ride?", "I have a complaint.", "Thanks!"]
    ]
    try:
        while max_calls is None or call_count < max_calls:
            call_id = random.randint(1000, 9999)
            print("\nIncoming call...\n")
            print("AI: Hello! Thank you for calling Vaam, London's trusted ride service. How can I help you today?")
            user_inputs = random.choice(user_inputs_bank)
            for user_input in user_inputs:
                print(f"User: {user_input}")
                result = assistant.voice_to_text(user_input)
                if result["intent"] == "faq":
                    answer = assistant.answer_faq(result["text"])
                    print("AI:", answer)
                elif result["intent"] == "escalate":
                    print("AI: I'm sorry to hear that. Let me escalate this to our support team.")
                    assistant.escalate_to_human(call_id, user_input)
                else:
                    print("AI: How else can I assist you with your Vaam ride today?")
            assistant.send_post_call_summary(call_id)
            print("AI: Thank you for calling Vaam. Have a great day!")
            call_count += 1
            time.sleep(2)  # Wait before next call
    except KeyboardInterrupt:
        print("\nAgent stopped by user.")

if __name__ == "__main__":
    main()
