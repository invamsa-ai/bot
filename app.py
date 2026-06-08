from flask import Flask
from threading import Thread
import bot

app = Flask('')

@app.route('/')
def home():
    return "البوت يعمل بكفاءة!"

def run():
    app.run(host='0.0.0.0', port=10000)

def start_bot():
    # تشغيل البوت في thread منفصل
    bot.bot.infinity_polling()

if __name__ == "__main__":
    # تشغيل البوت في الخلفية
    t = Thread(target=start_bot)
    t.start()
    # تشغيل خادم Flask
    run()
