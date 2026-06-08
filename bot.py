import telebot
import re
import requests
import os
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ============= الإعدادات =============
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ============= الأزرار الثابتة =============
def main_keyboard():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=False)
    markup.add(
        KeyboardButton("🎵 تيك توك"),
        KeyboardButton("📷 انستغرام"),
        KeyboardButton("📘 فيسبوك"),
        KeyboardButton("🎥 يوتيوب"),
        KeyboardButton("🐦 تويتر/X"),
        KeyboardButton("💬 ريديت"),
        KeyboardButton("📱 حالات واتساب"),
        KeyboardButton("🎬 لايكي"),
        KeyboardButton("❓ المساعدة"),
        KeyboardButton("ℹ️ عن البوت")
    )
    return markup

# ============= دوال تحميل تيك توك =============
def download_tiktok(url):
    try:
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        if data.get('code') == 0:
            return data['data']['play']
        return None
    except:
        return None

def download_tiktok_alternative(url):
    try:
        api_url = f"https://tiksave.io/api/ajaxSearch"
        headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'q': url}
        response = requests.post(api_url, headers=headers, data=data, timeout=15)
        result = response.json()
        if result.get('success') and result.get('links'):
            return result['links']['video']
        return None
    except:
        return None

# ============= دوال تحميل انستغرام =============
def download_instagram(url):
    try:
        if '?' in url:
            url = url.split('?')[0]
        
        # الطريقة الأولى
        api_url = "https://snapinsta.app/api/ajaxSearch"
        headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'q': url}
        response = requests.post(api_url, headers=headers, data=data, timeout=15)
        result = response.json()
        
        if result.get('success') and result.get('medias'):
            for media in result['medias']:
                if media.get('type') == 'video':
                    return media['url']
        
        # الطريقة الثانية
        api_url2 = "https://instasave.io/api/ajaxSearch"
        response2 = requests.post(api_url2, headers=headers, data=data, timeout=15)
        result2 = response2.json()
        if result2.get('success') and result2.get('links'):
            return result2['links']['video']
        
        return None
    except:
        return None

# ============= دوال تحميل فيسبوك =============
def download_facebook(url):
    try:
        api_url = f"https://fdownloader.net/api/ajaxSearch"
        headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'q': url}
        response = requests.post(api_url, headers=headers, data=data, timeout=15)
        result = response.json()
        
        if result.get('success') and result.get('links'):
            return result['links']['sd']
        return None
    except:
        return None

def download_facebook_alternative(url):
    try:
        api_url = f"https://getvid.pw/api/download?url={url}"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        if data.get('success') and data.get('video_url'):
            return data['video_url']
        return None
    except:
        return None

# ============= دوال تحميل يوتيوب =============
def download_youtube(url):
    try:
        api_url = f"https://youtube-downloader9.p.rapidapi.com/?url={url}"
        # هذه الخدمة تتطلب مفتاح API - نستخدم خدمة بديلة
        return download_youtube_alternative(url)
    except:
        return download_youtube_alternative(url)

def download_youtube_alternative(url):
    try:
        api_url = f"https://ytdlapi.com/api/download?url={url}"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        if data.get('success') and data.get('video_url'):
            return data['video_url']
        return None
    except:
        return None

# ============= دوال تحميل تويتر/X =============
def download_twitter(url):
    try:
        api_url = f"https://twitsave.com/api/get?url={url}"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        if data.get('success') and data.get('video_link'):
            return data['video_link']
        return None
    except:
        return None

def download_twitter_alternative(url):
    try:
        api_url = f"https://twitterdl.p.rapidapi.com/api/download?url={url}"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        if data.get('success') and data.get('video_url'):
            return data['video_url']
        return None
    except:
        return None

# ============= دوال تحميل ريديت =============
def download_reddit(url):
    try:
        api_url = f"https://redditsave.com/api/get?url={url}"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        if data.get('success') and data.get('video_url'):
            return data['video_url']
        return None
    except:
        return None

# ============= دوال تحميل لايكي =============
def download_likee(url):
    try:
        api_url = f"https://likee.ga/api/get?url={url}"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        if data.get('success') and data.get('video_url'):
            return data['video_url']
        return None
    except:
        return None

# ============= دوال تحميل حالات واتساب =============
def download_whatsapp_status(url):
    """WhatsApp Status - يحتاج إلى معالجة خاصة"""
    try:
        # حالات الواتساب تتطلب رابط مباشر من التطبيق
        if 'wa.me' in url or 'whatsapp.com' in url:
            return url
        return None
    except:
        return None

# ============= كشف نوع المنصة =============
def detect_platform(url):
    url_lower = url.lower()
    
    platforms = {
        'tiktok': ['tiktok.com', 'vm.tiktok.com'],
        'instagram': ['instagram.com', 'instagr.am'],
        'facebook': ['facebook.com', 'fb.com', 'fb.watch'],
        'youtube': ['youtube.com', 'youtu.be'],
        'twitter': ['twitter.com', 'x.com'],
        'reddit': ['reddit.com', 'redd.it'],
        'likee': ['likee.com', 'like.video'],
        'whatsapp': ['wa.me', 'whatsapp.com']
    }
    
    for platform, domains in platforms.items():
        for domain in domains:
            if domain in url_lower:
                return platform
    
    return None

# ============= معالجة التحميل حسب المنصة =============
def process_video(url, message, platform):
    bot.send_chat_action(message.chat.id, 'upload_video')
    
    download_functions = {
        'tiktok': [download_tiktok, download_tiktok_alternative],
        'instagram': [download_instagram],
        'facebook': [download_facebook, download_facebook_alternative],
        'youtube': [download_youtube, download_youtube_alternative],
        'twitter': [download_twitter, download_twitter_alternative],
        'reddit': [download_reddit],
        'likee': [download_likee],
        'whatsapp': [download_whatsapp_status]
    }
    
    functions = download_functions.get(platform, [])
    video_url = None
    
    for func in functions:
        try:
            video_url = func(url)
            if video_url:
                break
        except:
            continue
    
    platform_names = {
        'tiktok': 'تيك توك',
        'instagram': 'انستغرام',
        'facebook': 'فيسبوك',
        'youtube': 'يوتيوب',
        'twitter': 'تويتر/X',
        'reddit': 'ريديت',
        'likee': 'لايكي',
        'whatsapp': 'واتساب'
    }
    
    if video_url:
        try:
            response = requests.get(video_url, stream=True, timeout=30)
            if response.status_code == 200:
                bot.send_video(
                    message.chat.id,
                    response.content,
                    caption=f"✅ تم التحميل بنجاح من {platform_names.get(platform, platform)}!\n🚫 بدون علامة مائية",
                    reply_to_message_id=message.message_id
                )
            else:
                bot.reply_to(message, f"❌ فشل تحميل الفيديو من {platform_names.get(platform, platform)}. حاول مرة أخرى.")
        except Exception as e:
            bot.reply_to(message, f"❌ حدث خطأ أثناء التحميل: {str(e)[:50]}")
    else:
        bot.reply_to(message, 
            f"❌ *لم نتمكن من تحميل الفيديو من {platform_names.get(platform, platform)}*\n\n"
            f"الأسباب المحتملة:\n"
            f"• الرابط غير صحيح\n"
            f"• المحتوى خاص أو محذوف\n"
            f"• المنصة غير مدعومة بالكامل\n\n"
            f"💡 حاول استخدام رابط آخر أو تواصل مع المطور",
            parse_mode='Markdown')

# ============= أوامر البوت =============
@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = """
🌐 *مرحباً بك في البوت الشامل لتحميل فيديوهات التواصل الاجتماعي!* 🌐

🎬 *المنصات المدعومة:*

📱 • تيك توك (TikTok)
📷 • انستغرام (Instagram)
📘 • فيسبوك (Facebook)
🎥 • يوتيوب (YouTube)
🐦 • تويتر / X (Twitter)
💬 • ريديت (Reddit)
🎵 • لايكي (Likee)
💚 • حالات واتساب (WhatsApp Status)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ *كيفية الاستخدام:*
1️⃣ اختر المنصة من الأزرار أدناه
2️⃣ أرسل رابط الفيديو
3️⃣ استلم الفيديو بدون علامة مائية

✨ *مجاني بالكامل - بدون علامات مائية - جودة عالية*
"""
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
📖 *طريقة استخدام البوت:*

1️⃣ اضغط على زر المنصة التي تريد التحميل منها
2️⃣ أرسل رابط الفيديو
3️⃣ انتظر لحظات وسأرسل لك الفيديو

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 *أمثلة الروابط المدعومة:*

• تيك توك: `https://www.tiktok.com/@user/video/123456789`
• انستغرام: `https://www.instagram.com/p/CxYZ123/`
• فيسبوك: `https://www.facebook.com/watch/?v=123456789`
• يوتيوب: `https://youtu.be/abcdefghijk`
• تويتر: `https://x.com/user/status/123456789`
• ريديت: `https://www.reddit.com/r/subreddit/comments/abc123/`
• لايكي: `https://likee.com/video/123456789`

⚠️ *ملاحظات مهمة:*
• البوت لا يدعم الحسابات الخاصة
• بعض المنصات قد تحتاج إلى وقت أطول للتحميل
• جميع الفيديوهات بدون علامة مائية
"""
    bot.reply_to(message, help_text, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['about'])
def about_command(message):
    about_text = """
ℹ️ *معلومات عن البوت:*

🤖 *الاسم:* VidSaverNoLogoBot
📅 *الإصدار:* 3.0 - الشامل
🌍 *المنصات المدعومة:* 8 منصات
💡 *المميزات:*
• تحميل بدون علامة مائية
• دعم متعدد المنصات
• سرعة عالية
• مجاني بالكامل

👨‍💻 *المطور:* @invamsa
🔒 *الخصوصية:* لا نحتفظ بأي فيديوهات

📢 *للاقتراحات والتواصل:* @invamsa
"""
    bot.reply_to(message, about_text, parse_mode='Markdown', reply_markup=main_keyboard())

# ============= التعامل مع الأزرار =============
@bot.message_handler(func=lambda message: message.text in ["🎵 تيك توك", "📷 انستغرام", "📘 فيسبوك", "🎥 يوتيوب", "🐦 تويتر/X", "💬 ريديت", "🎬 لايكي", "📱 حالات واتساب"])
def platform_selection(message):
    platform_map = {
        "🎵 تيك توك": "تيك توك",
        "📷 انستغرام": "انستغرام",
        "📘 فيسبوك": "فيسبوك",
        "🎥 يوتيوب": "يوتيوب",
        "🐦 تويتر/X": "تويتر",
        "💬 ريديت": "ريديت",
        "🎬 لايكي": "لايكي",
        "📱 حالات واتساب": "واتساب"
    }
    
    platform = platform_map.get(message.text, "")
    
    examples = {
        "تيك توك": "https://www.tiktok.com/@user/video/123456789",
        "انستغرام": "https://www.instagram.com/p/CxYZ123/",
        "فيسبوك": "https://www.facebook.com/watch/?v=123456789",
        "يوتيوب": "https://youtu.be/abcdefghijk",
        "تويتر": "https://x.com/user/status/123456789",
        "ريديت": "https://www.reddit.com/r/subreddit/comments/abc123/",
        "لايكي": "https://likee.com/video/123456789",
        "واتساب": "رابط الحالة من تطبيق واتساب"
    }
    
    bot.reply_to(message, 
        f"✅ *تم اختيار {platform}* ✅\n\n"
        f"📌 *أرسل رابط الفيديو الآن:*\n"
        f"مثال: `{examples.get(platform, 'الرابط')}`",
        parse_mode='Markdown',
        reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "❓ المساعدة")
def help_button(message):
    help_command(message)

@bot.message_handler(func=lambda message: message.text == "ℹ️ عن البوت")
def about_button(message):
    about_command(message)

# ============= معالجة الروابط =============
@bot.message_handler(func=lambda message: True)
def handle_links(message):
    text = message.text.strip()
    
    # تجاهل الأوامر والأزرار
    if text.startswith('/'):
        return
    
    buttons = ["🎵 تيك توك", "📷 انستغرام", "📘 فيسبوك", "🎥 يوتيوب", "🐦 تويتر/X", "💬 ريديت", "🎬 لايكي", "📱 حالات واتساب", "❓ المساعدة", "ℹ️ عن البوت"]
    if text in buttons:
        return
    
    platform = detect_platform(text)
    
    if not platform:
        bot.reply_to(
            message,
            "❌ *رابط غير مدعوم!*\n\n"
            "المنصات المدعومة حالياً:\n"
            "• تيك توك 📱\n"
            "• انستغرام 📷\n"
            "• فيسبوك 📘\n"
            "• يوتيوب 🎥\n"
            "• تويتر/X 🐦\n"
            "• ريديت 💬\n"
            "• لايكي 🎵\n\n"
            "📢 استخدم الأزرار أدناه لاختيار المنصة أولاً 👇",
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )
        return
    
    waiting_msg = bot.reply_to(
        message,
        f"🔄 *جاري تحميل الفيديو...*\n"
        f"يرجى الانتظار لحظة ⏳",
        parse_mode='Markdown'
    )
    
    process_video(text, message, platform)
    
    try:
        bot.delete_message(message.chat.id, waiting_msg.message_id)
    except:
        pass

# ============= تشغيل البوت =============
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════╗
    ║   بوت تحميل الفيديوهات الشامل V3.0 🎬   ║
    ║   8 منصات - تحميل بدون علامة مائية     ║
    ║   TikTok - IG - FB - YT - X - Reddit    ║
    ╚══════════════════════════════════════════╝
    """)
    print(f"🤖 البوت: @{bot.get_me().username}")
    print("✅ جاهز لاستقبال الروابط!")
    print("📱 المنصات المدعومة: 8 منصات\n")
    
    bot.infinity_polling(timeout=80)
