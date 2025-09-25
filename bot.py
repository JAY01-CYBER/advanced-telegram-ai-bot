import os
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from utils import clean_text
from voice_utils import transcribe_audio

# 🔹 Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN is not set in Render environment variables!")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is not set in Render environment variables!")

# 🔹 Remove hidden spaces/newlines
TELEGRAM_TOKEN = TELEGRAM_TOKEN.strip()
OPENAI_API_KEY = OPENAI_API_KEY.strip()

openai.api_key = OPENAI_API_KEY

# 🔹 Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I’m your AI Bot. Send me a text or voice message.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    prompt = clean_text(user_text)
    try:
        resp = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=200
        )
        reply = resp.choices[0].text.strip()
    except Exception as e:
        reply = f"⚠️ Error: {e}"
    await update.message.reply_text(reply)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    if not voice:
        await update.message.reply_text("Cannot process voice.")
        return
    
    file = await context.bot.get_file(voice.file_id)
    file_path = await file.download_to_drive()

    text = await transcribe_audio(file_path)
    if not text:
        await update.message.reply_text("Could not transcribe voice.")
        return
    
    prompt = clean_text(text)
    try:
        resp = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=200
        )
        reply = resp.choices[0].text.strip()
    except Exception as e:
        reply = f"⚠️ Error: {e}"
    await update.message.reply_text(reply)

# 🔹 Main entry point
def main():
    print(f"✅ Starting bot with token (length={len(TELEGRAM_TOKEN)} chars)")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.run_polling()

if __name__ == "__main__":
    main()
