from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random
import datetime

TOKEN = "7664216240:AAH1iDWhT5JhwpdPd-AnEEkSSwZLD5ZVin0"
# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 أهلاً في البوت الذكي 😏 اكتب /help")

# /help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """
🤖 الأوامر:

/time ⏰ الوقت
/joke 😂 نكتة
/wisdom 🧠 حكمة
/azkar 🕌 أذكار
/game 🎮 لعبة رقم
"""
    await update.message.reply_text(msg)

# /time
async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now()
    await update.message.reply_text(f"⏰ {now}")

# /joke
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = [
        "😂 واحد غبي فتح محل سماه مغلق دائمًا",
        "😂 واحد راح للدكتور قاله كل ما أشرب قهوة بوجعني عيني قاله شيل الملعقة",
        "😂 واحد اتزوج مدرسه، صار كل يوم عنده امتحان"
    ]
    await update.message.reply_text(random.choice(jokes))

# /wisdom
async def wisdom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wisdoms = [
        "🧠 لا تؤجل عمل اليوم إلى الغد",
        "🧠 من جد وجد ومن زرع حصد",
        "🧠 النجاح يحتاج صبر"
    ]
    await update.message.reply_text(random.choice(wisdoms))

# /azkar
async def azkar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    azkar_list = [
        "🕌 سبحان الله",
        "🕌 الحمد لله",
        "🕌 لا إله إلا الله",
        "🕌 الله أكبر"
    ]
    await update.message.reply_text(random.choice(azkar_list))

# 🎮 لعبة رقم
async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    num = random.randint(1, 10)
    await update.message.reply_text(f"🎮 خمن رقم بين 1 و 10: {num}")

# تشغيل
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("time", time))
app.add_handler(CommandHandler("joke", joke))
app.add_handler(CommandHandler("wisdom", wisdom))
app.add_handler(CommandHandler("azkar", azkar))
app.add_handler(CommandHandler("game", game))

app.run_polling()
