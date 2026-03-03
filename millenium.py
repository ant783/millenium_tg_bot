import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

# ---------------- БАЗОВАЯ НАСТРОЙКА ----------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в .env")

# Создаём экземпляры бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------------- ХЕНДЛЕРЫ ----------------

@dp.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить прокси", callback_data="update_proxies")]
    ])
    text = (
        "👋 Добро пожаловать!\n\n"
        "🔥 3 случайных MTProto прокси\n\n"
        "⚡ Нажми кнопку ниже и получишь результат!"
    )
    await message.answer(text, reply_markup=keyboard)

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Этот бот выдаёт MTProto-прокси.\n"
        "Команды:\n"
        "/start – меню\n"
        "/help – помощь"
    )

# здесь ты просто импортируешь и регистрируешь свои роутеры/хендлеры,
# если они вынесены в другие файлы (например, handlers/proxies.py)
# from handlers.proxies import router as proxies_router
# dp.include_router(proxies_router)

# ---------------- ТОЧКА ВХОДА ----------------

async def main():
    logger.info("🚀 Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

