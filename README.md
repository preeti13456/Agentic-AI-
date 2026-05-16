# Voice Agentic AI Assistant

A voice‑controlled assistant with real‑time date, weather API, OpenRouter LLM, and CSV logging.

## Setup
1. Clone the repo.
2. Create a virtual environment: `python3 -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your API keys.
5. Run: `python main.py` (microphone) or `python main.py --text` (type input).

## API Keys needed
- [OpenRouter](https://openrouter.ai/keys) – free LLM access
- [OpenWeatherMap](https://home.openweathermap.org/users/sign_up) – free weather API

## Features
- Voice & text input
- Intent detection (greeting, weather, date, tasks, notes, reminders, summarise, search, calculate)
- Offensive language guardrails
- Real‑time weather and current date
- CSV logging in `data/conversation_log.csv`
- Text‑to‑speech output