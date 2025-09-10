import requests, json

headers = {
    "Authorization": "Bearer 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",
    "Content-Type": "application/json"
}

payload = {
    "model": "deepseek/deepseek-chat-v3.1:free",
    "messages": [{"role": "user", "content": "Hello"}]
}

resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                     headers=headers, json=payload)

print(resp.status_code)
print(resp.text)
