import os
import random
import json
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
DATA_FILE = "players.json"

# تحميل البيانات
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# حفظ البيانات
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# إنشاء لاعب
def get_player(user_id):
    data = load_data()
    uid = str(user_id)

    if uid not in data:
        data[uid] = {
            "points": 0,
            "coins": 0,
            "last_daily": 0
        }
        save_data(data)

    return data

# ليفل
def level(points):
    return points // 20

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 أهلاً في لعبة التحدي!\nاستخدم /play للبدء"
    )

# 🎮 لعب
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    data = get_player(user.id)

    win = random.choice([True, False])

    if win:
        p = random.randint(3, 7)
        c = random.randint(2, 5)
        data[str(user.id)]["points"] += p
        data[str(user.id)]["coins"] += c
        msg = f"🔥 فزت!\n+{p} نقاط\n+{c} عملة"
    else:
        msg = "❌ خسرت!"

    save_data(data)

    pts = data[str(user.id)]["points"]
    lvl = level(pts)

    await update.message.reply_text(
        f"{msg}\n\n💰 نقاط: {pts}\n🪙 عملة: {data[str(user.id)]['coins']}\n⭐ ليفل: {lvl}"
    )

# 🧠 مهمة يومية
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    data = get_player(user.id)

    now = time.time()
    last = data[str(user.id)]["last_daily"]

    if now - last < 86400:
        await update.message.reply_text("❌ رجع بكرا")
        return

    data[str(user.id)]["coins"] += 20
    data[str(user.id)]["last_daily"] = now
    save_data(data)

    await update.message.reply_text("🎁 أخذت 20 عملة!")

# 🎁 صندوق
async def box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    data = get_player(user.id)

    if data[str(user.id)]["coins"] < 10:
        await update.message.reply_text("❌ تحتاج 10 عملات")
        return

    data[str(user.id)]["coins"] -= 10
    reward = random.randint(5, 20)
    data[str(user.id)]["points"] += reward
    save_data(data)

    await update.message.reply_text(
        f"🎁 حصلت على {reward} نقاط!"
    )

# ⚔️ قتال
async def fight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    data = get_player(user.id)

    win = random.choice([True, False])

    if win:
        reward = random.randint(5, 15)
        data[str(user.id)]["points"] += reward
        msg = f"⚔️ فزت!\n+{reward} نقاط"
    else:
        msg = "💀 خسرت القتال!"

    save_data(data)
    await update.message.reply_text(msg)

# 🏪 متجر
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏪 المتجر:\n🎁 صندوق = 10 عملات\nاستخدم /box"
    )

# 👤 معلوماتك
async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    data = get_player(user.id)

    pts = data[str(user.id)]["points"]
    lvl = level(pts)

    await update.message.reply_text(
        f"👤 {user.first_name}\n💰 نقاط: {pts}\n🪙 عملة: {data[str(user.id)]['coins']}\n⭐ ليفل: {lvl}"
    )

# 🏆 ترتيب
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    sorted_players = sorted(
        data.items(), key=lambda x: x[1]["points"], reverse=True
    )

    msg = "🏆 الترتيب:\n"

    for i, (_, info) in enumerate(sorted_players[:5], start=1):
        msg += f"{i}. {info['points']} نقطة\n"

    await update.message.reply_text(msg)

# تشغيل
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("play", play))
app.add_handler(CommandHandler("daily", daily))
app.add_handler(CommandHandler("box", box))
app.add_handler(CommandHandler("fight", fight))
app.add_handler(CommandHandler("shop", shop))
app.add_handler(CommandHandler("me", me))
app.add_handler(CommandHandler("top", top))

app.run_polling()
