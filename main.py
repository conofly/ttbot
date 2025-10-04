from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import requests
import os
import re
from keep_alive import keep_alive

BOT_TOKEN = os.environ["BOT_TOKEN"]

def extract_tiktok_url(text):
    match = re.search(r'(https?://(?:www\.)?(tiktok\.com|vt\.tiktok\.com|vm\.tiktok\.com)/[^\s]+)', text)
    return match.group(0) if match else None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    url = extract_tiktok_url(text)
    if not url:
        return

    await update.message.reply_text("⏳ Скачиваю видео...")

    try:
        # SnapTik API
        api_url = "https://snapx.vercel.app/api"
        params = {"url": url}
        response = requests.get(api_url, params=params, timeout=15).json()

        if not response.get("success"):
            raise Exception("Не удалось получить видео")

        video_url = response["data"]["video"]
        video_data = requests.get(video_url, timeout=15).content

        with open("video.mp4", "wb") as f:
            f.write(video_data)

        with open("video.mp4", "rb") as video:
            await update.message.reply_video(video, reply_to_message_id=update.message.id)

        os.remove("video.mp4")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен и слушает группы...")
    keep_alive()
    app.run_polling()

if __name__ == '__main__':
    main()
