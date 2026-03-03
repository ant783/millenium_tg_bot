import asyncio
import random
import re
import aiohttp
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

# ---------------- БАЗОВАЯ НАСТРОЙКА ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------------- ФУНКЦИИ ЗАГРУЗКИ ПРОКСИ ----------------
PROXY_URLS = [
    'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt',
    'https://raw.githubusercontent.com/Argh94/Proxy-List/refs/heads/main/MTProto.txt',
    'https://mtpro.xyz/',
    'https://mtpro.xyz/mtproto-ru'
]

async def fetch_proxies():
    """Загружает прокси из всех источников"""
    all_proxies = []
    
    for url in PROXY_URLS:
        try:
            if 'raw.githubusercontent.com' in url:
                # GitHub txt файлы
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        if resp.status == 200:
                            content = await resp.text()
                            proxies = [line.strip() for line in content.splitlines() if line.strip()]
                            all_proxies.extend(proxies)
                            logger.info(f"✅ {url}: {len(proxies)} прокси")
            else:
                # HTML сайты
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        if resp.status == 200:
                            html = await resp.text()
                            proxy_links = re.findall(r'(?:https://t\.me/proxy\?[^"\s]+|tg://proxy\?[^"\s]+)', html)
                            clean_proxies = [link.strip('"\'').rstrip() for link in proxy_links 
                                           if link.strip('"\'').rstrip().startswith(('https://t.me/proxy?', 'tg://proxy?'))]
                            all_proxies.extend(clean_proxies)
                            logger.info(f"✅ {url}: {len(clean_proxies)} прокси")
        except Exception as e:
            logger.error(f"❌ {url}: {e}")
    
    # Удаляем дубликаты
    unique_proxies = list(set(all_proxies))
    logger.info(f"🎉 Всего уникальных прокси: {len(unique_proxies)}")
    return unique_proxies

# ---------------- ХЕНДЛЕРЫ ----------------
@dp.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить прокси", callback_data="update_proxies")]
    ])
    text = """👋 Добро пожаловать!

🔥 3 случайных MTProto прокси

⚡ Нажмите кнопку ниже и получишь результат!"""
    await message.answer(text, reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "update_proxies")
async def update_proxies_handler(callback: CallbackQuery):
    await callback.message.edit_text("⏳ Загружаем свежие прокси...")
    
    proxies = await fetch_proxies()
    if not proxies:
        await callback.message.edit_text("❌ Прокси временно недоступны. Попробуйте позже.")
        await callback.answer()
        return
    
    available_count = min(len(proxies), 3)
    selected = random.sample(proxies, available_count)
    
    keyboard_rows = []
    for proxy in selected:
        keyboard_rows.append([InlineKeyboardButton(text="connect", url=proxy)])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    
    # ✅ ПРОСТОЙ ТЕКСТ БЕЗ MarkdownV2
    text = f"""🔥 {available_count} случайных MTProto прокси:

"""
    for i, proxy in enumerate(selected, 1):
        short_link = proxy[:60] + "..." if len(proxy) > 60 else proxy
        text += f"{i}. {short_link}\n\n"
    
    text += "👇 Кнопка connect после каждого прокси!"
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer("✅ Готово!")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    text = """Этот бот выдаёт MTProto-прокси.
Команды:
/start – меню
/help – помощь"""
    await message.answer(text)

# ---------------- ЗАПУСК ----------------
async def main():
    logger.info("🚀 Бот запущен")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
