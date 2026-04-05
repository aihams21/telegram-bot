import os
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

games = {}
user_game = {}

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
    combos=[(0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)]
    for x,y,z in combos:
        if b[x]==b[y]==b[z] and b[x]!="⬜":
            return b[x]
    return None

# start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 لعب مع صاحبك", callback_data="create")]
    ])
    await update.message.reply_text("🎮 X O", reply_markup=keyboard)

# create room
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    code = str(uuid.uuid4())[:5]

    games[code] = {
        "p1": query.from_user.id,
        "p2": None,
        "board": ["⬜"]*9,
        "turn": query.from_user.id,
        "msg1": None,
        "msg2": None,
        "active": True
    }

    user_game[query.from_user.id] = code

    await query.message.reply_text(
        f"🔥 كود الغرفة: {code}\n\nخلي صاحبك يكتب:\n/join {code}"
    )

# join
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
    user_game[g["p2"]] = code

    # إرسال لوحة للطرفين وتخزين message_id
    m1 = await context.bot.send_message(
        chat_id=g["p1"],
        text="🎮 بدأت اللعبة",
        reply_markup=board_ui(g["board"])
    )

    m2 = await context.bot.send_message(
        chat_id=g["p2"],
        text="🎮 بدأت اللعبة",
        reply_markup=board_ui(g["board"])
    )

    g["msg1"] = m1.message_id
    g["msg2"] = m2.message_id

# اللعب
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user.id

    if user not in user_game:
        return

    code = user_game[user]
    g = games[code]

    if not g["active"]:
        return

    if g["turn"] != user:
        return

    idx = int(query.data)

    if g["board"][idx] != "⬜":
        return

    mark = "❌" if user == g["p1"] else "⭕"
    g["board"][idx] = mark

    winner = win(g["board"])

    # تحديث اللوحتين
    await context.bot.edit_message_reply_markup(
        chat_id=g["p1"], message_id=g["msg1"], reply_markup=board_ui(g["board"])
    )
    await context.bot.edit_message_reply_markup(
        chat_id=g["p2"], message_id=g["msg2"], reply_markup=board_ui(g["board"])
    )

    if winner:
        g["active"] = False
        await context.bot.send_message(g["p1"], f"🏆 {mark} فاز!")
        await context.bot.send_message(g["p2"], f"🏆 {mark} فاز!")
        return

    if "⬜" not in g["board"]:
        g["active"] = False
        await context.bot.send_message(g["p1"], "🤝 تعادل")
        await context.bot.send_message(g["p2"], "🤝 تعادل")
        return

    g["turn"] = g["p2"] if user == g["p1"] else g["p1"]

# 💬 chat داخل الغرفة
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id

    if user not in user_game:
        return

    code = user_game[user]
    g = games[code]

    other = g["p2"] if user == g["p1"] else g["p1"]

    await context.bot.send_message(
        chat_id=other,
        text=f"💬 {update.message.text}"
    )

# 🚪 خروج
async def exit_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id

    if user not in user_game:
        return

    code = user_game[user]
    g = games[code]

    g["active"] = False

    await context.bot.send_message(g["p1"], "🚪 انتهت اللعبة")
    await context.bot.send_message(g["p2"], "🚪 انتهت اللعبة")

# تشغيل
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("join", join))
app.add_handler(CommandHandler("exit", exit_game))
app.add_handler(CallbackQueryHandler(create, pattern="create"))
app.add_handler(CallbackQueryHandler(play))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.run_polling()
