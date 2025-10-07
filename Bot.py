# filename: bot.py
# ساخته شده برای Koyeb (تلگرام + بله)
# شامل صف ارسال، پشتیبانی از متن، عکس و ویدیو

import os
import time
import threading
from queue import Queue
from telegram import Bot as TelegramBot, InputFile
from telegram.error import TelegramError
from bale import Bot as BaleBot

# -------------------- تنظیمات --------------------
TELEGRAM_TOKEN = "8201165297:AAHQaEiSqvZRB7lFB7HXDS3__i4-9TEj1V0"
BALE_TOKEN = "1455600908:By8cYMGG1o89t6z9NUI4eeIy3dw4L0pzKmg"
TELEGRAM_CHANNEL = "@Sattar360"
BALE_CHANNEL = "@sattar360"

# فاصله بین پست‌ها (دقیقه)
INTERVAL_MINUTES = 5  # می‌تونی عددش رو تغییر بدی

# -------------------------------------------------

telegram_bot = TelegramBot(token=TELEGRAM_TOKEN)
bale_bot = BaleBot(token=BALE_TOKEN)

post_queue = Queue()

def send_post_to_channels(post):
    """ارسال پست به هر دو کانال"""
    try:
        if post.get("type") == "text":
            telegram_bot.send_message(chat_id=TELEGRAM_CHANNEL, text=post["content"])
            bale_bot.send_message(chat_id=BALE_CHANNEL, text=post["content"])
        elif post.get("type") == "photo":
            telegram_bot.send_photo(chat_id=TELEGRAM_CHANNEL, photo=post["file"], caption=post.get("caption", ""))
            bale_bot.send_photo(chat_id=BALE_CHANNEL, photo=post["file"], caption=post.get("caption", ""))
        elif post.get("type") == "video":
            telegram_bot.send_video(chat_id=TELEGRAM_CHANNEL, video=post["file"], caption=post.get("caption", ""))
            bale_bot.send_video(chat_id=BALE_CHANNEL, video=post["file"], caption=post.get("caption", ""))
    except TelegramError as e:
        print("خطا در ارسال:", e)

def scheduler():
    """ارسال پست‌ها با فاصله زمانی تنظیم‌شده"""
    while True:
        if not post_queue.empty():
            post = post_queue.get()
            send_post_to_channels(post)
            print("✅ پست ارسال شد.")
        time.sleep(INTERVAL_MINUTES * 60)

def handle_incoming_post(link, caption=""):
    """شبیه‌سازی پردازش لینک پست و افزودن به صف"""
    # در آینده میشه اینجا لینک‌ها رو تحلیل کرد و فایل اصلی پست رو گرفت
    # فعلاً فقط متن لینک یا کپشن رو می‌فرسته
    post_queue.put({"type": "text", "content": f"{caption}\n\n📎 {link}"})
    print("🕓 پست به صف اضافه شد.")

# شروع ترد زمان‌بندی
threading.Thread(target=scheduler, daemon=True).start()

print("🤖 ربات فعال شد و آماده دریافت پست‌هاست...")

# حلقه ساده برای اضافه کردن پست‌ها (برای تست)
while True:
    link = input("لینک پست را وارد کن (یا exit برای خروج): ")
    if link.lower() == "exit":
        break
    caption = input("کپشن (اختیاری): ")
    handle_incoming_post(link, caption)
