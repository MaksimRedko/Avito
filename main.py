import asyncio
import logging
import config

from src.avito_parser import run_parser_with_refresh
# --- Imports from other files ---
from src.telegram_bot import router, send_rerun_notification  # Импорт функций Telegram бота и роутера
from src.db import ItemDB  # Импорт класса ItemDB
from aiogram import Bot, Dispatcher  # Импорт Bot и Dispatcher из aiogram

# --- End of imports ---

logging.basicConfig(level=logging.INFO)


async def main():
    # --- Initialize Telegram Bot ---
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    bot_task = asyncio.create_task(dp.start_polling(bot))  # Запускаем бота как фоновую задачу
    # --- End of Telegram Bot Initialization ---

    # --- Initialize ItemDB ---
    item_db = ItemDB(max_items=config.MAX_ITEMS, keywords=config.KEYWORDS)
    await item_db.create_tables()
    user_chat_ids = await item_db.get_all_users()
    # --- End of ItemDB Initialization ---


    for chat_id in user_chat_ids:
        await send_rerun_notification(bot=bot, chat_id=chat_id)

    test_url = [config.AVITO_URL_IPAD, config.AVITO_URL_MACBOOK]
    parser_task = asyncio.create_task(run_parser_with_refresh(test_url, use_proxy=True, bot=bot, item_db=item_db,
                                                              user_chat_ids=user_chat_ids, headless=False))  # Запускаем парсер как фоновую задачу

    await asyncio.gather(parser_task,
                         bot_task)  # Запускаем обе задачи конкурентно и ждем завершения обеих (хотя они бесконечные)


if __name__ == "__main__":
    asyncio.run(main())
