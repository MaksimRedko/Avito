from typing import List

import config


def item_contains_keyword(item_name: str, item_description: str, keywords: List[str]) -> bool:
    """Проверяет наличие ключевых слов в названии и описании. Возвращает True если содержит"""
    combined_text_lower = (item_name + " " + item_description).lower().replace(" ", "")
    combined_text_lower = combined_text_lower.replace("c", "с").replace("a", "а").replace("o", "о").replace("p", "р")
    for keyword in keywords:
        keyword_lower = keyword.lower().replace(" ", "")
        keyword_lower = keyword_lower.replace("c", "с").replace("a", "а").replace("o", "о").replace("p", "р")
        if keyword_lower in combined_text_lower:
            return True
    return False


def item_contains_negative_keyword(item_name: str, item_description: str, negative_keywords: List[str]) -> bool:
    """Проверяет наличие запрещенных слов в названии и описании. Возвращает True если содержит"""
    item_name_lower = item_name.lower()
    item_description_lower = item_description.lower()
    item_name_lower = item_name_lower.replace(" ", "")
    item_description_lower = item_description_lower.replace(" ", "")
    for keyword in negative_keywords:
        keyword_lower = keyword.lower().replace(" ", "")
        if keyword_lower in item_name_lower or keyword_lower in item_description_lower:
            return True
    return False


def test_item_filter(item_name: str, item_description: str) -> bool:
    """Проверяет описание и название товара на наличие ключевых слов и запрещенных слов. Возращает True если товар проходит все фильтры"""
    if not item_contains_keyword(item_name, item_description, config.KEYWORDS):
        return False
    if item_contains_negative_keyword(item_name, item_description, config.NEGATIVE_KEYWORDS):
        return False
    return True


def check_geo(url: str) -> bool:
    split_url = url.split('/')
    if 'sankt-peterburg' in split_url:
        return True
    return False
