import re
from collections import Counter

OFFENSIVE_WORDS = [
    "damn", "suck", "shit", "fuck", "bitch", "crap", "asshole", "bastard",
    "dick", "piss", "whore", "slut", "cunt", "fag", "faggot",
    "retard", "nigger", "spic", "kike", "chink", "wetback"
]

_HARMFUL_PHRASES = [
    "shut up", "i hate you", "kill yourself", "go die", "i want to kill",
    "i will hurt", "bomb", "terrorist", "suicide", "self-harm"
]

_OFFENSIVE_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in OFFENSIVE_WORDS) + r")\b"
    r"|(" + "|".join(re.escape(p) for p in _HARMFUL_PHRASES) + r")",
    re.IGNORECASE,
)

def is_offensive(text: str) -> bool:
    return bool(_OFFENSIVE_PATTERN.search(text))

_DATE_NUMERIC   = re.compile(r"\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b")
_DATE_YYYY      = re.compile(r"\b\d{4}[/\-]\d{1,2}[/\-]\d{1,2}\b")
_DATE_VERBAL    = re.compile(
    r"\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|"
    r"apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|"
    r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{2,4})\b",
    re.IGNORECASE,
)
_DATE_VERBAL_INV = re.compile(
    r"\b((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|"
    r"dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{2,4})\b",
    re.IGNORECASE,
)
_DATE_RELATIVE  = re.compile(
    r"\b(today|tomorrow|yesterday|next\s+(?:monday|tuesday|...)|last\s+(?:week|month|year))\b",
    re.IGNORECASE,
)
_EMAIL = re.compile(r"\b[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+\b", re.IGNORECASE)
_PHONE = re.compile(
    r"(?<!\d)(\+?1[\s\-.]?)?(\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4})(?!\d)"
)
_KEYWORDS = re.compile(
    r"\b(task|note|remind(?:er)?|schedul(?:e|ing)|weather|news|search|find|look up|calculate|timer|alarm)\b",
    re.IGNORECASE,
)
_COMMANDS = re.compile(
    r"\b(show|save|send|open|close|read|write|add|remove|delete|update|create|list|get|fetch|check|set|start|end|run|summarize|help)\b",
    re.IGNORECASE,
)

_INTENT_RULES = [
    ("greeting",    re.compile(r"\b(hi|hello|hey|good morning|good afternoon|good evening)\b", re.I)),
    ("show_tasks",  re.compile(r"\b(show|list|what are)\b.{0,20}\btasks?\b", re.I)),
    ("save_note",   re.compile(r"\b(save|write down|note down|record)\b.{0,10}\bnote\b", re.I)),
    ("set_reminder",re.compile(r"\b(set|add|create)\b.{0,15}\breminder\b", re.I)),
    ("summarize",   re.compile(r"\bsummariz(?:e|ing)\b", re.I)),
    ("weather",     re.compile(r"\b(weather|forecast|temperature|rain|sunny|humidity|climate)\b", re.I)),
    ("search",      re.compile(r"\b(search|find|look up|google)\b", re.I)),
    ("calculate",   re.compile(r"\b(calculat(?:e|or)|what is \d|how much is)\b", re.I)),
    ("help",        re.compile(r"\b(help|assist|support|what can you do)\b", re.I)),
    ("date",        re.compile(r"\b(what'?s? (the )?(day|date|today)|current date|day of week)\b", re.I)),
    ("email",       _EMAIL),
    ("phone",       _PHONE),
]

def extract_intent(text: str) -> str:
    if is_offensive(text):
        return "offensive"
    for label, pattern in _INTENT_RULES:
        if pattern.search(text):
            return label
    return "general"

def extract_entities(text: str) -> dict:
    emails   = _EMAIL.findall(text)
    phones   = [m[1] for m in _PHONE.findall(text) if m[1]]
    dates    = (_DATE_NUMERIC.findall(text) + _DATE_YYYY.findall(text) +
                _DATE_VERBAL.findall(text) + _DATE_VERBAL_INV.findall(text) +
                _DATE_RELATIVE.findall(text))
    keywords = _KEYWORDS.findall(text)
    commands = _COMMANDS.findall(text)
    _STOPWORDS = {"the", "a", "an", "is", "it", "in", "on", "at", "to", "of", "and", "or", "for", "with", "i", "my", "me", "you", "this", "that", "was", "are", "be", "been", "have", "has", "do", "did"}
    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    word_freq = Counter(w for w in words if w not in _STOPWORDS)
    return {
        "emails":   sorted(set(emails)),
        "phones":   sorted(set(phones)),
        "dates":    list(dict.fromkeys(dates)),
        "keywords": sorted(set(k.lower() for k in keywords)),
        "commands": sorted(set(c.lower() for c in commands)),
        "word_freq": dict(word_freq.most_common(10)),
    }