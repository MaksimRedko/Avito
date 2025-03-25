import asyncio
import logging
import random
import re
import time
import urllib
import requests, httpx

from playwright.async_api import Page, BrowserContext
from config import API_KEY, CREATE_TASK_URL, GET_TASK_RESULT_URL


def create_proxy(proxy_string):
    """Создает прокси из строки, взятой из PROXY_LIST"""
    if proxy_string == "no_proxy":
        return None
    if ":" not in proxy_string:
        return None
    prox_str = proxy_string.split(':')
    ip = prox_str[0]
    port = prox_str[1]
    username = prox_str[2]
    password = prox_str[3]
    proxy = {
        "server": f"http://{ip}:{port}",
        "username": username,
        "password": password,
    }
    return proxy


async def is_captcha_present(page: Page) -> bool:
    """Проверяет, присутствует ли капча на странице."""

    # Проверяем заголовок страницы (на русском и английском, на всякий случай)
    captcha_title_ru = "Доступ ограничен: проблема с IP"
    captcha_title_en = "Access Denied: IP problem"  # или что-то подобное, если сайт на английском
    page_title = await page.title()
    if captcha_title_ru in page_title or captcha_title_en in page_title:
        logging.warning(f"Detected CAPTCHA by page title: {page_title}")
        return True

    # Проверяем наличие контейнера firewall-container (общий контейнер капчи на Авито)
    firewall_container = page.locator('.firewall-container')
    if await firewall_container.is_visible():
        logging.warning("Detected CAPTCHA by firewall-container")
        return True

    # Проверяем наличие hCaptcha (если Авито использует hCaptcha)
    hcaptcha_element = page.locator('#h-captcha')
    if await hcaptcha_element.is_visible():
        logging.warning("Detected hCaptcha element")
        return True

    # Проверяем наличие внутренней капчи (inner-captcha, если это собственная разработка Авито)
    inner_captcha_element = page.locator('#inner-captcha')
    if await inner_captcha_element.is_visible():
        logging.warning("Detected inner-captcha element")
        return True

    # Проверяем наличие GeeTest капчи (если Авито использует GeeTest)
    geetest_captcha_element = page.locator('#geetest_captcha')
    if await geetest_captcha_element.is_visible():
        logging.warning("Detected GeeTest captcha element")
        return True

    # Дополнительная проверка на общий селектор .captcha (если он все еще актуален)
    generic_captcha_element = page.locator('.captcha')
    if await generic_captcha_element.is_visible():
        logging.warning("Detected generic captcha element (.captcha)")
        return True

    return False  # Капча не обнаружена


async def click_continue(page: Page) -> bool:
    """
    Нажимает кнопку "Продолжить", чтобы перейти к решению капчи.
    Возвращает True, если кнопка была нажата и дальнейшая капча ожидается, False в противном случае.
    """
    try:
        continue_button = page.locator('button', has_text="Продолжить")  # Ищем кнопку с текстом "Продолжить"
        if await continue_button.is_visible():
            await continue_button.click()
            await asyncio.sleep(random.uniform(3, 5))
            # logging.info("Clicked 'Продолжить' button. Waiting for next captcha...")
            print("✅ Clicked 'Продолжить' button. Waiting for next captcha...")
            if page.locator('geetest_text_tips', has_text='Переместите слайдером деталь, чтобы сложить пазл'):
                print('RETURN TRUE')
                return True

    except Exception as e:
        # logging.error(f"Error handling 'IP problem' captcha: {e}")
        print(f"❌ Error handling 'IP problem' captcha: {e}")
        print('RETURN FALSE')
        return False  # Ошибка при обработке


async def solve_captcha(page: Page):
    if await click_continue(page):
        print('Клик получен')
        updated_html_content = await page.content()
        captcha_id = await extract_geetest_params_from_html(updated_html_content)
        task = await create_geetest_v4_task(website_url=page.url, captcha_id=captcha_id)
        print(task)
        task_result = await get_task_result(task_id=task['taskId'])
        print(task_result)
        return verify_geetest_solution_via_get(geetest_solution=task_result,), task_result

    return False


async def extract_geetest_params_from_html(
        html_content: str) -> dict or None:  # Функция теперь принимает HTML контент как аргумент
    """Извлекает gt и challenge параметры GeeTest из HTML контента."""
    try:
        # ---  Теперь работаем с ПЕРЕДАННЫМ html_content, а не с page ---
        # logging.info("Trying to extract GeeTest parameters using Playwright locator... (Regex method only now)")
        print("ℹ️ Trying to extract GeeTest parameters using Playwright locator... (Regex method only now)")

        captcha_id = extract_geetest_v4_params(html_content)  # Вызываем regex функцию на HTML контенте
        if captcha_id is not None:
            # logging.info(f"Extracted GeeTest gt (regex): {captcha_id['gt']}")
            print(f"✅ Extracted GeeTest gt (regex): {captcha_id}")
            return captcha_id
        else:
            # logging.warning("Regex method failed to extract GeeTest parameters.")
            print("⚠️ Regex method failed to extract GeeTest parameters.")
            return None


    except Exception as extraction_error:
        # logging.warning(f"Extraction method failed to extract GeeTest parameters: {extraction_error}")
        print(f"⚠️ Extraction method failed to extract GeeTest parameters: {extraction_error}")
        return None


def extract_geetest_v4_params(html):
    match = re.search(r'captcha_id=([a-f0-9]{32})', html)
    if match:
        return match.group(1)
    match = re.search(r'captcha_id=([^&"\']+)', html)
    if match:
        captcha_id_raw = match.group(1)
        captcha_id = captcha_id_raw.split("<")[0]
        return captcha_id.strip()
    print(f"❌ Error during regex extraction of GeeTest parameters:")
    return None


async def create_geetest_v4_task(website_url, captcha_id, proxyless=True, proxy_details=None):
    """
    Создает задачу для GeeTest V4 через 2Captcha API.
    Обязательные параметры: websiteURL, версия (4) и initParameters с captcha_id.
    """
    task_type = "GeeTestTaskProxyless" if proxyless else "GeeTestTask"
    task = {
        "type": task_type,
        "websiteURL": website_url,
        "version": 4,
        "initParameters": {
            "captcha_id": captcha_id
        }
    }
    if not proxyless and proxy_details:
        task.update(proxy_details)
    payload = {
        "clientKey": API_KEY,
        "task": task
    }
    response = requests.post(CREATE_TASK_URL, json=payload)
    return response.json()


async def get_task_result(task_id, retry_interval=5, max_retries=20):
    """
    Опрашивает 2Captcha API до получения результата.
    """
    payload = {
        "clientKey": API_KEY,
        "taskId": task_id
    }
    for i in range(max_retries):
        response = requests.post(GET_TASK_RESULT_URL, json=payload)
        result = response.json()
        if result.get("status") == "processing":
            print(f"Капча ещё не решена, ждем... {i + 1}")
            time.sleep(retry_interval)
        else:
            return result
    return {"errorId": 1, "errorDescription": "Timeout waiting for solution."}


async def verify_geetest_solution_via_get(geetest_solution: dict) -> bool:
    """
    Отправляет GET запрос на gcaptcha4.geetest.com/verify для верификации решения капчи.

    """

    verify_url = "https://gcaptcha4.geetest.com/verify"

    params = {  # Собираем query parameters для GET запроса
        'callback': f'{geetest_solution['solution']['gen_time']}',  # Динамический callback, можно генерировать timestamp
        'captcha_id': geetest_solution['solution']['captcha_id'],  # gt (website ID)
        'client_type': 'web',
        'lot_number': geetest_solution['solution']['lot_number'],
        'payload': geetest_solution['solution']['captcha_output'],
        'process_token': geetest_solution['solution']['pass_token'],
        'payload_protocol': 1,
        'pt': 1,
        # 'w': '',
        # **Используем 'w' из решения, если есть, иначе пустая строка**
    }
    # logging.info(f"Sending GET request to verify URL: {verify_url} with params: {params}")
    # print(f"ℹ️ Sending GET request to verify URL: {verify_url} with params: {params}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(verify_url, params=params, timeout=30)  # Выполняем GET запрос
            response.raise_for_status()  # Проверка на HTTP ошибки

            response_text = response.text  # Получаем текст ответа
            # logging.info(f"GeeTest verify response text: {response_text}")
            print(f"✅ GeeTest verify response text: {response_text}")

            if '"status": "success"' in response_text:
                # logging.info("✅ GeeTest verification successful (booy response text check).")
                print("✅ GeeTest verification successful (by response text check).")
                return True  # Верификация успешна
            else:
                # logging.warning(f"GeeTest verification failed (by response text check). Response text: {response_text}")
                print(f"⚠️ GeeTest verification failed (by response text check). Response text: {response_text}")
                return False  # Верификация не удалась

    except httpx.HTTPError as e:
        # logging.error(f"HTTP error during GeeTest verification request: {e}")
        print(f"❌ HTTP error during GeeTest verification request: {e}")
        return False
    except Exception as e:
        # logging.error(f"Error during GeeTest verification request: {e}")
        print(f"❌ Error during GeeTest verification request: {e}")
        return False
