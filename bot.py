import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from transformers import pipeline

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Gunakan model AI gratis dari Hugging Face
chatbot = pipeline("text-generation", model="gpt2")

# Handler untuk command /start
async def start(update: Update, context):
    await update.message.reply_text('Halo! Saya adalah chatbot AI. Silakan kirim pesan apa pun.')

# Handler untuk pesan teks
async def chat(update: Update, context):
    user_message = update.message.text
    logging.info(f"User: {user_message}")

    # Generate respons menggunakan model AI
    response = chatbot(user_message, max_length=50, num_return_sequences=1)[0]['generated_text']
    logging.info(f"Bot: {response}")

    await update.message.reply_text(response)

if __name__ == '__main__':
    # Ambil token bot Telegram dari environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("Token bot Telegram tidak ditemukan. Pastikan Anda telah mengatur environment variable TELEGRAM_BOT_TOKEN.")

    # Bangun aplikasi
    application = ApplicationBuilder().token(token).build()

    # Tambahkan handler
    start_handler = CommandHandler('start', start)
    chat_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, chat)

    application.add_handler(start_handler)
    application.add_handler(chat_handler)

    # Jalankan bot
    application.run_polling()