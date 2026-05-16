"""
text_processing.py — RegEx, pattern matching, intent detection, entity
extraction, and content guardrails for the Voice Agentic AI Assistant.

Covers all six required categories:
    i.   Greetings
    ii.  Dates
    iii. Email IDs
    iv.  Phone numbers
    v.   Keywords / intents
    vi.  Commands
"""

import re
from collections import Counter

# ---------------------------------------------------------------------------
# 1.  OFFENSIVE / HARMFUL GUARDRAILS
# ---------------------------------------------------------------------------

# Tier-1: explicit profanity (exact word match)
_PROFANITY: list[str] = [
    "damn", "suck", "shit", "fuck", "bitch", "crap", "asshole", "bastard",
    "dick", "piss", "whore", "slut", "cunt", "fag", "faggot",
    "retard", "nigger", "spic", "kike", "chink", "wetback",
]

# Tier-2: harmful / threatening intent phrases
_HARMFUL_PHRASES: list[str] = [
    "shut up", "i hate you", "kill yourself", "go die", "i want to kill",
    "i will hurt", "bomb", "terrorist", "suicide", "self-harm",
    "how to make a weapon", "how to hack", "make explosives",
]

# Combined pattern (word-boundary aware for single words, substring for phrases)
_OFFENSIVE_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in _PROFANITY) + r")\b"
    r"|(" + "|".join(re.escape(p) for p in _HARMFUL_PHRASES) + r")",
    re.IGNORECASE,
)


def is_offensive(text: str) -> bool:
    """Return True if the text contains offensive or harmful content."""
    return bool(_OFFENSIVE_PATTERN.search(text))


# ---------------------------------------------------------------------------
# 2.  REGEX PATTERNS
# ---------------------------------------------------------------------------

# ii. Dates — DD/MM/YYYY, MM-DD-YYYY, YYYY-MM-DD, "15th June 2024", "June 15 2024"
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
    r"\b(today|tomorrow|yesterday|next\s+(?:monday|tuesday|wednesday|thursday|"
    r"friday|saturday|sunday|week|month|year)|last\s+(?:week|month|year)|"
    r"this\s+(?:week|month|year))\b",
    re.IGNORECASE,
)

# iii. Email IDs
_EMAIL = re.compile(r"\b[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+\b", re.IGNORECASE)

# iv. Phone numbers — E.164, US, international with spaces/dashes/dots
_PHONE = re.compile(
    r"(?<!\d)"                            # no preceding digit
    r"(\+?1[\s\-.]?)?"                    # optional country code
    r"(\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4})"
    r"(?!\d)",                            # no trailing digit
)

# v. Keywords — single-token high-value words
_KEYWORDS = re.compile(
    r"\b(task|note|remind(?:er)?|schedul(?:e|ing)|meeting|appointment|"
    r"weather|news|search|find|look up|calculate|convert|translate|"
    r"timer|alarm|play|stop|pause|resume|navigate|map|direction)\b",
    re.IGNORECASE,
)

# vi. Commands — imperative verb phrases
_COMMANDS = re.compile(
    r"\b(show|save|send|open|close|read|write|add|remove|delete|update|"
    r"create|list|get|fetch|check|set|start|end|run|summarize|help)\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# 3.  INTENT DETECTION
# ---------------------------------------------------------------------------

# Ordered list of (intent_label, compiled_regex) — first match wins.
_INTENT_RULES: list[tuple[str, re.Pattern]] = [
    # i. Greetings
    ("greeting",    re.compile(
        r"\b(hi|hello|hey|howdy|good\s+(?:morning|afternoon|evening|night)|"
        r"what'?s\s+up|greetings)\b", re.IGNORECASE)),

    # Agentic commands (before generic keyword checks)
    ("show_tasks",  re.compile(r"\b(show|list|what are)\b.{0,20}\btasks?\b", re.IGNORECASE)),
    ("save_note",   re.compile(r"\b(save|write down|note down|record)\b.{0,10}\bnote\b", re.IGNORECASE)),
    ("set_reminder",re.compile(r"\b(set|add|create)\b.{0,15}\breminder\b", re.IGNORECASE)),
    ("summarize",   re.compile(r"\bsummariz(?:e|ing)\b", re.IGNORECASE)),
    ("weather",     re.compile(r"\b(weather|forecast|temperature|rain|sunny|humidity|climate today)\b", re.IGNORECASE)),
    ("search",      re.compile(r"\b(search|find|look up|google)\b", re.IGNORECASE)),
    ("calculate",   re.compile(r"\b(calculat(?:e|or)|what is \d|how much is)\b", re.IGNORECASE)),
    ("help",        re.compile(r"\b(help|assist|support|what can you do)\b", re.IGNORECASE)),

    # ii–iv entity-type intents (detected via entity presence)
    # Conversational date questions must come before numeric pattern checks
    ("date",        re.compile(
        r"\b(what'?s? (the )?(day|date|today)"
        r"|what (is (the )?)?(day|date)(\s|$)"
        r"|what day (is it|today|is today)"
        r"|today'?s? (date|day)|current date|day of (the )?week)\b",
        re.IGNORECASE)),
    ("date",        _DATE_NUMERIC),
    ("date",        _DATE_VERBAL),
    ("email",       _EMAIL),
    ("phone",       _PHONE),
]


def extract_intent(text: str) -> str:
    """
    Return the intent label for *text*.

    Priority order:
        1. Offensive → "offensive"
        2. Rule-based regex (in _INTENT_RULES order)
        3. Fallback → "general"
    """
    if is_offensive(text):
        return "offensive"

    for label, pattern in _INTENT_RULES:
        if pattern.search(text):
            return label

    return "general"


# ---------------------------------------------------------------------------
# 4.  ENTITY EXTRACTION
# ---------------------------------------------------------------------------

def extract_entities(text: str) -> dict:
    """
    Extract structured entities from *text*.

    Returns a dict with keys:
        emails, phones, dates, keywords, commands, word_freq
    """
    emails   = _EMAIL.findall(text)
    phones   = [m[1] for m in _PHONE.findall(text) if m[1]]
    dates    = (
        _DATE_NUMERIC.findall(text)
        + _DATE_YYYY.findall(text)
        + _DATE_VERBAL.findall(text)
        + _DATE_VERBAL_INV.findall(text)
        + _DATE_RELATIVE.findall(text)
    )
    keywords = _KEYWORDS.findall(text)
    commands = _COMMANDS.findall(text)

    # Word-frequency counter (stopwords stripped) — uses collections.Counter
    _STOPWORDS = {
        "the", "a", "an", "is", "it", "in", "on", "at", "to", "of",
        "and", "or", "for", "with", "i", "my", "me", "you", "this",
        "that", "was", "are", "be", "been", "have", "has", "do", "did",
    }
    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    word_freq = Counter(w for w in words if w not in _STOPWORDS)

    return {
        "emails":   sorted(set(emails)),
        "phones":   sorted(set(phones)),
        "dates":    list(dict.fromkeys(dates)),   # deduplicate, preserve order
        "keywords": sorted(set(k.lower() for k in keywords)),
        "commands": sorted(set(c.lower() for c in commands)),
        "word_freq": dict(word_freq.most_common(10)),
    }


# ---------------------------------------------------------------------------
# 5.  VALIDATION HELPERS
# ---------------------------------------------------------------------------

def validate_email(email: str) -> bool:
    """Return True if *email* looks like a valid address."""
    return bool(re.fullmatch(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", email
    ))


def validate_phone(phone: str) -> bool:
    """Return True if *phone* has 10–15 digits (E.164 range)."""
    digits = re.sub(r"\D", "", phone)
    return 10 <= len(digits) <= 15