import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from datetime import datetime
import re
import os

# ============= الإعدادات =============
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)

# ============= قاعدة البيانات =============
conn = sqlite3.connect('advertising_bot.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS ad_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    channel_type TEXT,
    channel_link TEXT,
    duration_days INTEGER,
    budget_stars INTEGER,
    ad_content TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP
)''')
conn.commit()

# ============= شروط الاستخدام =============
TERMS_SHORT = """
📜 *شروط الاستخدام – ملخص*

✅ مسموح: محتوى عام، تعليمي، ترفيهي، منتجات حقيقية
⛔ ممنوع: إباحي، هاك، حسابات مخترقة، سياسي
"""

def terms_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ أوافق", callback_data="accept"))
    return markup

def channel_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🟢 محتوى", callback_data="type_content"))
    markup.add(InlineKeyboardButton("🛒 بيع", callback_data="type_shop"))
    return markup

def confirm_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ تأكيد", callback_data="confirm"))
    markup.add(InlineKeyboardButton("🔙 إعادة", callback_data="restart"))
    return markup

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.from_user.id] = {}
    bot.reply_to(message, f"✨ مرحباً!\n\n{TERMS_SHORT}\n\nأوافق على الشروط؟", 
                 parse_mode='Markdown', reply_markup=terms_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = call.from_user.id
    
    if call.data == "accept":
        bot.edit_message_text("✅ اختر نوع قناتك:", call.message.chat.id, 
                              call.message.message_id, reply_markup=channel_keyboard())
    
    elif call.data in ["type_content", "type_shop"]:
        user_data[uid]['type'] = 'content' if call.data == "type_content" else 'shop'
        bot.edit_message_text("📝 أرسل بيانات الإعلان بهذا الشكل:\n\n"
                              "رابط القناة: t.me/...\n"
                              "المدة: 7\n"
                              "الميزانية: 500\n"
                              "محتوى الإعلان: نص الإعلان هنا",
                              call.message.chat.id, call.message.message_id)
    
    elif call.data == "confirm":
        data = user_data.get(uid, {})
        if all(k in data for k in ['link', 'duration', 'budget', 'content']):
            c.execute("INSERT INTO ad_requests (user_id, username, channel_type, channel_link, duration_days, budget_stars, ad_content, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (uid, call.from_user.username, data['type'], data['link'], data['duration'], data['budget'], data['content'], datetime.now()))
            conn.commit()
            rid = c.lastrowid
            
            bot.send_message(ADMIN_ID, f"📢 طلب جديد #{rid}\nمن: @{call.from_user.username}\nنوع: {data['type']}\nرابط: {data['link']}\nمدة: {data['duration']}\nميزانية: {data['budget']}")
            bot.edit_message_text(f"✅ تم استلام طلبك رقم #{rid}\nسيتم مراجعته قريباً", 
                                  call.message.chat.id, call.message.message_id)
            del user_data[uid]
        else:
            bot.answer_callback_query(call.id, "بيانات ناقصة، أعد كتابة الإعلان", True)
    
    elif call.data == "restart":
        del user_data[uid]
        bot.edit_message_text("🔄 أعد كتابة البيانات من البداية", 
                              call.message.chat.id, call.message.message_id)
    
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: True)
def get_details(m):
    uid = m.from_user.id
    if uid not in user_data or 'type' not in user_data[uid]:
        bot.reply_to(m, "⚠️ استخدم /start أولاً")
        return
    
    lines = m.text.split('\n')
    data = {}
    for line in lines:
        if 'رابط' in line:
            data['link'] = line.split(':')[-1].strip()
        elif 'المدة' in line:
            data['duration'] = int(line.split(':')[-1].strip())
        elif 'الميزانية' in line:
            data['budget'] = int(line.split(':')[-1].strip())
        elif 'محتوى' in line:
            data['content'] = line.split(':')[-1].strip()
    
    if all(k in data for k in ['link', 'duration', 'budget', 'content']):
        user_data[uid].update(data)
        bot.reply_to(m, f"📋 ملخص:\nرابط: {data['link']}\nمدة: {data['duration']}\nميزانية: {data['budget']}\nمحتوى: {data['content']}\n\nهل البيانات صحيحة؟", 
                     reply_markup=confirm_keyboard())
    else:
        bot.reply_to(m, "❌ صيغة خاطئة. استخدم:\nرابط القناة: ...\nالمدة: ...\nالميزانية: ...\nمحتوى الإعلان: ...")

print("✅ بوت التمويل الإعلاني يعمل!")
bot.infinity_polling()
