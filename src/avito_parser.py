import asyncio
import logging
import random
from typing import List
import datetime

from aiogram import Bot
from playwright.async_api import async_playwright, Page

import config
from src.db import ItemDB
from src.filters import test_item_filter, check_geo
from src.telegram_bot import send_item_notification
from src.utils import create_proxy, is_captcha_present, handle_avito_ip_captcha


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


async def run_parser_with_refresh(url_list: List[str], use_proxy=False, bot=None, item_db=None, user_chat_ids=None):
    """
    Обновляет страницу, парсит объявления и обрабатывает капчу.
    """
    async with async_playwright() as p:
        proxy_list = config.PROXY_LIST
        proxy_index = 0
        url_index = 0

        browser = await p.chromium.launch(headless=False)

        while True:
            try:
                # --- Ротация Прокси ---
                proxy_string = proxy_list[proxy_index]
                current_proxy = create_proxy(proxy_string) if use_proxy and proxy_string != "no_proxy" else None

                # ---  Ротация User-Agent ---
                user_agent = random.choice(config.USER_AGENTS)  # Выбираем случайный User-Agent
                context = await browser.new_context(user_agent=user_agent)  # Создаем НОВЫЙ контекст с новым User-Agent
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
                    logging.warning(f"[{datetime.time}] CAPTCHA DETECTED! Script paused, waiting for manual solving.")
                    print(
                        "\n ⚠️ CAPTCHA DETECTED! Please solve the CAPTCHA in the browser window and press Enter to continue...")

                    await  asyncio.sleep(10)
                    response = await page.goto(url, wait_until='domcontentloaded')
                    # await browser.close()  # Закрываем headless браузер
                    # browser = await p.chromium.launch(headless=False)  # Запускаем видимый браузер для ручного решения капчи
                    # context = await browser.new_context(user_agent=user_agent)  # Создаем контекст в видимом браузере
                    # page = await context.new_page()  # Создаем страницу в видимом браузере
                    # await page.goto(url, wait_until='domcontentloaded')  # Переходим по URL еще раз в видимом
                    # ---  Handle "IP problem" captcha page first ---
                    if await handle_avito_ip_captcha(page):  # Вызываем новую функцию
                        # If handle_avito_ip_captcha returns True, it means "Continue" button was clicked
                        # and we should re-check for captcha presence AFTER clicking "Continue"
                        if await is_captcha_present(page):  # Check again AFTER clicking "Continue"
                            logging.info(
                                "Captcha still present after 'Продолжить' button. Proceeding to solve visual captcha.")
                            print(
                                "ℹ️ Captcha still present after 'Продолжить' button. Proceeding to solve visual captcha.")
                            # ---  Here you would add your code to solve the visual captcha (e.g., using 2Captcha or manual solving) ---
                            # ... (rest of your captcha solving logic - 2Captcha or manual) ...
                        else:
                            logging.info(
                                "'IP problem' page handled, no further captcha detected immediately. Continuing parsing.")
                            print(
                                "✅ 'IP problem' page handled, no further captcha detected immediately. Continuing parsing.")
                            continue  # Continue parsing if no further captcha immediately after "Продолжить"

                    # await browser.close()  # Закрываем видимый браузер после решения капчи
                    # browser = await p.chromium.launch(headless=True)  # Возвращаемся к headless режиму
                    print("Continuing after manual CAPTCHA solving.\n")
                    continue

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
