import os
import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
DATA_FILE = "players.json"

# تحميل/حفظ
def load():
    try:
        return json.load(open(DATA_FILE))
    except:
        return {}

def save(data):
    json.dump(data, open(DATA_FILE, "w"))

def get_player(uid):
    data = load()
    uid = str(uid)
    if uid not in data:
        data[uid] = {"points": 0}
        save(data)
    return data

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

# فوز
def win(b):
    c = [(0,1,2),(3,4,5),(6,7,8),
         (0,3,6),(1,4,7),(2,5,8),
         (0,4,8),(2,4,6)]
    for x,y,z in c:
        if b[x]==b[y]==b[z] and b[x]!="⬜":
            return b[x]
    return None

# 🧠 Minimax (hard)
def minimax(b, is_max):
    w = win(b)
    if w=="⭕": return 1
    if w=="❌": return -1
    if "⬜" not in b: return 0

    if is_max:
        best=-999
        for i in range(9):
            if b[i]=="⬜":
                b[i]="⭕"
                best=max(best,minimax(b,False))
                b[i]="⬜"
        return best
    else:
        best=999
        for i in range(9):
            if b[i]=="⬜":
                b[i]="❌"
                best=min(best,minimax(b,True))
                b[i]="⬜"
        return best

def best_move(b):
    best=-999
    move=0
    for i in range(9):
        if b[i]=="⬜":
            b[i]="⭕"
            score=minimax(b,False)
            b[i]="⬜"
            if score>best:
                best=score
                move=i
    return move

# 🎮 start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("😏 Easy", callback_data="easy"),
         InlineKeyboardButton("💀 Hard", callback_data="hard")]
    ])
    await update.message.reply_text("🎮 اختر الصعوبة:", reply_markup=keyboard)

# اختيار الصعوبة
async def difficulty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["mode"] = query.data
    board = ["⬜"]*9
    context.user_data["board"]=board

    await query.edit_message_text(
        f"🎮 بدأت اللعبة ({query.data})",
        reply_markup=board_ui(board)
    )

# اللعب
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    b = context.user_data["board"]
    mode = context.user_data["mode"]
    idx = int(query.data)

    if b[idx]!="⬜": return

    b[idx]="❌"

    if win(b):
        data=get_player(query.from_user.id)
        data[str(query.from_user.id)]["points"]+=10
        save(data)
        await query.edit_message_text("🔥 فزت +10 نقاط", reply_markup=board_ui(b))
        return

    if "⬜" not in b:
        await query.edit_message_text("🤝 تعادل", reply_markup=board_ui(b))
        return

    # 🤖 البوت
    if mode=="easy":
        move=random.choice([i for i in range(9) if b[i]=="⬜"])
    else:
        move=best_move(b)

    b[move]="⭕"

    if win(b):
        await query.edit_message_text("💀 خسرت", reply_markup=board_ui(b))
        return

    if "⬜" not in b:
        await query.edit_message_text("🤝 تعادل", reply_markup=board_ui(b))
        return

    await query.edit_message_text("🎮 دورك", reply_markup=board_ui(b))

# 🏆 نقاط
async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data=get_player(update.message.from_user.id)
    pts=data[str(update.message.from_user.id)]["points"]
    await update.message.reply_text(f"🏆 نقاطك: {pts}")

# تشغيل
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("me", me))
app.add_handler(CallbackQueryHandler(difficulty, pattern="^(easy|hard)$"))
app.add_handler(CallbackQueryHandler(play))

app.run_polling()
