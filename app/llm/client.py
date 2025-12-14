# app/llm/client.py
import streamlit as st
import requests
import time
import json

API_URL = st.secrets.get("LLM_API_URL", "https://openrouter.ai/api/v1/chat/completions")
API_KEY = st.secrets.get("LLM_API_KEY")
MODEL_NAME = st.secrets.get("LLM_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:8501",
    "X-Title": "jobfitindex-dev",
}

def call_llm(messages, temperature=0.7, max_tokens=512):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    # DEBUG
    print("API_URL =", repr(API_URL))
    print("MODEL_NAME =", repr(MODEL_NAME))

    for attempt in range(3):
        response = requests.post(API_URL, json=payload, headers=HEADERS)

        print("STATUS:", response.status_code)
        print("BODY:", response.text[:500])

        if response.status_code == 429:
            time.sleep(5 * (attempt + 1))
            continue

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    raise RuntimeError("LLM rate-limited (429). Please try again later.")
