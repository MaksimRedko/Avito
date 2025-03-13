import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

def fetch_items(url: str, session: requests.Session) -> Optional[List[Dict[str, str]]]:
    """Получает страницу и парсит товары, используя сессию requests и CSS-селекторы."""
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        items = []
        for item in soup.select('div[data-marker="item"]'):
            cur_item: Dict[str, str] = {}
            cur_item['id'] = item['id']
            cur_item['name'] = item.select_one('h3[itemprop="name"]').get_text(strip=True)
            cur_item['price'] = item.select_one('meta[itemprop="price"]')['content']
            cur_item['url'] = 'https://www.avito.ru' + item.select_one('a[itemprop="url"]')['href']
            cur_item['description'] = item.select_one('meta[itemprop="description"]')['content']
            items.append(cur_item)
        return items
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")  # Логируем, но не прерываем работу
        return None
    except Exception as e:
        print(f"Непредвиденная ошибка при парсинге: {e}")
        return None


def item_contains_keyword(item_name: str, keywords: List[str]) -> bool:
    """Проверяет, содержит ли название товара хотя бы одно из ключевых слов."""
    item_name_lower = item_name.lower()
    return any(keyword.lower() in item_name_lower for keyword in keywords)