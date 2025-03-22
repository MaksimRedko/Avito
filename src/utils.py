import logging

from playwright.async_api import Page


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
    captcha_title_en = "Access Denied: IP problem" # или что-то подобное, если сайт на английском
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

    return False # Капча не обнаружена

async def handle_avito_ip_captcha(page: Page) -> bool:
    """
    Обрабатывает страницу "Доступ ограничен: проблема с IP" на Авито.
    Нажимает кнопку "Продолжить", чтобы перейти к решению капчи.
    Возвращает True, если кнопка была нажата и дальнейшая капча ожидается, False в противном случае.
    """
    ip_problem_title_ru = "Доступ ограничен: проблема с IP"
    page_title = await page.title()

    if ip_problem_title_ru in page_title:
        logging.info("Handling 'IP problem' captcha page.")
        print("ℹ️ Handling 'IP problem' captcha page...")
        try:
            continue_button = page.locator('button', has_text="Продолжить") #  Ищем кнопку с текстом "Продолжить"
            if await continue_button.is_visible():
                await continue_button.click()
                logging.info("Clicked 'Продолжить' button. Waiting for next captcha...")
                print("✅ Clicked 'Продолжить' button. Waiting for next captcha...")
                return True #  Успешно нажали кнопку, ожидаем следующую капчу

            else:
                logging.warning("'Продолжить' button not found on 'IP problem' page.")
                print("⚠️ 'Продолжить' button not found on 'IP problem' page.")
                return False # Кнопка не найдена, не смогли обработать

        except Exception as e:
            logging.error(f"Error handling 'IP problem' captcha: {e}")
            print(f"❌ Error handling 'IP problem' captcha: {e}")
            return False # Ошибка при обработке

    return False # Не страница "проблемы с IP"


def solve_captcha():
    pass