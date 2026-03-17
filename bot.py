import logging
import anthropic
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TOKEN", "")
CLAUDE_KEY = os.environ.get("CLAUDE_KEY", "")

KNOWLEDGE = """
EMET Ukraine — дистриб'ютор ін'єкційних препаратів для естетичної медицини.
Продукти: Neuramis, Ellanse, Exoxe, Esse, Neuronox, Magnox, Vitaran, Petaran, iUse.
"""

MENU = ReplyKeyboardMarkup([
    [KeyboardButton("🎯 Sales Coach"), KeyboardButton("📚 Навчання")],
    [KeyboardButton("🥊 Coaching"), KeyboardButton("👥 HR")],
    [KeyboardButton("⚙️ Операційні"), KeyboardButton("🆕 Онбординг")],
    [KeyboardButton("🔙 Головне меню")]
], resize_keyboard=True)

MODES = {
    "🎯 Sales Coach": "Ти Sales Coach. Допомагай зі скриптами продажів, аргументами і роботою з запереченнями лікарів.",
    "📚 Навчання": "Ти викладач. Навчай менеджера по продуктах EMET. Давай чіткі пояснення і факти.",
    "🥊 Coaching": "Ти коуч. Розбирай кейси менеджерів, тренуй відпрацювання заперечень.",
    "👥 HR": "Ти HR-асистент. Відповідай на питання про регламенти, відпустки, правила компанії.",
    "⚙️ Операційні": "Ти операційний асистент. Відповідай про семінари, акції, прайси.",
    "🆕 Онбординг": "Ти наставник. Допомагай новим менеджерам освоїтись в компанії EMET.",
}

user_modes = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_modes[update.effective_user.id] = None
    await update.message.reply_text(
        "👋 Привіт! Я EMET Assistant.\n\nОбери режим роботи:",
        reply_markup=MENU
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if text == "🔙 Головне меню":
        user_modes[user_id] = None
        await update.message.reply_text("Обери режим:", reply_markup=MENU)
        return

    if text in MODES:
        user_modes[user_id] = text
        await update.message.reply_text(
            f"Режим {text} активовано!\n\nЗадай своє питання 👇",
            reply_markup=MENU
        )
        return

    mode = user_modes.get(user_id)
    if not mode:
        await update.message.reply_text("Спочатку обери режим 👆", reply_markup=MENU)
        return

    await update.message.reply_text("⏳ Думаю...")
    try:
        client = anthropic.AsyncAnthropic(api_key=CLAUDE_KEY)
        system = f"{MODES[mode]}\n\nБАЗА ЗНАНЬ:\n{KNOWLEDGE}"
        message = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": text}]
        )
        await update.message.reply_text(message.content[0].text, reply_markup=MENU)
    except Exception as e:
        await update.message.reply_text(f"Помилка: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ EMET AI Бот запущено!")
    app.run_polling()
