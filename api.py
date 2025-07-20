import random
import streamlit as st
import requests

def get_random_api_key():
    keys = st.secrets["openrouter_keys"]
    return random.choice(list(keys.values()))

def call_openrouter_api(prompt):
    api_key = get_random_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openchat/openchat-3.5",
        "messages": [
            {"role": "system", "content": "You are a world-class HR AI assistant. Provide structured insights and clear ranking for best-fit candidates."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "No response")
    except Exception as e:
        return f"API Error: {str(e)}"

def trim_cv(text, max_lines=40):
    return "\n".join(text.strip().splitlines()[:max_lines])
