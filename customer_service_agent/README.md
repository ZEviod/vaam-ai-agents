# 🚗 Vaam Smart Customer Service Agent

An intelligent AI-powered customer service chatbot that can think, reason, and resolve customer issues automatically using **FREE** AI models.

## ✨ Key Features

### 🤖 **Smart AI Assistant**

- Uses **FREE** Hugging Face AI models (no OpenAI API key needed!)
- Intelligent issue analysis and categorization
- Context-aware responses with conversation memory
- Emotional intelligence and empathy

### 🎯 **Automatic Issue Resolution**

- **Lost Items**: Automatically contacts drivers and arranges returns
- **Driver Behavior**: Investigates safety concerns and takes action
- **Billing Issues**: Reviews charges and processes refunds
- **Service Quality**: Resolves app issues and booking problems

### 🎫 **Smart Ticketing System**

- Automatically creates tickets for complex issues
- Priority assignment based on urgency
- Team routing based on issue type
- Full conversation history tracking

### 🌐 **Modern Web Interface**

- Beautiful, responsive design
- Mobile-friendly chat interface
- Real-time messaging with Socket.IO
- Typing indicators and status updates

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python run.py
```

### 3. Open Your Browser

Visit: http://localhost:5000

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Free AI Model Options
HF_MODEL = "microsoft/DialoGPT-medium"        # Default (recommended)
# HF_MODEL = "facebook/blenderbot-400M-distill"  # Alternative
# HF_MODEL = "microsoft/DialoGPT-small"          # Faster, smaller

# Company Settings
COMPANY_NAME = "Vaam"
COMPANY_EMAIL = "support@vaam.co.uk"
```

## 💡 How It Works

### 1. **Issue Analysis**

The AI analyzes customer messages using:

- Pattern recognition for common issues
- Sentiment analysis for emotional state
- Context extraction for urgency and details

### 2. **Intelligent Response Generation**

- Uses FREE Hugging Face AI models
- Applies company policies automatically
- Provides step-by-step resolution plans
- Escalates when necessary

### 3. **Smart Ticket Creation**

- Automatically creates tickets for complex issues
- Routes to appropriate teams
- Tracks resolution progress

## 🆓 Free AI Models Used

This system uses **completely free** AI models from Hugging Face:

1. **Microsoft DialoGPT-medium** (Default)

   - Conversational AI trained by Microsoft
   - Excellent for customer service dialogues
   - No API costs

2. **Facebook BlenderBot** (Alternative)

   - Facebook's open-source chatbot
   - Great empathy and personality
   - Completely free

3. **Google FLAN-T5** (Alternative)
   - Google's instruction-following model
   - Good for structured responses
   - Free to use

## 📱 Example Conversations

### Lost Item Example:

**Customer**: "I left my phone in the car yesterday"
**AI**: "I understand you've lost your phone during your Vaam ride. I'll help you recover it. Can you please provide your ride details (date, time, and pickup/dropoff locations) so I can contact your driver immediately?"

### Driver Issue Example:

**Customer**: "The driver was speeding and I felt unsafe"
**AI**: "I'm sorry to hear about your experience with our driver. Your safety is our top priority. I'm escalating this to our specialist team for immediate attention. Ticket #VAAM-000001 has been created to track this issue."

## 🔒 No API Keys Required

Unlike other solutions that require expensive API keys:

- ✅ Uses FREE Hugging Face models
- ✅ No OpenAI subscription needed
- ✅ No monthly API costs
- ✅ Unlimited conversations

## 🛠️ Technical Stack

- **Backend**: Python Flask + Socket.IO
- **Frontend**: Modern HTML5 + CSS3 + JavaScript
- **AI**: Hugging Face Transformers (FREE)
- **Database**: In-memory (easily extensible)

## 📊 Supported Issue Types

1. **Lost Items** 📱

   - Automatic driver contact
   - Return coordination
   - Compensation handling

2. **Driver Behavior** 🚗

   - Safety investigations
   - Disciplinary actions
   - Customer follow-up

3. **Billing Issues** 💳

   - Charge reviews
   - Refund processing
   - Dispute resolution

4. **Service Quality** ⭐
   - App troubleshooting
   - Booking assistance
   - Technical support

## 🚀 Getting Started (Detailed)

### Prerequisites

- Python 3.7+
- Internet connection (for AI model API calls)

### Installation

```bash
# Clone or download the project
cd customer_service_agent

# Install requirements
pip install -r requirements.txt

# Run the application
python run.py
```

### First Use

1. Open http://localhost:5000 in your browser
2. Try asking: "I lost my phone in the car"
3. Watch the AI analyze, respond, and create tickets automatically!

## 🔧 Customization

### Add New Issue Types

Edit the `company_policies` dictionary in `customer_service_agent.py`:

```python
"new_issue_type": {
    "description": "Description of the issue",
    "resolution_steps": ["Step 1", "Step 2", "Step 3"],
    "escalation_triggers": ["trigger1", "trigger2"],
    "response_template": "Template response"
}
```

### Change AI Models

Update `HF_MODEL` in `config.py` to use different free models.

## 🆘 Troubleshooting

### AI Not Responding?

- Check internet connection
- Verify Hugging Face API is accessible
- Try a different model in `config.py`

### Installation Issues?

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues and pull requests to improve the system!

---

**Built with ❤️ for better customer service experiences**
