"""
main.py — Voice Agentic AI Assistant entry point.
Run: python main.py (microphone)  or  python main.py --text
"""
import os
import sys
import re
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from agent.voice import listen
from agent.text_processing import extract_intent, extract_entities, is_offensive
from agent.llm import get_ai_response
from agent.tts import speak
from agent.storage import log_conversation

MAX_CONTEXT_TURNS = 6

def _trim_context(context: list) -> list:
    return context[-MAX_CONTEXT_TURNS:] if len(context) > MAX_CONTEXT_TURNS else context

def get_weather(city: str = None) -> str:
    """Fetch real‑time weather from OpenWeatherMap."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Weather API key missing. Please add OPENWEATHER_API_KEY to .env file."
    if not city:
        city = os.getenv("DEFAULT_CITY", "London")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            temp = data['main']['temp']
            desc = data['weather'][0]['description'].capitalize()
            return f"The weather in {city} is {desc} with a temperature of {temp}°C."
        else:
            return f"Could not fetch weather for {city}. Please check the city name or try again."
    except Exception as e:
        print(f"Weather API error: {e}")
        return "Sorry, I couldn't retrieve the weather right now."

def _append_note(note: str) -> None:
    notes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "notes.txt")
    os.makedirs(os.path.dirname(notes_path), exist_ok=True)
    with open(notes_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M}] {note}\n")

def _handle_intent(intent: str, user_text: str, context: list, entities: dict) -> str:
    lower = user_text.lower()

    if intent == "offensive":
        return "I'm sorry, but I can't respond to offensive or harmful language. Please keep the conversation respectful."

    if intent == "greeting":
        keywords = entities.get("keywords", [])
        if "weather" in keywords or "date" in [extract_intent(w) for w in keywords]:
            return get_ai_response(user_text, context)
        return "Hello! I'm your Voice AI Assistant. How can I help you today?"

    if intent == "weather":
        # Try to extract a city name from user text (simple)
        words = lower.split()
        known_cities = ["london", "new york", "paris", "tokyo", "berlin", "mumbai", "delhi", "jaipur", "chicago", "los angeles"]
        city = next((w.title() for w in words if w in known_cities), None)
        return get_weather(city)   # uses DEFAULT_CITY if city is None

    if intent == "date":
        today = datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today}."

    if intent == "show_tasks":
        return ("Here are your tasks for today:\n"
                "  1. Review project report\n"
                "  2. Team stand-up at 10 AM\n"
                "  3. Reply to pending emails")

    if intent == "save_note":
        note = re.sub(r"\b(save|write down|note down|record)\b.{0,10}\bnote\b[:\-]?\s*", "", lower, flags=re.I).strip()
        note = note or "Empty note"
        _append_note(note)
        return f"Note saved: '{note}'"

    if intent == "set_reminder":
        return get_ai_response(f"Extract the reminder time and task from this and confirm it back to the user: {user_text}", context)

    if intent == "summarize":
        content = re.sub(r"\bsummariz(?:e|ing)\b[:\s]*", "", lower, flags=re.I).strip()
        if not content:
            return "What would you like me to summarize? Please say or type the text."
        return get_ai_response(f"Summarize this in one sentence: {content}", context)

    if intent == "search":
        return get_ai_response(f"Answer the following search query concisely: {user_text}", context)

    if intent == "calculate":
        return get_ai_response(f"Solve this calculation and give only the answer: {user_text}", context)

    if intent == "help":
        return ("I can help you with:\n"
                "  - Showing your tasks (say: show my tasks)\n"
                "  - Saving notes (say: save note: ...)\n"
                "  - Setting reminders\n"
                "  - Summarising text\n"
                "  - Answering general questions\n"
                "  - Web searches\nJust speak or type your request!")

    if intent in ("email", "phone"):
        return get_ai_response(user_text, context)

    return get_ai_response(user_text, context)

def main(text_mode: bool = False) -> None:
    print("=" * 55)
    print("  🎙️  Voice Agentic AI Assistant")
    print("  Press Ctrl+C to exit.")
    print("=" * 55)

    context = []

    while True:
        try:
            if text_mode:
                user_text = input("\n💬 You: ").strip()
                if not user_text:
                    continue
            else:
                user_text = listen()

            if not user_text:
                log_conversation("", "No input detected", "no_input")
                continue

            intent = extract_intent(user_text)
            entities = extract_entities(user_text)

            print(f"   [intent: {intent}]", end="")
            if any(entities[k] for k in ("emails", "phones", "dates", "keywords")):
                print(f"  [entities: {entities}]", end="")
            print()

            ai_response = _handle_intent(intent, user_text, context, entities)

            print(f"\n🤖 AI: {ai_response}\n")
            speak(ai_response)

            if intent != "offensive":
                context.append({"role": "user", "content": user_text})
                context.append({"role": "assistant", "content": ai_response})
                context = _trim_context(context)

            log_conversation(user_text, ai_response, intent, entities)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            continue

if __name__ == "__main__":
    text_mode = "--text" in sys.argv
    main(text_mode=text_mode)