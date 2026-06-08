import telebot
import re
import requests
import os
import json
import yt_dlp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ============= الإعدادات =============
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ============= الأزرار الثابتة =============
def main_keyboard():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=False)
    markup.add(
        KeyboardButton("تيك توك"),
        KeyboardButton("انستغرام"),
        KeyboardButton("فيسبوك"),
        KeyboardButton("تويتر/X"),
        KeyboardButton("لايكي"),
        KeyboardButton("المساعدة"),
        KeyboardButton("عن البوت")
    )
    return markup

# ============= دالة التحميل الشاملة =============
def download_with_ytdlp(url, output_filename):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_filename,
        'no_warnings': True,
        'quiet': True,
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# ============= كشف نوع المنصة =============
def detect_platform(url):
    url_lower = url.lower()
    platforms = {
        'tiktok': ['tiktok.com', 'vm.tiktok.com'],
        'instagram': ['instagram.com', 'instagr.am'],
        'facebook': ['facebook.com', 'fb.com', 'fb.watch'],
        'twitter': ['twitter.com', 'x.com'],
        'likee': ['likee.com', 'like.video']
    }
    for platform, domains in platforms.items():
        for domain in domains:
            if domain in url_lower:
                return platform
    return None

# ============= معالجة التحميل حسب المنصة =============
def process_video(url, message, platform):
    bot.send_chat_action(message.chat.id, 'upload_video')
    
    platform_names = {
        'tiktok': 'تيك توك',
        'instagram': 'انستغرام',
        'facebook': 'فيسبوك',
        'twitter': 'تويتر/X',
        'likee': 'لايكي'
    }

    output_filename = f"video_{message.message_id}.mp4"
    
    try:
        actual_file = download_with_ytdlp(url, output_filename)
        
        if os.path.exists(actual_file):
            with open(actual_file, 'rb') as video_file:
                bot.send_video(
                    message.chat.id,
                    video_file,
                    caption=f"تم التحميل بنجاح\nمنصة: {platform_names.get(platform, platform)}\nبدون علامة مائية\nجودة عالية",
                    reply_to_message_id=message.message_id
                )
        else:
            bot.reply_to(message, f"فشل التحميل\nعذراً، لم نتمكن من معالجة الفيديو من {platform_names.get(platform, platform)}.\nيرجى المحاولة مرة أخرى أو استخدام رابط آخر.")
            
    except Exception as e:
        print(f"Error logs: {str(e)}")
        bot.reply_to(message, 
            f"فشل التحميل\n\n"
            f"المنصة: {platform_names.get(platform, platform)}\n\n"
            f"الأسباب المحتملة:\n"
            f"- الرابط غير صحيح أو منتهي الصلاحية\n"
            f"- الفيديو محذوف أو الحساب خاص\n"
            f"- الفيديو طويل جداً أو بحجم كبير\n\n"
            f"نصيحة: حاول استخدام رابط آخر أو تأكد من أن الفيديو منشور للجميع.")
            
    finally:
        if os.path.exists(output_filename):
            os.remove(output_filename)
        elif 'actual_file' in locals() and os.path.exists(actual_file):
            os.remove(actual_file)

# ============= أوامر البوت =============
@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = """
بوت تحميل الفيديوهات الشامل

مرحباً بك في البوت الأسرع لتحميل فيديوهات التواصل الاجتماعي

المنصات المدعومة:

- تيك توك
- انستغرام
- فيسبوك
- تويتر/X
- لايكي

كيفية الاستخدام:

1- اختر المنصة من الأزرار أدناه
2- أرسل رابط الفيديو
3- استلم الفيديو بجودة عالية وبدون علامة مائية

مجاني بالكامل - تحميل فوري - بدون علامات مائية
"""
    bot.reply_to(message, welcome_text, reply_markup=main_keyboard())

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
دليل الاستخدام السريع

الطريقة الأولى (الأزرار):
- اضغط على زر المنصة المطلوبة، ثم أرسل الرابط

الطريقة الثانية (مباشر):
- فقط ألصق رابط الفيديو وأرسله، وسيتعرف البوت تلقائياً على المنصة

أمثلة الروابط المدعومة:

تيك توك: https://www.tiktok.com/@user/video/123456789
انستغرام: https://www.instagram.com/p/CxYZ123/
فيسبوك: https://www.facebook.com/watch/?v=123456789
تويتر: https://x.com/user/status/123456789
لايكي: https://likee.com/video/123456789

ملاحظات مهمة:
- البوت لا يدعم الحسابات الخاصة
- الفيديو يجب أن يكون منشوراً للجميع
- جميع الفيديوهات بدون علامة مائية
"""
    bot.reply_to(message, help_text, reply_markup=main_keyboard())

@bot.message_handler(commands=['about'])
def about_command(message):
    about_text = """
معلومات عن البوت

الاسم: VidSaverNoLogoBot
الإصدار: 5.0
التقنية: yt-dlp + Python

المنصات المدعومة: 5 منصات

المميزات:
- تحميل بدون علامة مائية
- جودة عالية HD
- سرعة فائقة
- مجاني بالكامل

المطور: @invamsa
الخصوصية: لا نحتفظ بأي فيديوهات

للاقتراحات والتواصل: @invamsa
"""
    bot.reply_to(message, about_text, reply_markup=main_keyboard())

# ============= التعامل مع الأزرار =============
@bot.message_handler(func=lambda message: message.text in ["تيك توك", "انستغرام", "فيسبوك", "تويتر/X", "لايكي"])
def platform_selection(message):
    platform_map = {
        "تيك توك": "تيك توك",
        "انستغرام": "انستغرام",
        "فيسبوك": "فيسبوك",
        "تويتر/X": "تويتر",
        "لايكي": "لايكي"
    }
    platform = platform_map.get(message.text, "")
    examples = {
        "تيك توك": "https://www.tiktok.com/@user/video/123456789",
        "انستغرام": "https://www.instagram.com/p/CxYZ123/",
        "فيسبوك": "https://www.facebook.com/watch/?v=123456789",
        "تويتر": "https://x.com/user/status/123456789",
        "لايكي": "https://likee.com/video/123456789"
    }
    bot.reply_to(message, 
        f"تم اختيار {platform}\n\n"
        f"أرسل رابط الفيديو الآن:\n"
        f"مثال: {examples.get(platform, 'الرابط')}\n\n"
        f"سأقوم بتحميله لك فوراً بجودة عالية وبدون علامة مائية",
        reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "المساعدة")
def help_button(message):
    help_command(message)

@bot.message_handler(func=lambda message: message.text == "عن البوت")
def about_button(message):
    about_command(message)

# ============= معالجة الروابط =============
@bot.message_handler(func=lambda message: True)
def handle_links(message):
    text = message.text.strip()
    
    # تجاهل الأوامر والأزرار
    if text.startswith('/'):
        return
    
    buttons = ["تيك توك", "انستغرام", "فيسبوك", "تويتر/X", "لايكي", "المساعدة", "عن البوت"]
    if text in buttons:
        return
    
    platform = detect_platform(text)
    
    if not platform:
        bot.reply_to(
            message,
            "رابط غير مدعوم\n\n"
            "المنصات المدعومة حالياً:\n"
            "- تيك توك\n"
            "- انستغرام\n"
            "- فيسبوك\n"
            "- تويتر/X\n"
            "- لايكي\n\n"
            "نصيحة: استخدم الأزرار أدناه لاختيار المنصة أولاً ثم أرسل الرابط",
            reply_markup=main_keyboard()
        )
        return
    
    # رسالة انتظار
    waiting_msg = bot.reply_to(
        message,
        f"جاري تحميل الفيديو...\n\n"
        f"المنصة: {platform}\n"
        f"يرجى الانتظار لحظة\n"
        f"قد يستغرق التحميل بضع ثوانٍ حسب حجم الفيديو"
    )
    
    process_video(text, message, platform)
    
    try:
        bot.delete_message(message.chat.id, waiting_msg.message_id)
    except:
        pass

# ============= تشغيل البوت =============
if __name__ == "__main__":
    print("""
    بوت تحميل الفيديوهات V5.0
    5 منصات - تحميل بدون علامة مائية
    تيك توك - انستغرام - فيسبوك - تويتر - لايكي
    """)
    print(f"البوت: @{bot.get_me().username}")
    print("جاهز لاستقبال الروابط")
    print("المنصات المدعومة: تيك توك، انستغرام، فيسبوك، تويتر، لايكي\n")
    
    bot.infinity_polling(timeout=80)
