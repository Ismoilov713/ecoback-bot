from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

8227753790:AAFGqwVXR1OvEeh0LyCveGzkUAcqhRWiHYQ
TOKEN = "SIZNING_TOKENINGIZ"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("♻️ Salom! Bu Ecoback – chiqindini to‘g‘ri tashlab, cashback yutib oling!")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
