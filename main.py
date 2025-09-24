import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F
import asyncio
import os


BOT_TOKEN = os.getenv("BOT_TOKEN", "8227753790:AAFGqwVXR1OvEeh0LyCveGzkUAcqhRWiHYQ")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# /start komandasi
@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("♻️ Salom! Bu Ecoback – chiqindini to'g'ri tashlab, cashback yutib oling")

# Oddiy xabarni qaytarish
@dp.message(F.text)
async def echo_handler(message: Message):
    await message.answer(f"Siz yozdingiz: {message.text}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
