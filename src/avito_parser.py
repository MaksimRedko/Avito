import asyncio
import logging
import random
from typing import List
import datetime

import requests
from aiogram import Bot
from playwright.async_api import async_playwright, Page

import config
from src.db import ItemDB
from src.filters import test_item_filter, check_geo
from src.telegram_bot import send_item_notification
from src.utils import create_proxy, is_captcha_present, click_continue, solve_captcha


async def parse_listings(page: Page, item_db: ItemDB, bot: Bot, user_chat_ids: List[int]) -> List[dict]:
    """Парсит объявления, применяет фильтры, сохраняет новые товары и отправляет уведомления."""
    items = []
    item_elements = await page.locator('div[data-marker="item"]').all()
    logging.info(f"Count of item_elements found: {len(item_elements)}")
    print(f"Found {len(item_elements)} item listings. Filtering and displaying...\n")

    for item_element in item_elements:
        try:
            try:
                item_date_locator = item_element.locator("p[data-marker='item-date']")
                item_date_element = await item_date_locator.element_handle(timeout=5000)
                item_date = await item_date_element.inner_text()

            except Exception as e:
                item_date = 'Date not found'

            if item_date != '1 час назад':
                continue

            item_url_locator = item_element.locator('a[itemprop="url"][data-marker="item-title"]')
            # logging.info(f"item_url_locator: {item_url_locator}")
            item_url_element = await item_url_locator.element_handle(timeout=5000)
            item_url = 'https://www.avito.ru' + await item_url_element.get_attribute(
                'href') if item_url_element else "URL not found"

            if not check_geo(item_url):
                continue

            item_name_locator = item_element.locator('h3[itemprop="name"]')
            # logging.info(f"item_name_locator: {item_name_locator}")
            item_name_element = await item_name_locator.element_handle(timeout=5000)
            item_name = await item_name_element.inner_text() if item_name_element else "Name not found"

            item_id = await item_element.get_attribute('data-item-id', timeout=5000)

            item_price_locator = item_element.locator('meta[itemprop="price"]')
            # logging.info(f"item_price_locator: {item_price_locator}")
            item_price_element = await item_price_locator.element_handle(timeout=5000)
            item_price = await item_price_element.get_attribute('content') if item_price_element else "Price not found"

            if int(item_price) < 30000:
                continue

            item_description_locator = item_element.locator('meta[itemprop="description"]')
            # logging.info(f"item_description_locator: {item_description_locator}")
            item_description_element = await item_description_locator.element_handle(timeout=5000)
            item_description = await item_description_element.get_attribute(
                'content') if item_description_element else "Description not found"

            cur_item = {
                'id': item_id,
                'name': item_name,
                'price': item_price,
                'url': item_url,
                'description': item_description,
                'date': item_date,
            }

            if test_item_filter(item_name, item_description):
                is_new_item = await item_db.add_item(cur_item)
                if is_new_item:
                    logging.info(f"New item found and added to DB: {cur_item['id']} - {cur_item['name']}")
                    print(
                        f"[{datetime.time}] ✨ New item found: ({cur_item['date']}) {cur_item['name']}, {cur_item['url']} - Sending Telegram notification...")
                    for chat_id in user_chat_ids:
                        await send_item_notification(bot, chat_id, cur_item)
                    print("✅ Telegram notification sent.\n")
                else:
                    logging.info(f"Item already exists in DB: {cur_item['id']}")
                items.append(cur_item)
            else:
                logging.debug(f"Item did not pass filters: {item_name}")
                print(f"[{datetime.time}] ❌ Item '{item_name}' did not pass filters. {item_url}\n")

        except Exception as parse_item_error:
            logging.error(f"Error parsing item element: {parse_item_error}")
    return items


async def run_parser_with_refresh(url_list: List[str], use_proxy=False, bot=None, item_db=None, user_chat_ids=None,
                                  headless=False):
    """
    Обновляет страницу, парсит объявления и обрабатывает капчу.
    """
    async with async_playwright() as p:
        proxy_list = config.PROXY_LIST
        proxy_index = 0
        url_index = 0

        browser = await p.chromium.launch(headless=headless,ignore_default_args=['--enable-automation'],
                                          args=[
                                              '--disable-blink-features=AutomationControlled',
                                              # Отключаем индикаторы автоматизации
                                              '--no-sandbox',  # Для Docker/Linux, если нужно
                                              '--disable-setuid-sandbox',  # Для Docker/Linux, если нужно
                                              '--disable-dev-shm-usage'  # Для Docker/Linux, если нужно
                                          ])

        while True:
            try:
                # --- Ротация Прокси ---
                proxy_string = proxy_list[proxy_index]
                current_proxy = create_proxy(proxy_string) if use_proxy and proxy_string != "no_proxy" else None

                # ---  Ротация User-Agent ---
                user_agent = random.choice(config.USER_AGENTS)  # Выбираем случайный User-Agent
                context = await browser.new_context(user_agent=user_agent, viewport={'width': 1920, 'height': 1080})  # Создаем НОВЫЙ контекст с новым User-Agent
                page = await context.new_page()  # Создаем НОВУЮ страницу в этом контексте
                # --- Конец ротации User-Agent ---

                proxy_index = (proxy_index + 1) % len(proxy_list)  # % len(proxy_list) обеспечивает цикличность
                url_index = (url_index + 1) % len(url_list)
                url = url_list[url_index]

                proxy_info = current_proxy['server'] if current_proxy else 'No proxy'

                logging.info(
                    f"Navigating to/Refreshing page: {url} using proxy: {proxy_info}, User-Agent: {user_agent}")
                response = await page.goto(url, wait_until='domcontentloaded')

                if await is_captcha_present(page):
                    logging.warning(f"[{datetime.time}] ️ CAPTCHA DETECTED!")

                    # await browser.close()  # Закрываем headless браузер
                    # browser = await p.chromium.launch(
                    #     headless=False)  # Запускаем видимый браузер для ручного решения капчи
                    # context = await browser.new_context(user_agent=user_agent)  # Создаем контекст в видимом браузере
                    # page = await context.new_page()  # Создаем страницу в видимом браузере
                    # await page.goto(url, wait_until='domcontentloaded')  # Переходим по URL еще раз в видимом
                    result, dict = await solve_captcha(page)

                    headers = {  # Заголовки, как в примере запроса (Content-Type, User-Agent, Referer, Origin, X-Cube)
                        'Content-Type': 'application/json',  # Content-Type: application/json - ВАЖНО!
                        'User-Agent': user_agent,  # Используем User-Agent текущей страницы
                        'Referer': page.url,  # Referer - URL страницы с капчей
                        'Origin': 'https://www.avito.ru',  # Origin - домен Avito
                        'X-Cube': await page.evaluate("document.querySelector('#cubeResult')?.innerHTML || ''")
                    }

                    #  Получаем cookies из текущего контекста браузера и добавляем в headers
                    cookies = await page.context.cookies(urls=[page.url])
                    headers['Cookie'] = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

                    time_dict = {
                        'captcha': "",
                        'captcha_id': dict['solution']['captcha_id'],
                        'captcha_output': dict['solution']['captcha_output'],
                        'gen_time': dict['solution']['gen_time'],
                        'hCaptchaResponse':"",
                        'lot_number': dict['solution']['lot_number'],
                        'pass_token': dict['solution']['pass_token'],
                    }
                    if result:
                        print('РЕШИИИИИИИИИИЛИИИИИИИИ')
                        response = requests.post(url='https://www.avito.ru/web/1/firewallCaptcha/verify', json=time_dict, timeout=30)
                        print(response.status_code)
                        if response.status_code == 200:
                            print('ждем перезагрузочку')
                            await asyncio.sleep(random.uniform(3, 10))
                            await page.reload(wait_until='domcontentloaded')
                            items = await parse_listings(page, item_db, bot, user_chat_ids)
                    else:
                        print('Не РЕШИЛИ(((((((((')
                    # input()

                    # print("Continuing after manual CAPTCHA solving.\n")
                    # continue

                # if response and response.status == 429:
                #     logging.warning(f"RECEIVED 429 STATUS CODE! Browser SHOULD REMAIN OPEN.")
                #     print("\n⚠️ 429 Status Code Received! Browser window SHOULD BE OPEN and remain open.")
                elif response and response.status == 200:
                    logging.info(f"Page loaded successfully! Status code: {response.status}. Proceeding with parsing.")
                    print("\n✅ Page loaded successfully (200 OK). Proceeding with PARSED item output...\n")

                    items = await parse_listings(page, item_db, bot, user_chat_ids)

                elif response:
                    logging.warning(
                        f"Page loaded with status code: {response.status} - non 200/429. Browser MAY remain open.")
                    print(f"\n⚠️ Non-200/429 Status Code ({response.status}) Received. Browser window MAY remain open.")
                elif response is None:
                    logging.error(
                        f"Navigation failed, no response received for proxy: {proxy_info}. Browser MAY close or remain open.")
                    print(f"\n❌ Navigation FAILED (None response). Browser window MAY close or remain open.")

            except Exception as main_loop_error:
                logging.error(f"Exception caught in main loop: {main_loop_error}")
                print(f"\n❌ Exception caught in main loop! Error: {main_loop_error}")

            print(f"\n--- Waiting {config.CHECK_INTERVAL} seconds before next refresh ---")
            await context.close()
            await asyncio.sleep(config.CHECK_INTERVAL)

        await browser.close()
