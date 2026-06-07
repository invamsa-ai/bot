import telebot
import re
import requests
import os
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ============= الإعدادات =============
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ============= API مجانية لتحميل الفيديوهات =============
# خدمة 1: tikmate (لتيك توك)
def download_tiktok(url):
    """تحميل فيديو من تيك توك بدون علامة مائية"""
    try:
        # استخدام API مجاني
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url)
        data = response.json()
        
        if data.get('code') == 0:
            video_url = data['data']['play']
            return video_url
        return None
    except:
        return None

# خدمة 2: snapinsta (لانستغرام)
def download_instagram(url):
    """تحميل فيديو من انستغرام"""
    try:
        # تنظيف الرابط
        if '?' in url:
            url = url.split('?')[0]
        
        # استخدام API مجاني
        api_url = f"https://snapinsta.app/api/ajaxSearch"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'q': url}
        
        response = requests.post(api_url, headers=headers, data=data)
        result = response.json()
        
        if result.get('success') and result.get('medias'):
            for media in result['medias']:
                if media.get('type') == 'video':
                    return media['url']
        return None
    except:
        return None

# خدمة بديلة (tiksave)
def download_tiktok_alternative(url):
    """خدمة بديلة لتيك توك"""
    try:
        api_url = f"https://tiksave.io/api/ajaxSearch"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'q': url}
        
        response = requests.post(api_url, headers=headers, data=data)
        result = response.json()
        
        if result.get('success') and result.get('links'):
            return result['links']['video']
        return None
    except:
        return None

# خدمة بديلة لانستغرام
def download_instagram_alternative(url):
    """خدمة بديلة لانستغرام"""
    try:
        api_url = f"https://instasave.io/api/ajaxSearch"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'q': url}
        
        response = requests.post(api_url, headers=headers, data=data)
        result = response.json()
        
        if result.get('success') and result.get('links'):
            return result['links']['video']
        return None
    except:
        return None

# ============= كشف نوع الرابط =============
def detect_platform(url):
    """تحديد المنصة من الرابط"""
    url = url.lower()
    
    if 'tiktok.com' in url:
        return 'tiktok'
    elif 'instagram.com' in url or 'instagr.am' in url:
        return 'instagram'
    else:
        return None

# ============= معالجة الروابط =============
def process_video(url, message, platform):
    """معالجة الفيديو وإرساله للمستخدم"""
    bot.send_chat_action(message.chat.id, 'upload_video')
    
    if platform == 'tiktok':
        # محاولة الخدمة الأولى
        video_url = download_tiktok(url)
        if not video_url:
            video_url = download_tiktok_alternative(url)
        
        if video_url:
            # تحميل الفيديو وإرساله
            try:
                response = requests.get(video_url, stream=True)
                if response.status_code == 200:
                    bot.send_video(
                        message.chat.id,
                        response.content,
                        caption="✅ تم التحميل من تيك توك بدون علامة مائية!",
                        reply_to_message_id=message.message_id
                    )
                else:
                    bot.reply_to(message, "❌ فشل تحميل الفيديو. حاول مرة أخرى.")
            except:
                bot.reply_to(message, "❌ حدث خطأ أثناء التحميل.")
        else:
            bot.reply_to(message, "❌ لم نتمكن من تحميل الفيديو. تأكد من الرابط وحاول مرة أخرى.")
    
    elif platform == 'instagram':
        # محاولة الخدمة الأولى
        video_url = download_instagram(url)
        if not video_url:
            video_url = download_instagram_alternative(url)
        
        if video_url:
            try:
                response = requests.get(video_url, stream=True)
                if response.status_code == 200:
                    bot.send_video(
                        message.chat.id,
                        response.content,
                        caption="✅ تم التحميل من انستغرام بدون علامة مائية!",
                        reply_to_message_id=message.message_id
                    )
                else:
                    bot.reply_to(message, "❌ فشل تحميل الفيديو. حاول مرة أخرى.")
            except:
                bot.reply_to(message, "❌ حدث خطأ أثناء التحميل.")
        else:
            bot.reply_to(message, "❌ لم نتمكن من تحميل الفيديو. تأكد من الرابط وحاول مرة أخرى.")

# ============= أوامر البوت =============
@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = """
🎬 *مرحباً بك في بوت تحميل الفيديوهات!* 🎬

أرسل لي رابط فيديو من:
• 📱 *تيك توك (TikTok)*
• 📷 *انستغرام (Instagram)*

وسأقوم بتحميله لك *بدون علامة مائية* وبجودة عالية!

━━━━━━━━━━━━━━━━━━━━━━━━━
📌 *الأوامر المتاحة:*
/start - إعادة تشغيل البوت
/help - المساعدة
/about - معلومات عن البوت

✨ فقط أرسل الرابط وسأقوم بالباقي!
"""
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
📖 *كيفية استخدام البوت:*

1️⃣ انسخ رابط الفيديو من:
   • تيك توك (TikTok)
   • انستغرام (Instagram)

2️⃣ ألصق الرابط هنا وأرسله

3️⃣ انتظر لحظات وسأرسل لك الفيديو بدون علامة مائية!

━━━━━━━━━━━━━━━━━━━━━━━━━
📝 *أمثلة على الروابط المدعومة:*

• `https://www.tiktok.com/@user/video/123456789`
• `https://www.instagram.com/p/CxYZ123/`

⚠️ *ملاحظة:* البوت لا يدعم تحميل الـ Stories حالياً.
"""
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['about'])
def about_command(message):
    about_text = """
ℹ️ *معلومات عن البوت:*

🤖 الإصدار: 1.0
📅 تاريخ الإنشاء: 2026
👨‍💻 مطور البوت: @invamsa

💡 *المميزات:*
• تحميل بدون علامة مائية
• دعم تيك توك وانستغرام
• سرعة عالية في التحميل
• مجاني بالكامل

🔒 *الخصوصية:* لا نحتفظ بأي فيديوهات على خوادمنا.
"""
    bot.reply_to(message, about_text, parse_mode='Markdown')

# ============= معالجة الرسائل (الروابط) =============
@bot.message_handler(func=lambda message: True)
def handle_links(message):
    text = message.text.strip()
    
    # كشف نوع المنصة
    platform = detect_platform(text)
    
    if not platform:
        bot.reply_to(
            message,
            "❌ *رابط غير مدعوم!*\n\n"
            "الرجاء إرسال رابط من:\n"
            "• تيك توك (tiktok.com)\n"
            "• انستغرام (instagram.com)\n\n"
            "للمساعدة: /help",
            parse_mode='Markdown'
        )
        return
    
    # إرسال رسالة انتظار
    waiting_msg = bot.reply_to(
        message,
        "🔄 *جاري تحميل الفيديو...*\n"
        "يرجى الانتظار لحظة ⏳",
        parse_mode='Markdown'
    )
    
    # معالجة الفيديو
    process_video(text, message, platform)
    
    # حذف رسالة الانتظار
    try:
        bot.delete_message(message.chat.id, waiting_msg.message_id)
    except:
        pass

# ============= تشغيل البوت =============
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════╗
    ║   بوت تحميل الفيديوهات يعمل 🎬   ║
    ║   TikTok & Instagram Downloader  ║
    ╚══════════════════════════════════╝
    """)
    print(f"🤖 البوت: @{bot.get_me().username}")
    print("✅ جاهز لاستقبال الروابط!\n")
    
    bot.infinity_polling(timeout=80)
