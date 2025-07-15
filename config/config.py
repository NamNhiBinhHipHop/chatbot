import os

LLM_API_URL = "https://your-llm-endpoint.com/v1/chat/completions"
LLM_API_KEY = "your_llm_api_key_here"

if not LLM_API_URL:
    raise ValueError("⚠️ Chưa thiết lập LLM_API_URL trong .env")

if not LLM_API_KEY:
    raise ValueError("⚠️ Chưa thiết lập LLM_API_KEY trong .env")
