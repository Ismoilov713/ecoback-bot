import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import csv
import os

# 🔑 Admin ID (sizning ID'ingiz)
MY_ID = 5010840702  

# Ballar fayli
USERS_FILE = "users.csv"

# Mahsulot kodlari fayli
CODES_FILE = "codes.csv"

# Chiqindi idish kodlari fayli
BINS_FILE = "bins.csv"

# Foydalanuvchilar ballarini yuklash
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        return {rows[0]: int(rows[1]) for rows in reader}

# Foydalanuvchilar ballarini saqlash
def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for user_id, points in users.items():
            writer.writerow([user_id, points])

# Kodlarni yuklash
def load_codes(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["kod"]: row["status"] for row in reader}

# Kodlarni saqlash
def save_codes(file, codes):
    with open(file, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["kod", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for kod, status in codes.items():
            writer.writerow({"kod": kod, "status": status})

# 🔔 Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("♻️ Salom! EcoBack botiga xush kelibsiz!\n\n"
                                    "🎁 Mahsulot kodingizni yuboring.\n"
                                    "🗑 Keyin chiqindi idishidagi kodni yuboring.\n"
                                    "✅ Shunda ball qo‘shiladi!")

# 🔑 Kodlarni qayta ishlash
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.strip()

    users = load_users()
    codes = load_codes(CODES_FILE)
    bins = load_codes(BINS_FILE)

    # 1️⃣ Mahsulot kodi tekshirish
    if text in codes:
        if codes[text] == "unused":
            context.user_data["pending_product"] = text
            await update.message.reply_text("🗑 Endi chiqindi idishidagi kodni yuboring.")
        else:
            await update.message.reply_text("⚠️ Bu mahsulot kodi allaqachon ishlatilgan.")
        return

    # 2️⃣ Chiqindi idish kodi tekshirish
    if text in bins:
        if "pending_product" in context.user_data:
            product_code = context.user_data.pop("pending_product")
            codes[product_code] = "used"
            save_codes(CODES_FILE, codes)

            users[user_id] = users.get(user_id, 0) + 1
            save_users(users)

            await update.message.reply_text(f"✅ Ball qo‘shildi! Sizning balansingiz: {users[user_id]} ball.")

            # 🔔 Admin uchun reminder
            if users[user_id] >= 10:
                await context.bot.send_message(
                    chat_id=MY_ID,
                    text=f"⚡ Foydalanuvchi {user_id} 10+ ball yig‘di!"
                )
        else:
            await update.message.reply_text("⚠️ Avval mahsulot kodini yuboring.")
        return

    await update.message.reply_text("❌ Noto‘g‘ri kod.")

# 🔥 Botni ishga tushirish
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))

    app.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
