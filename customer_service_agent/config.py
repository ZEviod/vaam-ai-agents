# Configuration for Vaam Smart Customer Service Agent

# Hugging Face API Configuration (Free)
HF_API_TOKEN = "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"  # You can get your own free token from huggingface.co
HF_MODEL = "microsoft/DialoGPT-medium"  # Free conversation model

# Alternative free models you can try:
# HF_MODEL = "facebook/blenderbot-400M-distill"  # Facebook's BlenderBot
# HF_MODEL = "microsoft/DialoGPT-small"          # Smaller, faster DialoGPT
# HF_MODEL = "google/flan-t5-base"               # Google's T5 model

# Company Configuration
COMPANY_NAME = "Vaam"
COMPANY_EMAIL = "support@vaam.co.uk"

# Server Configuration
HOST = "0.0.0.0"
PORT = 5000
DEBUG = False

# AI Model Settings
AI_TIMEOUT = 30  # seconds
AI_MAX_TOKENS = 200
AI_TEMPERATURE = 0.7

# Features Configuration
ENABLE_TICKET_CREATION = True
ENABLE_CONVERSATION_MEMORY = True
ENABLE_SENTIMENT_ANALYSIS = True
MAX_CONVERSATION_HISTORY = 10  # messages to remember per session
