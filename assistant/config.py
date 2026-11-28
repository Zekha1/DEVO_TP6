import os

from openai import OpenAI

LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen2.5:0.5b")
EMBED_BASE_URL = os.environ.get("EMBED_BASE_URL", LLM_BASE_URL)
EMBED_MODEL = os.environ.get("EMBED_MODEL", "all-minilm")
TOP_K = int(os.environ.get("TOP_K", "5"))
INDEX_PATH = "assistant/index.json"

chat_client = OpenAI(base_url=LLM_BASE_URL, api_key="unused")    # Ollama et vLLM ignorent la clé
embed_client = OpenAI(base_url=EMBED_BASE_URL, api_key="unused")