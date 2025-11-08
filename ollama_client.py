import os
import requests
import json

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")


def ollama_chat(model: str, messages, options=None) -> str:
    url = f"{OLLAMA_HOST}/api/chat"
    payload = {"model": model, "messages": messages}
    if options:
        payload["options"] = options

    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()

    if isinstance(data, dict) and "message" in data:
        return data["message"]["content"]
    return json.dumps(data, indent=2)

