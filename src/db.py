# --- START OF FILE db.py ---
# db.py
from collections import deque
from typing import List, Dict, Deque, Set
import aiosqlite  # Используем aiosqlite


class ItemDB:
    def __init__(self, max_items: int, keywords: List[str], db_file: str = "avito_data.db"):
        self.items_deque: Deque[Dict[str, str]] = deque(maxlen=max_items)
        self.items_set: Set[str] = set()
        self.keywords = keywords
        self.max_items = max_items
        self.db_file = db_file

    async def create_tables(self):
        """Создает таблицы в базе данных, если они не существуют."""
        async with aiosqlite.connect(self.db_file) as db:  # Используем асинхронный контекстный менеджер
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY
                )
            """)
            await db.commit()

    async def add_user(self, chat_id: int) -> None:
        """Добавляет пользователя (chat_id) в базу данных."""
        async with aiosqlite.connect(self.db_file) as db:
            try:
                await db.execute("INSERT INTO users (chat_id) VALUES (?)", (chat_id,))
                await db.commit()  # Обязательно делаем commit
            except aiosqlite.IntegrityError:
                pass

    async def get_all_users(self) -> List[int]:
        """Возвращает список chat_id всех пользователей."""
        async with aiosqlite.connect(self.db_file) as db:
            async with db.execute("SELECT chat_id FROM users") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def add_item(self, item: Dict[str, str]) -> bool:
        """Добавляет элемент в deque и set, с проверкой дубликатов и фильтрацией."""
        if item['id'] not in self.items_set:
            self.items_deque.append(item)
            self.items_set.add(item['id'])
            return True
        return False

    def get_all_items(self) -> List[Dict[str, str]]:
        return list(self.items_deque)

    async def close(self):
      pass # aiosqlite сам закрывает соединение
# --- END OF FILE db.py ---