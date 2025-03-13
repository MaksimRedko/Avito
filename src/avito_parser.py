import random
import time

import fake_useragent
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


PROXY_LIST = [
    "83.171.240.157:10234:9bYynD86ur:ERNsWJWBfb",
    # "185.42.27.167:12733:PGpXhDnpAF:JyBG5C3DfZ",
]


def fetch_items(url: str, session: requests.Session) -> Optional[List[Dict[str, str]]]:
    try:
        prox_str = random.choice(PROXY_LIST).split(':')
        ip = prox_str[0]
        port = prox_str[1]
        username = prox_str[2]
        password = prox_str[3]

        proxies = {
            "http": f"http://{username}:{password}@{ip}:{port}",
            "https": f"http://{username}:{password}@{ip}:{port}",
        }

        ua = fake_useragent.UserAgent()
        user_agent = ua.random

        session.proxies.update(proxies)
        session.headers.update({'User-Agent': user_agent})

        response = session.get(url=url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        items = []
        for item in soup.select('div[data-marker="item"]'):
            carousel_ancestor_class = item.select_one(class_="iva-item-gallery-nEww5")
            if carousel_ancestor_class:
                print("Объявление пропущено, так как находится в карусели подобрано для вас.")
                continue

            cur_item: Dict[str, str] = {}
            cur_item['id'] = item['id']
            cur_item['url'] = 'https://www.avito.ru' + item.select_one('a[itemprop="url"]')['href']
            cur_item['name'] = item.select_one('h3[itemprop="name"]').get_text(strip=True)
            cur_item['price'] = item.select_one('meta[itemprop="price"]')['content']
            cur_item['description'] = item.select_one('meta[itemprop="description"]')['content']

            if is_spb_geo(cur_item['url'], session=session):
                items.append(cur_item)
            else:
                continue

        return items
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return None
    except Exception as e:
        print(f"Непредвиденная ошибка при парсинге: {e}")
        return None


def item_contains_keyword(item_name: str, keywords: List[str]) -> bool:
    item_name_lower = item_name.lower()
    return any(keyword.lower() in item_name_lower for keyword in keywords)


def is_spb_geo(url, session: requests.Session):
    time.sleep(random.uniform(0.5, 5))
    cur_req = session.get(url=url)
    soup_geo = BeautifulSoup(cur_req.text, 'html.parser')
    geo_elements = soup_geo.select_one('div[itemprop="address"]')
    if geo_elements:
        address_span = None
        for span in geo_elements.find_all('span'):
            classes = span.get('class', [])
            for class_name in classes:
                if class_name.startswith('style-item-address__string-'):
                    address_span = span
                    break
            if address_span:
                break
        if 'Санкт-Петербург' in address_span.text:
            return True
    return False