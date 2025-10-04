import os, re, requests, tempfile
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
BOT_TOKEN   = os.environ["BOT_TOKEN"]
RAPID_KEY   = os.environ["RAPID_KEY"]
регулярка ловит все известные форматы
TIKTOK_RE = re.compile(
r'(https?://(?:www.)?(?:tiktok.com|vm.tiktok.com|vt.tiktok.com|m.tiktok.com|t.tiktok.com|lite.tiktok.com)/[^\s?]+)',
re.IGNORECASE
)
async def handle_message(update: Update, _: ContextTypes.DEFAULT_TYPE):
text = update.message.text or update.message.caption
if not text:
return
Copy
match = TIKTOK_RE.search(text)
if not match:
    return

url = match.group(1)
await update.message.chat.send_action("upload_video")
await update.message.reply_text("⏳ Скачиваю видео…")

try:
    # 1. Получаем прямую ссылку через rapidapi
    resp = requests.get(
        "https://tiktok-info.p.rapidapi.com/dl/",
        headers={
            "X-RapidAPI-Key": RAPID_KEY,
            "X-RapidAPI-Host": "tiktok-info.p.rapidapi.com"
        },
        params={"url": url},
        timeout=20
    )
    resp.raise_for_status()
    data = resp.json()

    if not data.get("video_data", {}).get("nwm_video_url"):
        raise RuntimeError("Видео не найдено")

    video_url = data["video_data"]["nwm_video_url"]

    # 2. Скачиваем видео
    video_bytes = requests.get(video_url, timeout=30).content

    # 3. Отправляем
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(video_bytes)
        tmp.flush()
        with open(tmp.name, "rb") as f:
            await update.message.reply_video(
                video=f,
                supports_streaming=True,
                reply_to_message_id=update.message.message_id
            )
    os.unlink(tmp.name)

except Exception as e:
    await update.message.reply_text(f"⚠️ Не удалось скачать: {e}")
def main():
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling(drop_pending_updates=True)
if name == "main": main()
