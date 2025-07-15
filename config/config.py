import os

LLM_API_URL = "Your LLM API URL"
LLM_API_KEY = "Your LLM API KEY"

if not LLM_API_URL:
    raise ValueError("⚠️ Chưa thiết lập LLM_API_URL trong .env")

if not LLM_API_KEY:
    raise ValueError("⚠️ Chưa thiết lập LLM_API_KEY trong .env")
