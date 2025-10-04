from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import yt_dlp
import os
import re
from keep_alive import keep_alive

BOT_TOKEN = os.environ["8256203198:AAEVleNpTrpclJNz1QA7KI_yGMLflSLevtE"]

def extract_tiktok_url(text):
    match = re.search(r'(https?://(?:www\.)?vt.tiktok\.com/[^\s]+)', text)
    return match.group(0) if match else None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    url = extract_tiktok_url(text)
    if not url:
        return

    await update.message.reply_text("⏳ Скачиваю видео...")

    ydl_opts = {
        'outtmpl': 'video.mp4',
        'format': 'best'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open('video.mp4', 'rb') as video:
            await update.message.reply_video(video, reply_to_message_id=update.message.id)

        os.remove('video.mp4')
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
