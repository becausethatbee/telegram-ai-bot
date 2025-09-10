import os
import requests
import telebot
from dotenv import load_dotenv
from telebot import types
from models import MODELS

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Настройки по умолчанию
user_settings = {}  # chat_id -> {"model": ..., "context": ..., "history": [...]}
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_CONTEXT = 0

def get_settings(chat_id):
    if chat_id not in user_settings:
        user_settings[chat_id] = {
            "model": DEFAULT_MODEL,
            "context": DEFAULT_CONTEXT,
            "history": []
        }
    return user_settings[chat_id]

def ask_model(chat_id, user_input: str) -> str:
    settings = get_settings(chat_id)
    model = settings["model"]

    if model not in MODELS:
        return f"Модель {model} не найдена."

    # Добавляем сообщение пользователя в историю
    settings["history"].append({"role": "user", "content": user_input})

    # Обрезаем историю по контексту
    ctx_size = settings["context"]
    if ctx_size > 0:
        messages = settings["history"][-ctx_size:]
    else:
        messages = [{"role": "user", "content": user_input}]

    model_cfg = MODELS[model]
    headers = model_cfg["headers"](OPENROUTER_KEY)
    payload = model_cfg["payload"](messages)

    try:
        resp = requests.post(model_cfg["url"], headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        reply = data["choices"][0]["message"]["content"]

        # Сохраняем ответ ассистента в историю
        settings["history"].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"Ошибка при запросе к модели: {e}"

# === Команды ===
@bot.message_handler(commands=["start"])
def start_message(message):
    bot.reply_to(message, "Привет! Я AI-бот.\nИспользуй кнопки /model и /context для настроек.")

# === Модели через кнопки ===
@bot.message_handler(commands=["model"])
def choose_model(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    for model_name in MODELS.keys():
        btn = types.InlineKeyboardButton(model_name, callback_data=f"model:{model_name}")
        markup.add(btn)
    bot.send_message(chat_id, "Выбери модель:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("model:"))
def callback_model(call):
    chat_id = call.message.chat.id
    model = call.data.split(":")[1]
    get_settings(chat_id)["model"] = model
    bot.answer_callback_query(call.id, f"Модель переключена на {model}")
    bot.send_message(chat_id, f"Теперь активна модель: {model}")

# === Контекст через кнопки ===
@bot.message_handler(commands=["context"])
def choose_context(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    for ctx in [0, 5, 10, 21]:
        btn = types.InlineKeyboardButton(str(ctx), callback_data=f"context:{ctx}")
        markup.add(btn)
    bot.send_message(chat_id, "Выбери контекст сообщений:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("context:"))
def callback_context(call):
    chat_id = call.message.chat.id
    ctx = int(call.data.split(":")[1])
    get_settings(chat_id)["context"] = ctx
    bot.answer_callback_query(call.id, f"Контекст установлен: {ctx}")
    bot.send_message(chat_id, f"Теперь бот учитывает последние {ctx} сообщений")

# === Основной обработчик текста ===
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_input = message.text
    reply = ask_model(chat_id, user_input)
    bot.reply_to(message, reply)

print("Бот запущен... Ctrl+C для остановки")
bot.infinity_polling()
