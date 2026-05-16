"""
voice.py — Microphone capture with ambient-noise calibration.

Fixes:
- Calibrates for ambient noise before each listen so the recogniser
  doesn't hang waiting for a "loud enough" signal.
- Short, explicit timeouts prevent infinite blocking.
- Falls back gracefully on every known sr exception.
"""

import speech_recognition as sr

_recognizer = sr.Recognizer()
_recognizer.pause_threshold = 0.8   # seconds of silence = end of phrase


def listen(timeout: int = 10, phrase_time_limit: int = 12) -> str:
    import speech_recognition as sr
    with sr.Microphone() as source:
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Say something...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except Exception as e:
            print(f"Mic test failed: {e}")
            return ""