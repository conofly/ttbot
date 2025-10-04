import os, re, tempfile, requests, time
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ["BOT_TOKEN"]

# ловим все форматы TikTok-ссылок
TT_RE = re.compile(
    r'(https?://(?:www\.)?(?:tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com|m\.tiktok\.com|t\.tiktok\.com|lite\.tiktok\.com)/[^\s]+)',
    re.IGNORECASE
)

async def handle_message(update: Update, _: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or update.message.caption
    if not text:
        return
    m = TT_RE.search(text)
    if not m:
        return

    url = m.group(0)
    await update.message.reply_text("⏳ Скачиваю видео…")

    try:
        # 1. Получаем прямую ссылку через SnapTik-API
        api = "https://snaptik-api.herokuapp.com/download"
        r = requests.post(api, json={"url": url}, timeout=20)
        r.raise_for_status()
        data = r.json()

        if not data.get("success") or not data.get("video_url"):
            raise RuntimeError("Видео не найдено")

        video_url = data["video_url"]

        # 2. Качаем mp4
        vid_bytes = requests.get(video_url, timeout=30).content

        # 3. Отправляем
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(vid_bytes)
            tmp.flush()
            with open(tmp.name, "rb") as f:
                await update.message.reply_video(
                    video=f,
                    supports_streaming=True,
                    reply_to_message_id=update.message.message_id
                )
        os.unlink(tmp.name)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
