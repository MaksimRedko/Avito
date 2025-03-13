# main.py
import asyncio
import time
import requests
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, AVITO_URL, MAX_ITEMS, CHECK_INTERVAL, KEYWORDS
from src.avito_parser import fetch_items
from src.db import ItemDB
from src.telegram_bot import start_handler, send_item_notification, router  # Импортируем router
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage # или другой storage
from aiogram import F # импортируем F
import aiosqlite # импортируем aiosqlite

async def get_item_db():
    db = ItemDB(max_items=MAX_ITEMS, keywords=KEYWORDS)
    await db.create_tables() # создаем таблицы
    return db

async def main():
    """Основная функция."""
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage() # хранилище состояний
    dp = Dispatcher(storage=storage)
    session = requests.Session()

    # получаем item_db
    item_db = await get_item_db()

    dp.include_router(router)  # Подключаем router

    # Исправленная регистрация обработчика!
    dp.message.register(start_handler, CommandStart())  # Убрали item_db=...
    dp.startup.register(lambda: print("Бот запущен"))

    # Запускаем поллинг
    asyncio.create_task(dp.start_polling(bot, item_db=item_db))

    #  Получаем первые товары
    new_items_first = fetch_items(AVITO_URL, session)
    if new_items_first:
        for item in new_items_first:
            if await item_db.add_item(item):
                print(f"[{time.strftime('%X')}] Новый товар: {item['name']}")
    else:
        print(f"[{time.strftime('%X')}] Нет новых товаров или ошибка при получении.")

    try:
        while True:
            new_items = fetch_items(AVITO_URL, session)
            if new_items:
                for item in new_items:
                    if await item_db.add_item(item):
                        print(f"[{time.strftime('%X')}] Новый товар: {item['name']}")
                        for chat_id in await item_db.get_all_users():
                            await send_item_notification(bot, chat_id, item)
            else:
                print(f"[{time.strftime('%X')}] Нет новых товаров или ошибка при получении.")

            await asyncio.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("Завершение работы...")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())