MODELS = {
    "deepseek-chat": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        "payload": lambda messages: {
            "model": "deepseek/deepseek-chat-v3.1:free",
            "messages": messages
        }
    },
    "sonoma-sky": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        "payload": lambda messages: {
            "model": "openrouter/sonoma-sky-alpha",
            "messages": messages
        }
    },
    "sonoma-dusk": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        "payload": lambda messages: {
            "model": "openrouter/sonoma-dusk-alpha",
            "messages": messages
        }
    },
    "chimera": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        "payload": lambda messages: {
            "model": "tngtech/deepseek-r1t2-chimera:free",
            "messages": messages
        }
    },
    "qwen-coder": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        "payload": lambda messages: {
            "model": "qwen/qwen3-coder:free",
            "messages": messages
        }
    },
    "deepseek-r1": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        "payload": lambda messages: {
            "model": "deepseek/deepseek-r1-0528:free",
            "messages": messages
        }
    },
    "gpt-oss": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        "payload": lambda messages: {
            "model": "openai/gpt-oss-20b:free",
            "messages": messages
        }
    },
    "mai-ds": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        "payload": lambda messages: {
            "model": "microsoft/mai-ds-r1:free",
            "messages": messages
        }
    },
    "gemini": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        "payload": lambda messages: {
            "model": "google/gemini-2.0-flash-exp:free",
            "messages": messages
        }
    },
    "llama": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        "payload": lambda messages: {
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "messages": messages
        }
    },
    "kimi": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        },
        "payload": lambda messages: {
            "model": "moonshotai/kimi-k2:free",
            "messages": messages
        }
    }
}
