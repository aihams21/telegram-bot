import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
# إنشاء لوحة اللعب
def create_board(board):
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            text = board[i*3 + j]
            row.append(InlineKeyboardButton(text, callback_data=str(i*3+j)))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

# فحص الفوز
def check_win(b):
    combos = [(0,1,2),(3,4,5),(6,7,8),
              (0,3,6),(1,4,7),(2,5,8),
              (0,4,8),(2,4,6)]
    for x,y,z in combos:
        if b[x] == b[y] == b[z] and b[x] != " ":
            return b[x]
    return None

# بدء اللعبة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    board = [" "]*9
    context.user_data["board"] = board
    await update.message.reply_text(
        "🎮 لعبة X O\nاختار مكانك:",
        reply_markup=create_board(board)
    )

# الضغط على زر
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    board = context.user_data.get("board", [" "]*9)
    idx = int(query.data)

    if board[idx] != " ":
        return

    # اللاعب X
    board[idx] = "❌"

    winner = check_win(board)
    if winner:
        await query.edit_message_text("🔥 فزت!", reply_markup=create_board(board))
        return

    # دور البوت O
    for i in range(9):
        if board[i] == " ":
            board[i] = "⭕"
            break

    winner = check_win(board)
    if winner:
        await query.edit_message_text("💀 البوت فاز!", reply_markup=create_board(board))
        return

    await query.edit_message_text(
        "🎮 دورك:",
        reply_markup=create_board(board)
    )

# تشغيل
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
