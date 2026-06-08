import telebot
import re
import requests
import os
import json
import yt_dlp  # المكتبة الأساسية لتحميل الفيديوهات
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

# ============= دالة التحميل الشاملة باستخدام مكتبة بايثون yt-dlp =============
def download_with_ytdlp(url, output_filename):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_filename,
        'no_warnings': True,
        'quiet': True,
        'nocheckcertificate': True,  # لتخطي مشاكل حظر الشهادات على السيرفرات
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

    if platform == 'whatsapp':
        bot.reply_to(message, "⚠️ حالات واتساب تتطلب رفع الملف يدوياً، لا يمكن معالجتها عبر رابط خارجي حالياً.")
        return

    output_filename = f"video_{message.message_id}.mp4"
    
    try:
        actual_file = download_with_ytdlp(url, output_filename)
        
        if os.path.exists(actual_file):
            with open(actual_file, 'rb') as video_file:
                bot.send_video(
                    message.chat.id,
                    video_file,
                    caption=f"✅ تم التحميل بنجاح من {platform_names.get(platform, platform)}!\n🚫 بدون علامة مائية",
                    reply_to_message_id=message.message_id
                )
        else:
            bot.reply_to(message, f"❌ فشل معالجة الفيديو من {platform_names.get(platform, platform)}. حاول مرة أخرى.")
            
    except Exception as e:
        print(f"Error logs: {str(e)}")
        # إذا كان الخطأ بسبب حظر يوتيوب للسيرفرات (Sign in to confirm...)
        if "Sign in to confirm" in str(e) and platform == 'youtube':
            bot.reply_to(message, 
                f"⚠️ *عذراً! يوتيوب يفرض قيوداً صارمة حالياً على خوادم التحميل السحابية.*\n\n"
                f"💡 جرب روابط من منصات أخرى مثل تيك توك، انستغرام، أو فيسبوك، فهي تعمل بثبات أعلى وبدون قيود.",
                parse_mode='Markdown')
        else:
            bot.reply_to(message, 
                f"❌ *لم نتمكن من تحميل الفيديو من {platform_names.get(platform, platform)}*\n\n"
                f"الأسباب المحتملة:\n"
                f"• الرابط غير صحيح أو قد يكون الحساب خاصاً (Private)\n"
                f"• الفيديو محذوف من المنصة الأساسية\n\n"
                f"💡 حاول استخدام رابط آخر أو تواصل مع المطور.",
                parse_mode='Markdown')
            
    finally:
        if os.path.exists(output_filename):
            os.remove(output_filename)
        elif 'actual_file' in locals() and os.path.exists(actual_file):
            os.remove(actual_file)

# ============= أوامر البوت =============
@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = """
🌐 *مرحباً بك في البوت الشامل لتحميل فيديوهات التواصل الاجتماعي!* 🌐

🎬 *المنصات المدعومة:*
📱 • تيك توك (TikTok) | 📷 • انستغرام (Instagram)
📘 • فيسبوك (Facebook) | 🎥 • يوتيوب (YouTube)
🐦 • تويتر / X (Twitter) | 💬 • ريديت (Reddit)
🎵 • لايكي (Likee) | 💚 • حالات واتساب

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ *كيفية الاستخدام:* أرسل رابط الفيديو مباشرة وسأقوم بتحميله لك فوراً بجودة عالية وبدون علامة مائية!
"""
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = "📖 *طريقة الاستخدام:* اختر المنصة أو أرسل الرابط مباشرة، وسيتكفل البوت بالباقي محلياً وبأعلى استقرار."
    bot.reply_to(message, help_text, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['about'])
def about_command(message):
    about_text = "👨‍💻 *المطور:* @invamsa \n🤖 البوت يعمل بكفاءة عبر مكتبة yt-dlp بشكل مستقل."
    bot.reply_to(message, about_text, parse_mode='Markdown', reply_markup=main_keyboard())

# ============= التعامل مع الأزرار =============
@bot.message_handler(func=lambda message: message.text in ["🎵 تيك توك", "📷 انستغرام", "📘 فيسبوك", "🎥 يوتيوب", "🐦 تويتر/X", "💬 ريديت", "🎬 لايكي", "📱 حالات واتساب"])
def platform_selection(message):
    bot.reply_to(message, f"📌 *أرسل رابط الفيديو الخاص بالمنصة الآن للتحميل المباشر:*", parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "❓ المساعدة")
def help_button(message): help_command(message)

@bot.message_handler(func=lambda message: message.text == "ℹ️ عن البوت")
def about_button(message): about_command(message)

# ============= معالجة الروابط =============
@bot.message_handler(func=lambda message: True)
def handle_links(message):
    text = message.text.strip()
    if text.startswith('/') or text in ["🎵 تيك توك", "📷 انستغرام", "📘 فيسبوك", "🎥 يوتيوب", "🐦 تويتر/X", "💬 ريديت", "🎬 لايكي", "📱 حالات واتساب", "❓ المساعدة", "ℹ️ عن البوت"]:
        return
    
    platform = detect_platform(text)
    if not platform:
        bot.reply_to(message, "❌ *رابط غير مدعوم!* يرجى إرسال رابط صحيح للمنصات المدعومة.")
        return
    
    waiting_msg = bot.reply_to(message, f"🔄 *جاري معالجة الرابط وتحميل الفيديو...* ⏳", parse_mode='Markdown')
    process_video(text, message, platform)
    try: bot.delete_message(message.chat.id, waiting_msg.message_id)
    except: pass

# ============= تشغيل البوت المستمر =============
if __name__ == "__main__":
    print("🤖 البوت يعمل الآن بنظام الـ Workers بثبات كامل وبدون تداخل منافذ...")
    bot.infinity_polling(timeout=80)
