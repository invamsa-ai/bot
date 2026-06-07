import os
import telebot
from openai import OpenAI
from dotenv import load_dotenv
import logging
import base64

# تحميل المتغيرات من ملف .env
load_dotenv()

# إعداد التسجيل للأخطاء
logging.basicConfig(level=logging.INFO)

# تهيئة البوت
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# قاموس لحفظ تاريخ المحادثات لكل مستخدم
user_conversations = {}

def get_conversation_history(user_id, max_messages=10):
    """الحصول على تاريخ المحادثة للمستخدم"""
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    return user_conversations[user_id][-max_messages:]

def save_conversation(user_id, role, content):
    """حفظ رسالة في تاريخ المحادثة"""
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    user_conversations[user_id].append({"role": role, "content": content})
    
    if len(user_conversations[user_id]) > 50:
        user_conversations[user_id] = user_conversations[user_id][-50:]

def clear_conversation(user_id):
    """مسح تاريخ المحادثة للمستخدم"""
    if user_id in user_conversations:
        user_conversations[user_id] = []
    return True

# أمر /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
✨ *مرحباً بك في بوت GPTAIServBot!* ✨

يمكنني مساعدتك في:
📝 *الرد على أسئلتك* - اسألني أي شيء
🖼️ *تحليل الصور* - أرسل صورة وسأصفها لك
💬 *محادثة ذكية* - سأتذكر سياق حديثك

🔧 *الأوامر المتاحة:*
/start - إظهار هذه الرسالة
/help - المساعدة
/clear - مسح تاريخ المحادثة

🎯 *فقط أرسل لي رسالتك وسأرد عليك فوراً!*
    """
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

# أمر /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
📚 *كيفية استخدام البوت:*

*للأسئلة النصية:*
فقط اكتب سؤالك وسأجيب عليه بأفضل صورة

*للصور:*
أرسل الصورة مع وصف (كابتشن) وسأقوم بتحليلها

*للمحادثة المستمرة:*
أتذكر سياق آخر 10 رسائل، استخدم /clear لمسح الذاكرة

🔑 *نصائح:*
- كلما كانت أسئلتك أكثر تحديداً، كانت إجاباتي أفضل
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')

# أمر /clear لمسح تاريخ المحادثة
@bot.message_handler(commands=['clear'])
def clear_history(message):
    user_id = message.from_user.id
    clear_conversation(user_id)
    bot.reply_to(message, "🧹 تم مسح تاريخ المحادثة! يمكنك البدء من جديد.")

# معالجة الرسائل النصية
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text_message(message):
    user_id = message.from_user.id
    user_message = message.text
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    save_conversation(user_id, "user", user_message)
    conversation_history = get_conversation_history(user_id)
    
    try:
        messages = [
            {"role": "system", "content": "أنت مساعد ذكي ومفيد. أجب على الأسئلة بدقة ووضوح. استخدم اللغة العربية."}
        ]
        messages.extend(conversation_history)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        ai_response = response.choices[0].message.content
        save_conversation(user_id, "assistant", ai_response)
        bot.reply_to(message, ai_response)
            
    except Exception as e:
        error_msg = f"❌ عذراً، حدث خطأ: {str(e)}"
        bot.reply_to(message, error_msg)
        logging.error(f"Error for user {user_id}: {str(e)}")

# معالجة الصور
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    prompt = message.caption or "ماذا يوجد في هذه الصورة؟ صفها بتفصيل"
    
    bot.send_chat_action(message.chat.id, 'typing')
    waiting_msg = bot.reply_to(message, "🖼️ جاري تحليل الصورة... لحظة من فضلك")
    
    try:
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_base64 = base64.b64encode(downloaded_file).decode('utf-8')
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        bot.delete_message(message.chat.id, waiting_msg.message_id)
        bot.reply_to(message, f"🖼️ *تحليل الصورة:*\n\n{ai_response}", parse_mode='Markdown')
        
    except Exception as e:
        bot.edit_message_text(
            f"❌ حدث خطأ أثناء تحليل الصورة: {str(e)}", 
            message.chat.id, 
            waiting_msg.message_id
        )

# تشغيل البوت
if __name__ == "__main__":
    print("🤖 البوت يعمل الآن...")
    print(f"البوت: @GPTAIServBot")
    bot.infinity_polling()