from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update

BOT_TOKEN = "8227753790:AAFGqwVXR1OvEeh0LyCveGzkUAcqhRWiHYQ"

# Foydalanuvchilar ballari uchun xotira (oddiy dictionary, keyin DB ulash mumkin)
user_points = {}

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "♻️ Salom! Bu Ecoback – chiqindini to‘g‘ri tashlab, cashback yutib oling\n\n"
        "📷 QR kodni yuboring – siz ball yig‘asiz.\n"
        "🎁 Ballar yetganda sovg‘a olishingiz mumkin!"
    )

# QR kod yoki matnli kod yuborilganda
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    code = update.message.text.strip()

    # Test uchun faqat 'ECO' bilan boshlangan kodlarni haqiqiy deb hisoblaymiz
    if code.startswith("ECO"):
        # Ball qo‘shamiz
        current_points = user_points.get(user_id, 0) + 10
        user_points[user_id] = current_points
        await update.message.reply_text(
            f"✅ Kod qabul qilindi!\nSizga 10 ball qo‘shildi.\n"
            f"Umumiy ballingiz: {current_points}"
        )
    else:
        await update.message.reply_text("❌ Noto‘g‘ri yoki yaroqsiz kod.")

# Ballar sonini ko‘rsatish
async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    current_points = user_points.get(user_id, 0)
    await update.message.reply_text(f"🎯 Sizning joriy ballaringiz: {current_points}")

# Sovg‘a olish komandasi
async def reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    current_points = user_points.get(user_id, 0)

    if current_points >= 50:
        user_points[user_id] = current_points - 50
        await update.message.reply_text("🎉 Tabriklaymiz! Siz sovg‘a oldingiz! Ballar 50 ga kamaytirildi.")
    else:
        await update.message.reply_text(f"❗ Sovg‘a olish uchun kamida 50 ball kerak. Sizda hozir {current_points} ball bor.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("points", points))
    app.add_handler(CommandHandler("reward", reward))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))

    app.run_polling()

if __name__ == "__main__":
    main()
