import logging
from aiogram import Bot, Dispatcher, executor, types
import os

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")  # Railway env variable’dan olish
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Salom! Bot ishlayapti ✅")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

