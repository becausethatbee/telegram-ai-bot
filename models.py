# models.py
# Структура: "id_модели": {"name": "Имя для кнопки", "vision": True/False}
# ID моделей взяты точно из вашего списка.

MODELS = {
    # --- Vision (зрячие) модели ---
    "openrouter/sonoma-dusk-alpha": {
        "name": "Sonoma Dusk Alpha",
        "vision": True,
    },
    "google/gemini-2.0-flash-exp:free": {
        "name": "Gemini 2.0 Flash Exp (Free)",
        "vision": True,
    },
    "qwen/qwen2.5-vl-72b-instruct:free": {
        "name": "Qwen 2.5 VL 72B (Free)",
        "vision": True,
    },
    "google/gemma-3-27b-it:free": {
        "name": "Gemma 3 27B IT (Free)",
        "vision": True,
    },

    # --- Текстовые модели ---
    "deepseek/deepseek-chat-v3.1:free": {
        "name": "Deepseek Chat v3.1 (Free)",
        "vision": False,
    },
    "tngtech/deepseek-r1t2-chimera:free": {
        "name": "Deepseek R1T2 Chimera (Free)",
        "vision": False,
    },
    "qwen/qwen3-coder:free": {
        "name": "Qwen 3 Coder (Free)",
        "vision": False,
    },
    "z-ai/glm-4.5-air:free": {
        "name": "GLM 4.5 Air (Free)",
        "vision": False,
    },
    "moonshotai/kimi-k2:free": {
        "name": "Kimi K2 (Free)",
        "vision": False,
    },
    "nvidia/nemotron-nano-9b-v2:free": {
        "name": "Nemotron Nano 9B v2 (Free)",
        "vision": False,
    },
}

# Модель по умолчанию при старте бота.
# Выбрана из вашего списка бесплатных vision-моделей.
DEFAULT_MODEL = "google/gemini-2.0-flash-exp:free"
