"""
main.py — Voice Agentic AI Assistant entry point.

Run:
    python main.py            # microphone mode (default)
    python main.py --text     # type input instead of speaking (useful for testing)
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()  # must be before any agent imports that read env vars

from agent.voice          import listen
from agent.text_processing import (
    extract_intent, extract_entities, is_offensive,
)
from agent.llm            import get_ai_response
from agent.tts            import speak
from agent.storage        import log_conversation

# ── Rolling conversation context (last N turns) for multi-turn LLM calls ──
MAX_CONTEXT_TURNS = 6  # keep last 3 user+assistant pairs

def _trim_context(context: list) -> list:
    """Keep only the most recent MAX_CONTEXT_TURNS messages."""
    return context[-MAX_CONTEXT_TURNS:] if len(context) > MAX_CONTEXT_TURNS else context


def _handle_intent(intent: str, user_text: str, context: list, entities: dict) -> str:
    """
    Route to the correct handler based on *intent* and return the response string.
    Falls through to LLM for general / unknown intents.
    """
    lower = user_text.lower()

    if intent == "offensive":
        return (
            "I'm sorry, but I can't respond to offensive or harmful language. "
            "Please keep the conversation respectful."
        )

    if intent == "greeting":
        # Check for additional intent markers (weather, date, etc.) and use LLM if found
        keywords = entities.get("keywords", [])
        if "weather" in keywords or "date" in [extract_intent(w) for w in keywords]:
            return get_ai_response(user_text, context)
        return "Hello! I'm your Voice AI Assistant. How can I help you today?"

    if intent == "weather":
        return get_ai_response(
            f"The current date is Wednesday, May 16, 2026. Please answer this weather-related query: {user_text}",
            context
        )

    if intent == "date":
        return get_ai_response(
            f"The current date is Wednesday, May 16, 2026. Please answer this date/time query: {user_text}",
            context
        )

    if intent == "show_tasks":
        # In production: query a task DB / file here
        return (
            "Here are your tasks for today:\n"
            "  1. Review project report\n"
            "  2. Team stand-up at 10 AM\n"
            "  3. Reply to pending emails"
        )

    if intent == "save_note":
        # Strip command words to isolate the note body
        note = re.sub(
            r"\b(save|write down|note down|record)\b.{0,10}\bnote\b[:\-]?\s*",
            "", lower, flags=re.IGNORECASE
        ).strip()
        note = note or "Empty note"
        _append_note(note)
        return f"Note saved: '{note}'"

    if intent == "set_reminder":
        return get_ai_response(
            f"Extract the reminder time and task from this and confirm it back to the user: {user_text}",
            context,
        )

    if intent == "summarize":
        # Strip "summarize" command words to get the content
        content = re.sub(r"\bsummariz(?:e|ing)\b[:\s]*", "", lower, flags=re.IGNORECASE).strip()
        if not content:
            return "What would you like me to summarize? Please say or type the text."
        return get_ai_response(f"Summarize this in one sentence: {content}", context)

    if intent == "search":
        return get_ai_response(
            f"Answer the following search query concisely: {user_text}", context
        )

    if intent == "calculate":
        return get_ai_response(
            f"Solve this calculation and give only the answer: {user_text}", context
        )

    if intent == "help":
        return (
            "I can help you with:\n"
            "  - Showing your tasks (say: show my tasks)\n"
            "  - Saving notes (say: save note: ...)\n"
            "  - Setting reminders\n"
            "  - Summarising text\n"
            "  - Answering general questions\n"
            "  - Web searches\n"
            "Just speak or type your request!"
        )

    if intent in ("email", "phone", "date"):
        return get_ai_response(user_text, context)

    # Default: send to LLM with rolling context
    return get_ai_response(user_text, context)


def _append_note(note: str) -> None:
    """Append *note* to data/notes.txt."""
    notes_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "notes.txt"
    )
    os.makedirs(os.path.dirname(notes_path), exist_ok=True)
    from datetime import datetime
    with open(notes_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M}] {note}\n")


# ── Inline import needed by _handle_intent ──
import re


def main(text_mode: bool = False) -> None:
    print("=" * 55)
    print("  🎙️  Voice Agentic AI Assistant")
    print("  Press Ctrl+C to exit.")
    print("=" * 55)

    context: list[dict] = []  # rolling LLM conversation context

    while True:
        try:
            # ── 1. Input ──────────────────────────────────────────────────
            if text_mode:
                user_text = input("\n💬 You: ").strip()
                if not user_text:
                    continue
            else:
                user_text = listen()

            if not user_text:
                log_conversation("", "No input detected", "no_input")
                continue

            # ── 2. Text processing ───────────────────────────────────────
            intent   = extract_intent(user_text)
            entities = extract_entities(user_text)

            print(f"   [intent: {intent}]", end="")
            if any(entities[k] for k in ("emails", "phones", "dates", "keywords")):
                print(f"  [entities: {entities}]", end="")
            print()

            # ── 3. Handle intent → AI response ───────────────────────────
            ai_response = _handle_intent(intent, user_text, context, entities)

            # ── 4. Output ─────────────────────────────────────────────────
            print(f"\n🤖 AI: {ai_response}\n")
            speak(ai_response)

            # ── 5. Update rolling context (skip offensive turns) ─────────
            if intent != "offensive":
                context.append({"role": "user",      "content": user_text})
                context.append({"role": "assistant",  "content": ai_response})
                context = _trim_context(context)

            # ── 6. Persist to CSV ─────────────────────────────────────────
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
