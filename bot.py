# bot.py (ИСПРАВЛЕННАЯ ВЕРСИЯ 4)
import logging
import os
import json
from collections import defaultdict

import httpx
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.constants import ParseMode, ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import BadRequest

# Кастомные импорты
from models import MODELS, DEFAULT_MODEL

# Загружаем переменные окружения из .env файла
load_dotenv()

# --- Настройки ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
YOUR_SITE_URL = "https://t.me/your_bot_username"
YOUR_SITE_NAME = "My Telegram AI Bot"
TELEGRAM_MAX_MESSAGE_LENGTH = 4096

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Хранилище данных пользователей в оперативной памяти
user_data = defaultdict(lambda: {"history": [], "context_enabled": True, "model": DEFAULT_MODEL})

# --- API Функция ---
async def call_openrouter_api(model: str, messages: list) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": YOUR_SITE_URL,
                    "X-Title": YOUR_SITE_NAME,
                },
                json={"model": model, "messages": messages},
                timeout=180, # Увеличено время ожидания для vision моделей
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            try:
                error_details = e.response.json().get("error", {}).get("message", e.response.text)
            except json.JSONDecodeError:
                error_details = e.response.text
            return {"error": f"Ошибка API: {e.response.status_code}. {error_details}"}
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return {"error": f"Произошла непредвиденная ошибка: {str(e)}"}

# --- НОВАЯ ФУНКЦИЯ для отправки длинных сообщений ---
async def send_long_message(update: Update, text: str, reply_markup=None):
    """Отправляет длинное сообщение, разбивая его на части, если необходимо."""
    if len(text) <= TELEGRAM_MAX_MESSAGE_LENGTH:
        await update.message.reply_text(text, reply_markup=reply_markup)
        return

    parts = []
    while len(text) > 0:
        if len(text) > TELEGRAM_MAX_MESSAGE_LENGTH:
            part = text[:TELEGRAM_MAX_MESSAGE_LENGTH]
            last_newline = part.rfind('\n')
            if last_newline != -1:
                parts.append(part[:last_newline])
                text = text[last_newline + 1:]
            else:
                parts.append(part)
                text = text[TELEGRAM_MAX_MESSAGE_LENGTH:]
        else:
            parts.append(text)
            break
            
    for i, part in enumerate(parts):
        # Отправляем клавиатуру только с последней частью
        current_reply_markup = reply_markup if i == len(parts) - 1 else None
        await update.message.reply_text(part, reply_markup=current_reply_markup)

# --- Функции Клавиатур ---
def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    context_status = "Контекст: ✅ ВКЛ" if user_data[user_id]["context_enabled"] else "Контекст: ❌ ВЫКЛ"
    keyboard = [["/models", "/reset"], [context_status]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_models_keyboard() -> InlineKeyboardMarkup:
    keyboard = []
    for model_id, details in MODELS.items():
        button_text = f"📸 {details['name']}" if details['vision'] else details['name']
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"model:{model_id}")])
    return InlineKeyboardMarkup(keyboard)
    
# --- Обработчики Команд ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user, user_id = update.effective_user, update.effective_user.id
    user_data[user_id] = {"history": [], "context_enabled": True, "model": DEFAULT_MODEL}
    logger.info(f"User {user.username} (ID: {user_id}) started the bot.")
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Я AI-ассистент. Отправьте мне текст или "
        "изображение с подписью, чтобы начать.\n\n"
        "📸 - модели, работающие с изображениями.",
        reply_markup=get_main_keyboard(user_id)
    )
    await models_command(update, context)

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]["history"] = []
    logger.info(f"History reset for user ID: {user_id}")
    await update.message.reply_text("История чата сброшена.", reply_markup=get_main_keyboard(user_id))

async def models_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    current_model_id = user_data[user_id].get('model', DEFAULT_MODEL)
    current_model_name = MODELS.get(current_model_id, {}).get('name', 'Неизвестная')
    await update.message.reply_text(
        f"Текущая модель: `{current_model_name}`\n\nВыберите новую модель:",
        reply_markup=get_models_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )

async def toggle_context_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_data[user_id]["context_enabled"] = not user_data[user_id]["context_enabled"]
    state = "включен" if user_data[user_id]["context_enabled"] else "выключен"
    logger.info(f"Context toggled to {state} for user ID: {user_id}")
    await update.message.reply_text(f"Режим контекста {state}.", reply_markup=get_main_keyboard(user_id))

# --- Обработчики Сообщений ---
async def model_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    model_id = query.data.split(":", 1)[1]
    
    user_data[user_id]["model"] = model_id
    model_name = MODELS.get(model_id, {}).get('name', "Неизвестная")
    
    logger.info(f"User ID {user_id} switched model to: {model_id}")
    await query.edit_message_text(text=f"✅ Модель установлена: `{model_name}`", parse_mode=ParseMode.MARKDOWN)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    if user_input == "/reset": return await reset_command(update, context)
    if user_input == "/models": return await models_command(update, context)
    if user_input.startswith("Контекст:"): return await toggle_context_command(update, context)
    await process_request(update, context, user_input)

async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    current_model_id = user_data[user_id]['model']

    if not MODELS[current_model_id]['vision']:
        await update.message.reply_text(
            f"Текущая модель `{MODELS[current_model_id]['name']}` не умеет работать с изображениями. "
            "Пожалуйста, выберите 'зрячую' модель (с 📸) через команду /models."
        )
        return

    photo_file = await update.message.photo[-1].get_file()
    image_url = photo_file.file_path
    
    text_prompt = update.message.caption or "Что на этом изображении?"

    vision_payload = [{"type": "text", "text": text_prompt}, {"type": "image_url", "image_url": {"url": image_url}}]
    await process_request(update, context, text_prompt, vision_payload)

async def process_request(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str, vision_payload: list = None) -> None:
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)

    messages_for_api = []
    if user_data[user_id]["context_enabled"]:
        messages_for_api.extend(user_data[user_id]["history"])

    # Готовим сообщение для API
    user_message_content = vision_payload if vision_payload else user_input
    messages_for_api.append({"role": "user", "content": user_message_content})
    
    api_response = await call_openrouter_api(user_data[user_id]["model"], messages_for_api)

    if "error" in api_response:
        bot_response_text = api_response["error"]
    else:
        bot_response_text = api_response.get('choices', [{}])[0].get('message', {}).get('content', 'Не удалось получить ответ от модели.')

    # Сохраняем в историю
    if user_data[user_id]["context_enabled"] and "error" not in api_response:
        # --- БОНУС-ФИКС: Правильно сохраняем контекст для vision ---
        # Раньше сохранялся только текст "что на картинке", а не сама картинка,
        # из-за чего бот "забывал" о ней при следующем вопросе.
        user_data[user_id]["history"].append({"role": "user", "content": user_message_content})
        user_data[user_id]["history"].append({"role": "assistant", "content": bot_response_text})

    # --- ИЗМЕНЕНИЕ: Используем новую функцию для отправки ---
    await send_long_message(update, bot_response_text, reply_markup=get_main_keyboard(user_id))
    
# --- Основная Функция ---
def main() -> None:
    if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
        logger.error("Критическая ошибка: TELEGRAM_TOKEN или OPENROUTER_API_KEY не найдены в .env файле!")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("models", models_command))
    application.add_handler(CallbackQueryHandler(model_button_callback, pattern="^model:"))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))

    logger.info("Бот запускается...")
    application.run_polling()

if __name__ == "__main__":
    main()
