import os
import glob
import asyncio
import requests
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("8807648828:AAGkCE1y8fWap110yBiWSmf6pWnzz3IhNQI", "8807648828:AAGkCE1y8fWap110yBiWSmf6pWnzz3IhNQI")

FAST_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "concurrent_fragment_downloads": 16,
    "retries": 10,
    "fragment_retries": 10,
    "socket_timeout": 20,
}

async def smooth_loader(msg, texts, delay=0.35):
    for text in texts:
        await asyncio.sleep(delay)
        await msg.edit_text(text)

def file_size_mb(path):
    return round(os.path.getsize(path) / (1024 * 1024), 2)

def format_speed(speed):
    if not speed:
        return "0 KB/s"
    if speed >= 1024 * 1024:
        return f"{speed / (1024 * 1024):.2f} MB/s"
    return f"{speed / 1024:.2f} KB/s"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "╔══════════════════════════════╗\n"
        "║ 💜✨ ADMIN RAHMAN BOT ✨💜 ║\n"
        "╠══════════════════════════════╣\n"
        "║ 🌌 VIDEO + PHOTO DOWNLOADER  ║\n"
        "║ 🎬 YouTube • TikTok          ║\n"
        "║ 📸 TikTok Photos Supported   ║\n"
        "║ 🎧 MP3 • HD Video            ║\n"
        "╚══════════════════════════════╝\n\n"
        "💜 Send your video/photo link 👇"
    )

async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not ("youtube.com" in url or "youtu.be" in url or "tiktok.com" in url):
        await update.message.reply_text("❌ Valid YouTube/TikTok link পাঠাও")
        return

    context.user_data["url"] = url

    msg = await update.message.reply_text("💜 Initializing...")

    await smooth_loader(msg, [
        "╭━━━〔 💜 SCANNING 〕━━━╮\n┃ 🔍 Detecting link...\n┃ ▱▱▱▱▱ 0%\n╰━━━━━━━━━━━━━━━━━━━━╯",
        "╭━━━〔 💜 SCANNING 〕━━━╮\n┃ 🔍 Processing...\n┃ ▰▱▱▱▱ 20%\n╰━━━━━━━━━━━━━━━━━━━━╯",
        "╭━━━〔 💜 SCANNING 〕━━━╮\n┃ 🔍 Fetching info...\n┃ ▰▰▰▱▱ 60%\n╰━━━━━━━━━━━━━━━━━━━━╯",
        "╭━━━〔 ✅ DONE 〕━━━╮\n┃ 💜 Link detected successfully\n┃ ▰▰▰▰▰ 100%\n╰━━━━━━━━━━━━━━━━━━━━╯",
    ])

    try:
        with yt_dlp.YoutubeDL(FAST_OPTS) as ydl:
            data = ydl.extract_info(url, download=False)

        title = data.get("title", "Unknown")
        duration = data.get("duration", 0)
        thumbnail = data.get("thumbnail")

        context.user_data["title"] = title

        m = duration // 60
        s = duration % 60

        buttons = [
            [
                InlineKeyboardButton("💜 1080p", callback_data="1080"),
                InlineKeyboardButton("⚡ 720p", callback_data="720")
            ],
            [
                InlineKeyboardButton("🔮 360p", callback_data="360"),
                InlineKeyboardButton("🎧 MP3", callback_data="mp3")
            ]
        ]

        if "tiktok.com" in url:
            buttons.append([InlineKeyboardButton("📸 Photo/Slideshow", callback_data="photo")])

        caption = (
            "╭━━━━〔 💜 NEON PREVIEW 💜 〕━━━━╮\n"
            f"🎬 {title[:45]}\n"
            f"⏱ Duration: {m}:{s:02d}\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
            "⚡ Choose format 👇"
        )

        await msg.delete()

        if thumbnail:
            await update.message.reply_photo(
                photo=thumbnail,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await update.message.reply_text(
                caption,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    except Exception:
        if "tiktok.com" in url:
            buttons = [
                [InlineKeyboardButton("📸 Download Photos", callback_data="photo")]
            ]

            await msg.edit_text(
                "╭━━━〔 📸 TIKTOK PHOTO 〕━━━╮\n"
                "┃ Photo post detected\n"
                "┃ Click below to download\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await msg.edit_text("❌ Preview failed")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    url = context.user_data.get("url")
    title = context.user_data.get("title", "Your file")
    choice = q.data

    if choice == "photo":
        msg = await q.message.reply_text("📸 Fetching photos...")

        try:
            api = "https://www.tikwm.com/api/?url=" + url
            data = requests.get(api, timeout=20).json()
            images = data.get("data", {}).get("images", [])

            if not images:
                await msg.edit_text("❌ Photo পাওয়া যায়নি")
                return

            for img in images[:20]:
                await q.message.reply_photo(photo=img)

            await msg.edit_text(
                "╭━━━〔 ✅ PHOTOS DONE 〕━━━╮\n"
                f"┃ 📸 Total: {len(images)} photos\n"
                "┃ 💜 ADMIN RAHMAN BOT\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯"
            )
            return

        except Exception as e:
            await msg.edit_text("❌ Photo download failed\n\n" + str(e)[:150])
            return

    quality_name = {
        "1080": "1080p HD",
        "720": "720p HD",
        "360": "360p Lite",
        "mp3": "MP3 Audio"
    }.get(choice, "Video")

    msg = await q.message.reply_text("🚀 Starting download...")

    try:
        os.makedirs("downloads", exist_ok=True)

        for old in glob.glob("downloads/*"):
            try:
                os.remove(old)
            except:
                pass

        base_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "noplaylist": True,
            **FAST_OPTS
        }

        if choice == "mp3":
            ydl_opts = {
                **base_opts,
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                }],
            }
        elif choice == "1080":
            ydl_opts = {**base_opts, "format": "bestvideo[height<=1080]+bestaudio/best"}
        elif choice == "720":
            ydl_opts = {**base_opts, "format": "bestvideo[height<=720]+bestaudio/best"}
        else:
            ydl_opts = {**base_opts, "format": "bestvideo[height<=360]+bestaudio/best"}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(data)

        await msg.edit_text("📤 Sending...")

        if choice == "mp3":
            file = file.replace(".webm", ".mp3").replace(".m4a", ".mp3")
            size = file_size_mb(file)

            with open(file, "rb") as f:
                await q.message.reply_audio(
                    audio=f,
                    caption=(
                        "╭━━━〔 🎧 AUDIO READY 〕━━━╮\n"
                        f"┃ 🎵 Title: {title[:25]}\n"
                        f"┃ 💾 Size: {size} MB\n"
                        "┃ 💜 ADMIN RAHMAN BOT\n"
                        "╰━━━━━━━━━━━━━━━━━━━━╯"
                    )
                )
        else:
            size = file_size_mb(file)

            with open(file, "rb") as f:
                await q.message.reply_video(
                    video=f,
                    caption=(
                        "╭━━━〔 ✅ DONE 〕━━━╮\n"
                        f"┃ 🎬 Title: {title[:25]}\n"
                        f"┃ 📺 Quality: {quality_name}\n"
                        f"┃ 💾 Size: {size} MB\n"
                        "┃ 💜 ADMIN RAHMAN BOT\n"
                        "╰━━━━━━━━━━━━━━━━━━━━╯"
                    )
                )

        for fpath in glob.glob("downloads/*"):
            try:
                os.remove(fpath)
            except:
                pass

        await msg.delete()

    except Exception as e:
        await msg.edit_text("❌ Download failed\n\n" + str(e)[:200])

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, link_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("💜 Photo Video Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
