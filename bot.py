import telebot
import re
import requests
import os
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ============= الإعدادات =============
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ============= الأزرار الثابتة (تظهر دائماً في الأسفل) =============
def main_keyboard():
    """لوحة الأزرار الرئيسية الثابتة"""
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=False)
    markup.add(
        KeyboardButton("🎵 تحميل تيك توك"),
        KeyboardButton("📷 تحميل انستغرام"),
        KeyboardButton("❓ المساعدة"),
        KeyboardButton("ℹ️ عن البوت"),
        KeyboardButton("📊 الإحصائيات")
    )
    return markup

# ============= أزرار مضمنة (اختيارية تظهر داخل الرسائل) =============
def inline_buttons():
    """أزرار مضمنة تظهر داخل رسالة الترحيب"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎵 تيك توك", callback_data="help_tiktok"),
        InlineKeyboardButton("📷 انستغرام", callback_data="help_instagram"),
        InlineKeyboardButton("📖 طريقة الاستخدام", callback_data="how_to_use"),
        InlineKeyboardButton("👨‍💻 المطور", url="https://t.me/invamsa")
    )
    return markup

# ============= دوال التحميل (نفس الكود القديم) =============
def download_tiktok(url):
    try:
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url)
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
        response = requests.post(api_url, headers=headers, data=data)
        result = response.json()
        if result.get('success') and result.get('links'):
            return result['links']['video']
        return None
    except:
        return None

def download_instagram(url):
    try:
        if '?' in url:
            url = url.split('?')[0]
        api_url = "https://snapinsta.app/api/ajaxSearch"
        headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'}
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

def download_instagram_alternative(url):
    try:
        api_url = "https://instasave.io/api/ajaxSearch"
        headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'q': url}
        response = requests.post(api_url, headers=headers, data=data)
        result = response.json()
        if result.get('success') and result.get('links'):
            return result['links']['video']
        return None
    except:
        return None

def detect_platform(url):
    url = url.lower()
    if 'tiktok.com' in url:
        return 'tiktok'
    elif 'instagram.com' in url or 'instagr.am' in url:
        return 'instagram'
    return None

def process_video(url, message, platform):
    bot.send_chat_action(message.chat.id, 'upload_video')
    
    if platform == 'tiktok':
        video_url = download_tiktok(url)
        if not video_url:
            video_url = download_tiktok_alternative(url)
        
        if video_url:
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
            bot.reply_to(message, "❌ لم نتمكن من تحميل الفيديو. تأكد من الرابط.")
    
    elif platform == 'instagram':
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
            bot.reply_to(message, "❌ لم نتمكن من تحميل الفيديو. تأكد من الرابط.")

# ============= أوامر البوت =============
@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = """
🎬 *مرحباً بك في بوت تحميل الفيديوهات!* 🎬

✨ *يمكنك استخدام الأزرار أدناه أو إرسال الرابط مباشرة*

📥 *المنصات المدعومة:*
• 📱 تيك توك (TikTok)
• 📷 انستغرام (Instagram)

⚡ *مميزات البوت:*
✅ تحميل بدون علامة مائية
✅ جودة عالية HD
✅ سرعة فائقة
✅ مجاني بالكامل

━━━━━━━━━━━━━━━━━━━━━━━━━
🔹 *فقط أرسل الرابط وسأقوم بالباقي!*
"""
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
📖 *طريقة استخدام البوت:*

🔹 *الطريقة الأولى (الأزرار):*
• اضغط على زر "🎵 تحميل تيك توك" أو "📷 تحميل انستغرام"
• ثم أرسل الرابط

🔹 *الطريقة الثانية (مباشر):*
• فقط ألصق رابط الفيديو وأرسله

━━━━━━━━━━━━━━━━━━━━━━━━━
📝 *أمثلة الروابط:*
• تيك توك: `https://www.tiktok.com/@user/video/123456789`
• انستغرام: `https://www.instagram.com/p/CxYZ123/`

⚠️ *ملاحظة:* البوت لا يدعم الـ Stories حالياً
"""
    bot.reply_to(message, help_text, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['about'])
def about_command(message):
    about_text = """
ℹ️ *معلومات عن البوت:*

🤖 *الاسم:* VidSaverNoLogoBot
📅 *الإصدار:* 2.0
💡 *المميزات:*
• تحميل بدون علامة مائية
• دعم تيك توك وانستغرام
• سرعة عالية
• مجاني بالكامل

👨‍💻 *المطور:* @invamsa
🔒 *الخصوصية:* لا نحتفظ بأي فيديوهات
"""
    bot.reply_to(message, about_text, parse_mode='Markdown', reply_markup=main_keyboard())

# ============= التعامل مع الأزرار الثابتة =============
@bot.message_handler(func=lambda message: message.text == "🎵 تحميل تيك توك")
def tiktok_button(message):
    bot.reply_to(message, 
        "🎵 *تم اختيار تيك توك* ✅\n\n"
        "📌 *أرسل رابط الفيديو الآن:*\n"
        "مثال: `https://www.tiktok.com/@user/video/123456789`",
        parse_mode='Markdown',
        reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "📷 تحميل انستغرام")
def instagram_button(message):
    bot.reply_to(message, 
        "📷 *تم اختيار انستغرام* ✅\n\n"
        "📌 *أرسل رابط الفيديو الآن:*\n"
        "مثال: `https://www.instagram.com/p/CxYZ123/`",
        parse_mode='Markdown',
        reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == "❓ المساعدة")
def help_button(message):
    help_command(message)

@bot.message_handler(func=lambda message: message.text == "ℹ️ عن البوت")
def about_button(message):
    about_command(message)

@bot.message_handler(func=lambda message: message.text == "📊 الإحصائيات")
def stats_button(message):
    stats_text = """
📊 *إحصائيات البوت*

🎬 عدد مرات التحميل: غير متاح حالياً
📱 عدد المستخدمين: غير متاح حالياً

💡 *نصيحة:* للإحصائيات المفصلة، تواصل مع المطور
"""
    bot.reply_to(message, stats_text, parse_mode='Markdown', reply_markup=main_keyboard())

# ============= معالجة الأزرار المضمنة (callback) =============
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "help_tiktok":
        bot.answer_callback_query(call.id, "أرسل رابط فيديو تيك توك", show_alert=True)
    elif call.data == "help_instagram":
        bot.answer_callback_query(call.id, "أرسل رابط فيديو انستغرام", show_alert=True)
    elif call.data == "how_to_use":
        bot.answer_callback_query(call.id, "فقط أرسل رابط الفيديو وسأقوم بالباقي!", show_alert=True)
    
    # تحديث الرسالة (اختياري)
    try:
        bot.edit_message_text(
            "✅ *تم اختيار المساعدة*\n\nأرسل رابط الفيديو مباشرة",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )
    except:
        pass

# ============= معالجة الروابط =============
@bot.message_handler(func=lambda message: True)
def handle_links(message):
    text = message.text.strip()
    
    # تجاهل الرسائل التي هي أوامر أو أزرار
    if text.startswith('/'):
        return
    if text in ["🎵 تحميل تيك توك", "📷 تحميل انستغرام", "❓ المساعدة", "ℹ️ عن البوت", "📊 الإحصائيات"]:
        return
    
    platform = detect_platform(text)
    
    if not platform:
        bot.reply_to(
            message,
            "❌ *رابط غير مدعوم!*\n\n"
            "الرجاء إرسال رابط من:\n"
            "• تيك توك (tiktok.com)\n"
            "• انستغرام (instagram.com)\n\n"
            "أو استخدم الأزرار أدناه للمساعدة 👇",
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )
        return
    
    waiting_msg = bot.reply_to(
        message,
        "🔄 *جاري تحميل الفيديو...*\n"
        "يرجى الانتظار لحظة ⏳",
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
    ╔══════════════════════════════════════╗
    ║   بوت تحميل الفيديوهات V2.0 🎬      ║
    ║   مع أزرار تفاعلية ثابتة            ║
    ║   TikTok & Instagram Downloader      ║
    ╚══════════════════════════════════════╝
    """)
    print(f"🤖 البوت: @{bot.get_me().username}")
    print("✅ جاهز لاستقبال الروابط!")
    print("📱 الأزرار الثابتة: تحميل تيك توك | تحميل انستغرام | مساعدة | عن البوت\n")
    
    bot.infinity_polling(timeout=80)
