from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import random
import datetime
import os
from flask import Flask
import threading

TOKEN = os.getenv("7664216240:AAH1iDWhT5JhwpdPd-AnEEkSSwZLD5ZVin0")

# 🌐 Flask (عشان Render)
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is running 🔥"

def run_web():
    app_web.run(host='0.0.0.0', port=10000)

# ❤️ ثابت
def love(msg):
    return msg + "\n\n❤️ بحبك مريم"

# 💌 حب
love_msgs = [
    "💌 أنتِ أجمل شي بحياتي",
    "💌 بدونك الحياة ما إلها طعم",
    "💌 ضحكتك تسوى الدنيا",
    "💌 والله إني بحبك حب مو طبيعي",
    "💌 أنتِ الأمان ❤️"
]

# 🤖 AI بسيط
def ai_reply(text):
    text = text.lower()
    if "كيفك" in text:
        return "تمام دامك معي ❤️"
    elif "بحبك" in text:
        return "وأنا أموت فيك 😏❤️"
    else:
        return "احكي أكثر 😏"

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(love("🔥 أهلاً في بوت الحب 😏"))

# /love
async def love_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(love(random.choice(love_msgs)))

# /joke
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = [
        "😂 واحد فتح محل سماه مغلق دائمًا",
        "😂 واحد شرب قهوة ووجعته عينه طلع في ملعقة"
    ]
    await update.message.reply_text(love(random.choice(jokes)))

# /dice
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(love(f"🎲 {random.randint(1,6)}"))

# 🤖 رد على أي رسالة
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = ai_reply(update.message.text)
    await update.message.reply_text(love(reply))

# تشغيل Flask بالخلفية
threading.Thread(target=run_web).start()

# تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("love", love_cmd))
app.add_handler(CommandHandler("joke", joke))
app.add_handler(CommandHandler("dice", dice))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.run_polling()
