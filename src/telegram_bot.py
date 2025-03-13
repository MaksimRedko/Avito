# telegram_bot.py
from aiogram import Bot, types, Router, F
from typing import Dict
from aiogram.filters import CommandStart
from src.db import ItemDB
from aiogram.fsm.context import FSMContext # понадобится для работы с состояниями (если будете использовать)
from aiogram.fsm.storage.memory import MemoryStorage # или другой storage
from aiogram.types import Message

router = Router()

async def send_item_notification(bot: Bot, chat_id: int, item: Dict[str, str]):
    """Отправляет уведомление о новом товаре в Telegram."""
    message = (
        f"🔥 Новый товар на Avito!\n\n"
        f"Название: {item['name']}\n"
        f"Цена: {item['price']} руб.\n"
        f"Описание: {item['description']}\n"
        f"Ссылка: {item['url']}"
    )
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")


@router.message(CommandStart())  # Декоратор для роутера
async def start_handler(message: types.Message, item_db: ItemDB):
    """Обработчик команды /start."""
    await item_db.add_user(message.chat.id)
    await message.answer("Привет! Теперь ты будешь получать уведомления о новых товарах с Avito.")