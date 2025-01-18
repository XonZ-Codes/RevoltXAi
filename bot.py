import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Fungsi untuk menghasilkan respons menggunakan Hugging Face API
def generate_response(prompt):
    api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"  # Ganti dengan model lain jika perlu
    headers = {"Authorization": f"Bearer {os.getenv('HUGGING_FACE_API_KEY')}"}
    payload = {"inputs": prompt}
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception jika status code bukan 200
        response_data = response.json()
        
        # Cek apakah respons valid
        if isinstance(response_data, list) and len(response_data) > 0:
            return response_data[0]['generated_text']
        else:
            raise Exception("Respons dari API tidak valid.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error saat memanggil Hugging Face API: {e}")
        raise Exception("Terjadi kesalahan saat memproses pesan Anda. Silakan coba lagi nanti.")

# Handler untuk command /start
async def start(update: Update, context):
    await update.message.reply_text('Halo! Saya adalah Revolt AI. Silakan kirim pesan apa pun.')

# Handler untuk pesan teks
async def chat(update: Update, context):
    user_message = update.message.text
    logging.info(f"User: {user_message}")

    try:
        # Berikan konteks yang jelas ke model
        prompt = f"Anda adalah asisten AI yang ramah dan membantu. Jawablah pertanyaan berikut dengan singkat dan jelas: {user_message}"
        
        # Generate respons menggunakan Hugging Face API
        response = generate_response(prompt)
        logging.info(f"Bot: {response}")
        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(f"Maaf, terjadi kesalahan: {str(e)}")

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
    logging.info("Starting bot...")
    application.run_polling()
