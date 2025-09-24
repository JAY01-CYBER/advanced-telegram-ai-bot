import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import openai
from utils import save_message, get_last_messages
from voice_utils import speech_to_text

# Load environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Help", callback_data='help')],
        [InlineKeyboardButton("About", callback_data='about')],
        [InlineKeyboardButton("Generate Image", callback_data='image')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Hello! I am your advanced AI assistant. Type or send a voice message. Use buttons for commands.", 
        reply_markup=reply_markup
    )

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'help':
        query.edit_message_text("You can type messages, send voice, or generate images with /image command.")
    elif query.data == 'about':
        query.edit_message_text("Advanced AI Telegram Bot with GPT, DALL·E, and voice features.")
    elif query.data == 'image':
        query.edit_message_text("Send a message describing the image you want to generate.")

def chat(update: Update, context: CallbackContext):
    user_msg = update.message.text
    save_message(update.message.chat_id, "user", user_msg)
    
    history = get_last_messages(update.message.chat_id)
    prompt = "\n".join([f"{h['role']}: {h['text']}" for h in history])

    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=200
        )
        reply = response.choices[0].text.strip()
    except Exception:
        reply = "Oops! Something went wrong."
    
    save_message(update.message.chat_id, "bot", reply)
    update.message.reply_text(reply)

def generate_image(update: Update, context: CallbackContext):
    user_msg = " ".join(context.args)
    if not user_msg:
        update.message.reply_text("Usage: /image Describe your image here")
        return
    try:
        response = openai.Image.create(
            prompt=user_msg,
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']
        update.message.reply_photo(photo=image_url)
    except Exception:
        update.message.reply_text("Failed to generate image.")

def voice_handler(update: Update, context: CallbackContext):
    file = context.bot.get_file(update.message.voice.file_id)
    file.download("voice.ogg")
    text = speech_to_text("voice.ogg")
    update.message.reply_text(f"You said: {text}")
    update.message.text = text
    chat(update, context)

def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("image", generate_image))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, chat))
    dp.add_handler(MessageHandler(Filters.voice, voice_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
