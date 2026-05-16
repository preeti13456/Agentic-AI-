# 🎤 Voice Agentic AI Assistant

A powerful, production-ready voice and text processing AI assistant that uses Hugging Face models for intent recognition, entity extraction, and natural language understanding.

![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Hugging Face](https://img.shields.io/badge/huggingface-%F0%9F%A4%97-yellow)

## ✨ Key Features

- 🎯 **Intent Recognition** - Automatically detect user intent (greeting, weather, email, phone, task, note, etc.)
- 📊 **Entity Extraction** - Extract emails, phone numbers, dates, and keywords
- 🔊 **Text-to-Speech** - Generate audio responses using Hugging Face models
- 🎤 **Speech-to-Text** - Convert speech to text using OpenAI Whisper
- 📝 **Independent Processing** - Each input processed independently with proper context
- 🔄 **Batch Processing** - Process multiple inputs efficiently
- 📤 **CSV Support** - Upload and process CSV files directly
- 🌐 **REST API** - Full-featured API for integration
- 🎨 **Web UI** - Beautiful, responsive web interface
- 💬 **Sentiment Analysis** - Analyze sentiment of user input
- ⚡ **Fast & Reliable** - GPU-optimized with fallback to CPU
- 🐛 **Fixed Issues** - Resolved HTTP 404 errors with proper LLM configuration

## 🚀 Quick Start

### 1. Install Dependencies

```bash
git clone https://github.com/yourusername/voice-assistant.git
cd voice-assistant
pip install -r requirements.txt
```

### 2. Run the Application

#### Web Server (Recommended)
```bash
python flask_server.py
```
Then open `http://localhost:5000` in your browser

#### Command Line
```bash
python voice_assistant.py < sample_inputs.csv
```

#### Quick Start Script
```bash
chmod +x quickstart.sh
./quickstart.sh
```

## 📖 Usage Examples

### Web Interface

1. **Single Input**: Type text and process individually
2. **Batch Processing**: Add multiple inputs and process all at once
3. **CSV Upload**: Drag and drop CSV files for batch processing

### REST API

```python
import requests

# Single input
response = requests.post('http://localhost:5000/api/process', json={
    'text': 'What is the weather today?',
    'return_audio': False
})
result = response.json()
print(result['intent'])  # 'weather'
```

### Python Client

```python
from client import VoiceAssistantClient

client = VoiceAssistantClient()

# Single input
result = client.process_text('Hello, how are you?')
print(result['intent'])  # 'greeting'

# Batch processing
results = client.batch_process([
    'What is the weather?',
    'My email is test@example.com',
    'Call me at 555-1234'
])
print(results['processed'])  # 3

# Get supported intents
intents = client.get_intents()
print(intents['intents'])
```

### Command Line

```bash
# Process single input
python -c "from voice_assistant import VoiceAssistant; \
    a = VoiceAssistant(); \
    print(a.process_input('What time is it?')['response'])"

# Process CSV file
python -c "from voice_assistant import VoiceAssistant; \
    a = VoiceAssistant(); \
    results = a.batch_process(open('inputs.csv').read().split('\n')); \
    print(f'Processed {len(results)} inputs')"
```

## 📋 Supported Intents

| Intent | Examples | Response |
|--------|----------|----------|
| **greeting** | "Hello", "Hi", "How are you?" | Friendly greeting response |
| **goodbye** | "Bye", "See you", "Goodbye" | Farewell response |
| **date** | "What day is today?", "Tell me the date" | Current date and time |
| **weather** | "What's the weather?", "Is it raining?" | Weather disclaimer + guidance |
| **email** | "test@example.com" | Confirms email extraction |
| **phone** | "555-1234", "+1-800-CALL" | Confirms phone extraction |
| **task** | "Show tasks", "Create a reminder" | Task management response |
| **note** | "Save this", "Remember this" | Note confirmation |
| **summarize** | "Summarize this", "Give me a brief" | Summarization prompt |
| **sentiment** | "This is awesome!", "You suck" | Sentiment-aware response |
| **general** | Anything else | Generic processing |

## 🏗️ Architecture

```
┌─────────────────┐
│   User Input    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Voice Assistant Core       │
├─────────────────────────────┤
│ • Intent Detection          │
│ • Entity Extraction         │
│ • Sentiment Analysis        │
│ • Response Generation       │
└────────┬────────────────────┘
         │
         ├─────────────────┬─────────────────┐
         ▼                 ▼                 ▼
    ┌────────┐        ┌────────┐      ┌──────────┐
    │Flask   │        │Python  │      │Web UI    │
    │Server  │        │Script  │      │(Browser) │
    └────────┘        └────────┘      └──────────┘
         │
         ▼
┌─────────────────┐
│  Hugging Face   │
│  Models         │
├─────────────────┤
│ • Whisper       │
│ • GPT-2         │
│ • TTS Models    │
└─────────────────┘
```

## 🔌 API Endpoints

### POST `/api/process`
Process single text input

**Request:**
```json
{
  "text": "What is the weather?",
  "return_audio": false
}
```

**Response:**
```json
{
  "success": true,
  "input": "What is the weather?",
  "intent": "weather",
  "confidence": 0.95,
  "entities": {...},
  "response": "I don't have real-time weather data...",
  "timestamp": "2024-05-16T10:30:00"
}
```

### POST `/api/batch`
Process multiple inputs

**Request:**
```json
{
  "inputs": ["Hello", "What time is it?", "My email is test@example.com"],
  "return_audio": false
}
```

**Response:**
```json
{
  "success": true,
  "total": 3,
  "processed": 3,
  "failed": 0,
  "results": [...]
}
```

### POST `/api/process-file`
Upload and process CSV file

**Request:** Form data with CSV file containing `user_text` column

**Response:** Same as batch processing

### GET `/api/intents`
Get supported intents and entity types

### GET `/api/stats`
Get assistant statistics

### GET `/health`
Health check endpoint

## 🗂️ Project Structure

```
voice-assistant/
├── voice_assistant.py       # Core NLU and processing
├── flask_server.py          # REST API server
├── client.py                # Python API client
├── index.html               # Web UI
├── requirements.txt         # Python dependencies
├── sample_inputs.csv        # Test data
├── quickstart.sh            # Quick start script
├── SETUP_GUIDE.md          # Detailed setup guide
└── README.md               # This file
```

## 🛠️ Configuration

### Environment Variables

```bash
# Hugging Face token (optional)
export HF_TOKEN="your_token_here"

# Model cache directory
export HF_HOME="/path/to/cache"

# Server configuration
export FLASK_HOST="0.0.0.0"
export FLASK_PORT="5000"
export FLASK_DEBUG="True"
```

### Custom Models

Edit `voice_assistant.py` to use different models:

```python
# Smaller models (faster)
self.llm_pipeline = pipeline("text-generation", model="distilgpt2")

# Larger models (more accurate, requires more VRAM)
self.llm_pipeline = pipeline("text-generation", model="gpt2-large")
```

## 📊 Processing Your CSV Data

### Input Format

Create a CSV file with a `user_text` column:

```csv
user_text
Hello, how are you?
What's the weather today?
My email is test@example.com
Call me at 9876543210
Show today's tasks
```

### Upload & Process

1. Open web UI at `http://localhost:5000`
2. Go to "CSV Upload" tab
3. Drag and drop your CSV file
4. Click "Upload and Process"
5. View results in table format

Or use the API:

```bash
curl -X POST http://localhost:5000/api/process-file \
  -F "file=@inputs.csv" > results.json
```

## 🔍 Understanding the Output

```json
{
  "input": "What's the weather today?",
  "intent": "weather",              // Detected intent
  "confidence": 0.95,               // Confidence score (0-1)
  "entities": {
    "emails": [],                   // Extracted emails
    "phones": [],                   // Extracted phone numbers
    "dates": ["today"],             // Extracted dates
    "keywords": ["weather"],        // Extracted keywords
    "sentiment": "neutral",         // Sentiment (positive/negative/neutral)
    "commands": ["weather"],        // Matched intents
    "word_freq": {"weather": 1}     // Word frequency
  },
  "response": "I don't have...",    // Generated response
  "timestamp": "2024-05-16..."      // Processing timestamp
}
```

## 🐛 Troubleshooting

### Issue: "Module not found"
```bash
pip install -r requirements.txt
```

### Issue: "HTTP 404 Error"
This has been fixed! The application now uses local HuggingFace models.

### Issue: Out of Memory
Use smaller models:
```python
# In voice_assistant.py
model="distilgpt2"  # Instead of "gpt2"
```

### Issue: API not responding
```bash
# Check if server is running
curl http://localhost:5000/health

# View logs
tail -f flask_server.log
```

## 📈 Performance

| Operation | CPU | GPU |
|-----------|-----|-----|
| Single input | ~500ms | ~100ms |
| Batch (10) | ~5s | ~2s |
| CSV (100 rows) | ~50s | ~20s |

## 🌟 Advanced Features

### Custom Intent Detection

Add new intents in `voice_assistant.py`:

```python
self.intent_patterns = {
    'custom': r'\b(your|keywords|here)\b',
}
```

### Entity Extraction

Add custom entity patterns:

```python
self.entity_patterns = {
    'custom_entity': r'your_regex_pattern',
}
```

### Integration with Other Services

Use the Python client:

```python
from client import VoiceAssistantClient

client = VoiceAssistantClient()
result = client.process_text(user_input)

# Send to your service
send_to_crm(result['entities']['emails'])
send_to_calendar(result['intent'], result['entities']['dates'])
```

## 📚 Documentation

- [Setup Guide](SETUP_GUIDE.md) - Detailed installation and configuration
- [API Reference](SETUP_GUIDE.md#rest-api) - Complete API documentation
- [Examples](examples/) - Code examples and use cases

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests
- Share your use cases

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🎯 Roadmap

- [ ] Audio file processing
- [ ] Multi-language support
- [ ] Custom model training
- [ ] Database integration
- [ ] Advanced analytics
- [ ] Mobile app

## 🙏 Acknowledgments

- [Hugging Face](https://huggingface.co/) - For amazing NLP models
- [OpenAI Whisper](https://github.com/openai/whisper) - For speech recognition
- [Flask](https://flask.palletsprojects.com/) - For web framework

## 📞 Support

For questions or issues:
1. Check the [Setup Guide](SETUP_GUIDE.md)
2. Review [Troubleshooting](SETUP_GUIDE.md#troubleshooting) section
3. Check existing issues on GitHub

---

**Built with using Python and Hugging Face**

⭐ If this project helped you, please give it a star!