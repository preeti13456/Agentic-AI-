import os
import pandas as pd
from datetime import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)
DATA_DIR = os.path.join(_PROJECT_ROOT, "data")
LOG_PATH = os.path.join(DATA_DIR, "conversation_log.csv")
_COLUMNS = ["timestamp", "user_text", "ai_response", "intent", "emails", "phones", "dates", "keywords"]

def log_conversation(user_text, ai_response, intent, entities=None):
    os.makedirs(DATA_DIR, exist_ok=True)
    entities = entities or {}
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_text": user_text,
        "ai_response": ai_response,
        "intent": intent,
        "emails": " | ".join(entities.get("emails", [])),
        "phones": " | ".join(entities.get("phones", [])),
        "dates": " | ".join(entities.get("dates", [])),
        "keywords": " | ".join(entities.get("keywords", [])),
    }
    df = pd.DataFrame([row], columns=_COLUMNS)
    if not os.path.exists(LOG_PATH):
        df.to_csv(LOG_PATH, index=False)
    else:
        df.to_csv(LOG_PATH, mode='a', header=False, index=False)