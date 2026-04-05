import os
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

games = {}

# 🎨 لوحة
def board_ui(b):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(b[0], callback_data="0"),
         InlineKeyboardButton(b[1], callback_data="1"),
         InlineKeyboardButton(b[2], callback_data="2")],
        [InlineKeyboardButton(b[3], callback_data="3"),
         InlineKeyboardButton(b[4], callback_data="4"),
         InlineKeyboardButton(b[5], callback_data="5")],
        [InlineKeyboardButton(b[6], callback_data="6"),
         InlineKeyboardButton(b[7], callback_data="7"),
         InlineKeyboardButton(b[8], callback_data="8")]
    ])

def win(b):
    c=[(0,1,2),(3,4,5),(6,7,8),
       (0,3,6),(1,4,7),(2,5,8),
       (0,4,8),(2,4,6)]
    for x,y,z in c:
        if b[x]==b[y]==b[z] and b[x]!="⬜":
            return b[x]
    return None

# 🏁 start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 العب مع صاحبك", callback_data="create")]
    ])
    await update.message.reply_text("🎮 لعبة X O", reply_markup=keyboard)

# 📜 help
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - بدء\n"
        "/join CODE - دخول لعبة\n"
        "/help - كل الأوامر"
    )

# 🔗 إنشاء غرفة
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    code = str(uuid.uuid4())[:6]

    games[code] = {
        "p1": query.from_user.id,
        "p2": None,
        "board": ["⬜"]*9,
        "turn": query.from_user.id,
        "active": True
    }

    await query.message.reply_text(
        f"🔥 غرفة جاهزة!\n\n📌 الكود:\n{code}\n\nخلي صاحبك يكتب:\n/join {code}"
    )

# 🔗 دخول
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ اكتب الكود")
        return

    code = context.args[0]

    if code not in games:
        await update.message.reply_text("❌ كود غلط")
        return

    g = games[code]

    if g["p2"]:
        await update.message.reply_text("❌ الغرفة ممتلئة")
        return

    g["p2"] = update.message.from_user.id

    await update.message.reply_text(
        "🔥 بدأت اللعبة!",
        reply_markup=board_ui(g["board"])
    )

# 🎮 اللعب
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user.id

    for code, g in games.items():
        if not g["active"]:
            return

        if user in [g["p1"], g["p2"]]:

            if g["turn"] != user:
                return

            idx = int(query.data)

            if g["board"][idx] != "⬜":
                return

            mark = "❌" if user == g["p1"] else "⭕"
            g["board"][idx] = mark

            # فحص الفوز
            if win(g["board"]):
                g["active"] = False
                await query.message.reply_text(
                    f"🏆 {mark} فاز!",
                    reply_markup=board_ui(g["board"])
                )
                return

            if "⬜" not in g["board"]:
                g["active"] = False
                await query.message.reply_text(
                    "🤝 تعادل",
                    reply_markup=board_ui(g["board"])
                )
                return

            # تبديل الدور
            g["turn"] = g["p2"] if user == g["p1"] else g["p1"]

            await query.message.reply_text(
                "🎮 الدور التالي",
                reply_markup=board_ui(g["board"])
            )
            return

# تشغيل
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("join", join))
app.add_handler(CallbackQueryHandler(create, pattern="create"))
app.add_handler(CallbackQueryHandler(play))

app.run_polling()
