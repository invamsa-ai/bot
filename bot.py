import telebot
import re
import requests
import os
import time
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ============= الإعدادات =============
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ============= الأزرار الثابتة =============
def main_keyboard():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=False)
    markup.add(
        KeyboardButton("🎵 تحميل تيك توك"),
        KeyboardButton("📷 تحميل انستغرام"),
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

# ============= دوال تحميل انستغرام (محسنة) =============
def download_instagram_v1(url):
    """الطريقة الأولى: استخدام snapinsta"""
    try:
        if '?' in url:
            url = url.split('?')[0]
        
        api_url = "https://snapinsta.app/api/ajaxSearch"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = {'q': url}
        
        response = requests.post(api_url, headers=headers, data=data, timeout=15)
        result = response.json()
        
        if result.get('success') and result.get('medias'):
            for media in result['medias']:
                if media.get('type') == 'video':
                    return media['url']
        return None
    except:
        return None

def download_instagram_v2(url):
    """الطريقة الثانية: استخدام instasave"""
    try:
        if '?' in url:
            url = url.split('?')[0]
            
        api_url = "https://instasave.io/api/ajaxSearch"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'q': url}
        
        response = requests.post(api_url, headers=headers, data=data, timeout=15)
        result = response.json()
        
        if result.get('success') and result.get('links'):
            if 'video' in result['links']:
                return result['links']['video']
        return None
    except:
        return None

def download_instagram_v3(url):
    """الطريقة الثالثة: استخدام saveinsta"""
    try:
        if '?' in url:
            url = url.split('?')[0]
            
        api_url = "https://saveinsta.app/api/ajaxSearch"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'q': url}
        
        response = requests.post(api_url, headers=headers, data=data, timeout=15)
        result = response.json()
        
        if result.get('success') and result.get('medias'):
            for media in result['medias']:
                if media.get('type') == 'video' and media.get('url'):
                    return media['url']
        return None
    except:
        return None

def download_instagram_v4(url):
    """الطريقة الرابعة: api بديلة"""
    try:
        # تنظيف الرابط
        if '/reel/' in url:
            url = url.split('?')[0]
        
        api_url = "https://instagram-downloader-download-instagram-videos-stories.p.rapidapi.com/index"
        # هذه الخدمة تتطلب مفتاح API - قد لا تعمل بدون تسجيل
        # نتركها كخيار احتياطي فقط
        return None
    except:
        return None

def download_instagram(url):
    """محاولة جميع الطرق لتحميل فيديو انستغرام"""
    methods = [
        download_instagram_v1,
        download_instagram_v2,
        download_instagram_v3
    ]
    
    for i, method in enumerate(methods, 1):
        try:
            print(f"محاولة تحميل انستغرام - الطريقة {i}...")
            video_url = method(url)
            if video_url:
                print(f"نجحت الطريقة {i}!")
                return video_url
        except Exception as e:
            print(f"الطريقة {i} فشلت: {e}")
            continue
    
    return None

# ============= دوال تحميل عامة =============
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
                response = requests.get(video_url, stream=True, timeout=30)
                if response.status_code == 200:
                    bot.send_video(
                        message.chat.id,
                        response.content,
                        caption="✅ تم التحميل من تيك توك بدون علامة مائية!",
                        reply_to_message_id=message.message_id
                    )
                else:
                    bot.reply_to(message, "❌ فشل تحميل الفيديو. حاول مرة أخرى.")
            except Exception as e:
                bot.reply_to(message, f"❌ حدث خطأ: {str(e)[:50]}")
        else:
            bot.reply_to(message, "❌ لم نتمكن من تحميل الفيديو. تأكد من الرابط وحاول مرة أخرى.")
    
    elif platform == 'instagram':
        bot.send_message(message.chat.id, "🔄 جاري تحميل الفيديو من انستغرام... قد يستغرق بضع ثوانٍ")
        
        video_url = download_instagram(url)
        
        if video_url:
            try:
                response = requests.get(video_url, stream=True, timeout=30)
                if response.status_code == 200:
                    bot.send_video(
                        message.chat.id,
                        response.content,
                        caption="✅ تم التحميل من انستغرام بدون علامة مائية!",
                        reply_to_message_id=message.message_id
                    )
                else:
                    bot.reply_to(message, "❌ فشل تحميل الفيديو. حاول مرة أخرى.")
            except Exception as e:
                bot.reply_to(message, f"❌ حدث خطأ أثناء التحميل: {str(e)[:50]}")
        else:
            bot.reply_to(message, 
                "❌ *لم نتمكن من تحميل الفيديو*\n\n"
                "الأسباب المحتملة:\n"
                "• الرابط غير صحيح\n"
                "• الحساب خاص\n"
                "• الفيديو غير موجود\n\n"
                "💡 نصيحة: تأكد من أن الفيديو منشور بشكل عام",
                parse_mode='Markdown')

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

⚠️ *ملاحظة:* 
• البوت لا يدعم الـ Stories حالياً
• الحسابات الخاصة غير مدعومة
"""
    bot.reply_to(message, help_text, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['about'])
def about_command(message):
    about_text = """
ℹ️ *معلومات عن البوت:*

🤖 *الاسم:* VidSaverNoLogoBot
📅 *الإصدار:* 2.1
💡 *المميزات:*
• تحميل بدون علامة مائية
• دعم تيك توك وانستغرام
• سرعة عالية
• مجاني بالكامل

👨‍💻 *المطور:* @invamsa
🔒 *الخصوصية:* لا نحتفظ بأي فيديوهات
"""
    bot.reply_to(message, about_text, parse_mode='Markdown', reply_markup=main_keyboard())

# ============= التعامل مع الأزرار =============
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
        "مثال: `https://www.instagram.com/p/CxYZ123/`\n\n"
        "⚠️ ملاحظة: الحساب يجب أن يكون عاماً",
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
    if text in ["🎵 تحميل تيك توك", "📷 تحميل انستغرام", "❓ المساعدة", "ℹ️ عن البوت"]:
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
    ║   بوت تحميل الفيديوهات V2.1 🎬      ║
    ║   TikTok & Instagram Downloader      ║
    ╚══════════════════════════════════════╝
    """)
    print(f"🤖 البوت: @{bot.get_me().username}")
    print("✅ جاهز لاستقبال الروابط!")
    print("📱 تم تحسين تحميل انستغرام بثلاث طرق مختلفة!\n")
    
    bot.infinity_polling(timeout=80)
