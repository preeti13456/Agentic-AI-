import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
model = os.getenv("OPENROUTER_MODEL", "openrouter/free")  # free model

if not api_key:
    raise ValueError("OPENROUTER_API_KEY not set in .env file")

client = OpenAI(api_key=api_key, base_url=base_url)

def get_ai_response(prompt: str, context: list | None = None) -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful, concise AI assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM API error: {e}")
        return "Sorry, I couldn't get a response from the AI."