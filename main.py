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
       await update.message.reply_text("⏳ Скачиваю видео...")

    proxy = os.environ.get("PROXY")          # берём из Replit-Secrets
    proxies = {"http": proxy, "https": proxy} if proxy else None

    try:
        # 1. получаем прямую ссылку на видео
        api_url = "https://api.tikwm.com/video/"
        params = {"url": url}
        print(proxies)
        resp = requests.get(api_url, params=params, timeout=10,
                            proxies=proxies, allow_redirects=True)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != 0:
            raise RuntimeError("API вернуло ошибку")

        video_url = data["data"]["play"]

        # 2. скачиваем сам файл
        video_bytes = requests.get(video_url, timeout=15,
                                   proxies=proxies, allow_redirects=True).content
        with open("video.mp4", "wb") as f:
            f.write(video_bytes)

        # 3. отправляем пользователю
        with open("video.mp4", "rb") as v:
            await update.message.reply_video(v, reply_to_message_id=update.message.id)

        os.remove("video.mp4")

    except requests.exceptions.ProxyError:
        await update.message.reply_text("⚠️ Прокси недоступен")
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
