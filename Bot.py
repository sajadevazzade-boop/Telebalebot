# filename: bot.py
# ربات هماهنگ بین تلگرام و بله، قابل اجرا در Koyeb با موبایل
import os
import time
import threading
from queue import Queue
import requests
from telegram import Bot as TelegramBot, InputFile
from telegram.error import TelegramError

# -------------------- تنظیمات --------------------
TELEGRAM_TOKEN = "8201165297:AAHQaEiSqvZRB7lFB7HXDS3__i4-9TEj1V0"
BALE_TOKEN = "1455600908:By8cYMGG1o89t6z9NUI4eeIy3dw4L0pzKmg"
TELEGRAM_CHANNEL = "@Sattar360"
BALE_CHANNEL = "@sattar360"

# فاصله بین پست‌ها (دقیقه)
INTERVAL_MINUTES = 5

# -------------------------------------------------
telegram_bot = TelegramBot(token=TELEGRAM_TOKEN)
post_queue = Queue()

def send_to_bale(content, type_="text", file=None, caption=None):
    """ارسال پیام به بله با استفاده از API رسمی"""
    base_url = f"https://tapi.bale.ai/bot{BALE_TOKEN}"
    try:
        if type_ == "text":
            requests.post(f"{base_url}/sendMessage", json={
                "chat_id": BALE_CHANNEL,
                "text": content
            })
        elif type_ == "photo":
            files = {'photo': open(file, 'rb')}
            data = {"chat_id": BALE_CHANNEL, "caption": caption or ""}
            requests.post(f"{base_url}/sendPhoto", data=data, files=files)
        elif type_ == "video":
            files = {'video': open(file, 'rb')}
            data = {"chat_id": BALE_CHANNEL, "caption": caption or ""}
            requests.post(f"{base_url}/sendVideo", data=data, files=files)
    except Exception as e:
        print("❌ خطا در ارسال بله:", e)

def send_post_to_channels(post):
    """ارسال پست به هر دو کانال"""
    try:
        if post.get("type") == "text":
            telegram_bot.send_message(chat_id=TELEGRAM_CHANNEL, text=post["content"])
            send_to_bale(post["content"], "text")
        elif post.get("type") == "photo":
            telegram_bot.send_photo(chat_id=TELEGRAM_CHANNEL, photo=post["file"], caption=post.get("caption", ""))
            send_to_bale(None, "photo", file=post["file"], caption=post.get("caption", ""))
        elif post.get("type") == "video":
            telegram_bot.send_video(chat_id=TELEGRAM_CHANNEL, video=post["file"], caption=post.get("caption", ""))
            send_to_bale(None, "video", file=post["file"], caption=post.get("caption", ""))
        print("✅ پست ارسال شد.")
    except TelegramError as e:
        print("❌ خطا در ارسال تلگرام:", e)

def scheduler():
    """ارسال پست‌ها با فاصله زمانی مشخص"""
    while True:
        if not post_queue.empty():
            post = post_queue.get()
            send_post_to_channels(post)
        time.sleep(INTERVAL_MINUTES * 60)

def handle_incoming_post(link, caption=""):
    """افزودن لینک به صف ارسال"""
    post_queue.put({"type": "text", "content": f"{caption}\n\n📎 {link}"})
    print("🕓 پست به صف اضافه شد.")

threading.Thread(target=scheduler, daemon=True).start()
print("🤖 ربات فعال شد...")

while True:
    link = input("🔗 لینک پست: ")
    if link.lower() == "exit":
        break
    caption = input("📝 کپشن (اختیاری): ")
    handle_incoming_post(link, caption)
