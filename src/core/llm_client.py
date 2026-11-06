"""Simple LLM client supporting OpenAI, Gemini, and Ollama."""

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama

# Load .env from project root (works regardless of cwd)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# Read configuration from .env file
PROVIDER = os.getenv("PROVIDER", "openai").lower()
MODEL = os.getenv("MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
TIMEOUT = 60

def get_langchain_llm():
    """
    Returns Langchain LLM wrapper based on .env PROVIDER.
    Used by agents_langchain/ (Langchain-based agents).
    """
    if PROVIDER == "openai":
        return ChatOpenAI(
            model=MODEL,
            api_key=OPENAI_API_KEY
        )

    elif PROVIDER == "google":
        return ChatGoogleGenerativeAI(
            model=MODEL,
            google_api_key=GOOGLE_API_KEY
        )

    elif PROVIDER == "ollama":
        return Ollama(
            model=MODEL,
            base_url=OLLAMA_HOST
        )

    else:
        raise ValueError(f"Unsupported provider: {PROVIDER}")