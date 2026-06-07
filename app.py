from threading import Thread
from flask import Flask
import bot  # هذا هو ملف البوت الرئيسي الخاص بك

# إنشاء تطبيق Flask بسيط جداً
app = Flask('')

@app.route('/')
def home():
    return "✅ بوت التمويل الإعلاني يعمل!", 200

# دالة لتشغيل البوت في الخلفية
def run_bot():
    # تشغيل polling الخاص بالبوت في thread منفصل
    bot.bot.infinity_polling()

if __name__ == "__main__":
    # بدء تشغيل البوت في thread
    bot_thread = Thread(target=run_bot)
    bot_thread.start()
    
    # تشغيل خادم Flask (هذا ما سيفتح المنفذ)
    app.run(host='0.0.0.0', port=10000)
