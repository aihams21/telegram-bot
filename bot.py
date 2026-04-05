import os
import uuid
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

games = {}
user_game = {}

# ===== XO UI =====
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

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌⭕ XO", callback_data="create_xo")],
        [InlineKeyboardButton("🎯 تخمين الرقم", callback_data="create_guess")]
    ])
    await update.message.reply_text("🎮 اختر لعبة", reply_markup=keyboard)

# ===== CREATE XO =====
async def create_xo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    code = str(uuid.uuid4())[:5]

    games[code] = {
        "game": "xo",
        "p1": query.from_user.id,
        "p2": None,
        "board": ["⬜"]*9,
        "turn": query.from_user.id,
        "msg1": None,
        "msg2": None,
        "active": True
    }

    user_game[query.from_user.id] = code

    await query.message.reply_text(f"🔥 كود: {code}\n/join {code}")

# ===== CREATE GUESS =====
async def create_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    code = str(uuid.uuid4())[:5]

    games[code] = {
        "game": "guess",
        "p1": query.from_user.id,
        "p2": None,
        "number": random.randint(1, 20),
        "guesses": {},
        "active": True
    }

    user_game[query.from_user.id] = code

    await query.message.reply_text(f"🔥 كود: {code}\n/join {code}")

# ===== JOIN =====
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

    if g["game"] == "xo":
        m1 = await context.bot.send_message(g["p1"], "🎮 بدأت XO", reply_markup=board_ui(g["board"]))
        m2 = await context.bot.send_message(g["p2"], "🎮 بدأت XO", reply_markup=board_ui(g["board"]))

        g["msg1"] = m1.message_id
        g["msg2"] = m2.message_id

    elif g["game"] == "guess":
        await context.bot.send_message(g["p1"], "🎯 خمن رقم من 1-20")
        await context.bot.send_message(g["p2"], "🎯 خمن رقم من 1-20")

# ===== PLAY XO =====
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user.id

    if user not in user_game:
        return

    code = user_game[user]
    g = games[code]

    if g["game"] != "xo":
        return

    if not g["active"] or g["turn"] != user:
        return

    idx = int(query.data)

    if g["board"][idx] != "⬜":
        return

    mark = "❌" if user == g["p1"] else "⭕"
    g["board"][idx] = mark

    winner = win(g["board"])

    await context.bot.edit_message_reply_markup(g["p1"], g["msg1"], reply_markup=board_ui(g["board"]))
    await context.bot.edit_message_reply_markup(g["p2"], g["msg2"], reply_markup=board_ui(g["board"]))

    if winner or "⬜" not in g["board"]:
        g["active"] = False

        text = f"🏆 {mark} فاز!" if winner else "🤝 تعادل"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 نعم", callback_data="again")],
            [InlineKeyboardButton("❌ لا", callback_data="no")]
        ])

        await context.bot.send_message(g["p1"], text)
        await context.bot.send_message(g["p2"], text)

        await context.bot.send_message(g["p1"], "تلعب مرة ثانية؟", reply_markup=keyboard)
        await context.bot.send_message(g["p2"], "تلعب مرة ثانية؟", reply_markup=keyboard)

        return

    g["turn"] = g["p2"] if user == g["p1"] else g["p1"]

# ===== GUESS GAME =====
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id

    if user not in user_game:
        return

    code = user_game[user]
    g = games[code]

    if g["game"] == "guess":
        try:
            guess = int(update.message.text)
        except:
            return

        g["guesses"][user] = guess

        if len(g["guesses"]) == 2:
            n = g["number"]
            p1 = g["p1"]
            p2 = g["p2"]

            d1 = abs(g["guesses"][p1] - n)
            d2 = abs(g["guesses"][p2] - n)

            if d1 < d2:
                winner = p1
            elif d2 < d1:
                winner = p2
            else:
                winner = None

            text = "🤝 تعادل" if winner is None else f"🏆 الفائز هو {winner}"

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 نعم", callback_data="again")],
                [InlineKeyboardButton("❌ لا", callback_data="no")]
            ])

            await context.bot.send_message(p1, text)
            await context.bot.send_message(p2, text)

            await context.bot.send_message(p1, "تلعب مرة ثانية؟", reply_markup=keyboard)
            await context.bot.send_message(p2, "تلعب مرة ثانية؟", reply_markup=keyboard)

            g["active"] = False

        return

# ===== AGAIN =====
async def again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user.id

    if user not in user_game:
        return

    code = user_game[user]
    g = games[code]

    if g["game"] == "xo":
        g["board"] = ["⬜"]*9
        g["turn"] = g["p1"]
        g["active"] = True

        m1 = await context.bot.send_message(g["p1"], "🔄 XO جديدة", reply_markup=board_ui(g["board"]))
        m2 = await context.bot.send_message(g["p2"], "🔄 XO جديدة", reply_markup=board_ui(g["board"]))

        g["msg1"] = m1.message_id
        g["msg2"] = m2.message_id

    elif g["game"] == "guess":
        g["number"] = random.randint(1, 20)
        g["guesses"] = {}
        g["active"] = True

        await context.bot.send_message(g["p1"], "🎯 رقم جديد! خمن")
        await context.bot.send_message(g["p2"], "🎯 رقم جديد! خمن")

# ===== NO =====
async def no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("👍 تمام")

# ===== RUN =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("join", join))
app.add_handler(CallbackQueryHandler(create_xo, pattern="create_xo"))
app.add_handler(CallbackQueryHandler(create_guess, pattern="create_guess"))
app.add_handler(CallbackQueryHandler(play))
app.add_handler(CallbackQueryHandler(again, pattern="again"))
app.add_handler(CallbackQueryHandler(no, pattern="no"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.run_polling()
