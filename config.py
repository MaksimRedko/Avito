# --- START OF FILE config.py ---
from typing import List

BOT_TOKEN = "7757476367:AAGKNCRriatQ_p9CloQCqZnnvLwanq-l6bo"  #  оригинал

API_KEY = 'f6bd71199c6985a2ae8310b9b925c216'
CREATE_TASK_URL = "https://api.rucaptcha.com/createTask"
GET_TASK_RESULT_URL = "https://api.rucaptcha.com/getTaskResult"

# BOT_TOKEN = '6548451315:AAGSYOIFxn9avnYbAEzaHLQMtMEqptugxL4' #  тестовый

# AVITO_URL = 'https://www.avito.ru/sankt-peterburg/bytovaya_elektronika?context=H4sIAAAAAAAA_wFRAK7_YToyOntzOjg6ImZyb21QYWdlIjtzOjE0OiJjYXRlZ29yeVdpZGdldCI7czo5OiJmcm9tX3BhZ2UiO3M6MTQ6ImNhdGVnb3J5V2lkZ2V0Ijt9inXVTFEAAAA&q=Apple&s=104'
AVITO_URL_MACBOOK = 'https://www.avito.ru/sankt-peterburg/noutbuki/apple/b_u-ASgBAgICAkTwvA2I0jSo5A302WY?cd=1&f=ASgBAQICAkTwvA2I0jSo5A302WYBQJ7kDcS8sZ4VqOOXFcKZlhWw2O8R1NjvEZzY7xGyo8QRkqPEEY7NrRCYza0QpprGENbMrRA&q=Apple&s=104&user=1'
AVITO_URL_IPAD = 'https://www.avito.ru/sankt-peterburg/planshety_i_elektronnye_knigi?cd=1&f=ASgBAgECAUT0vA2Q0jQBRcaaDBV7ImZyb20iOjMwMDAwLCJ0byI6MH0&q=Apple&s=104'

PROXY_LIST = [
    "83.171.240.157:10234:9bYynD86ur:ERNsWJWBfb",
    "185.42.27.229:10234:Q2RAAx5vGr:XxArs7aVbr",
    "194.226.236.124:10234:KNjTsvNyAj:47ded9uEVZ",
    "194.226.247.213:10234:a3V7DVje9g:gSXf6Edj6M",
    "no_proxy",  # Опция для использования вашего собственного IP
    "185.42.27.24:10234:6KwAT8hWQr:tSVxk3Ztgy"
]

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 12.5; rv:103.0) Gecko/20100101 Firefox/103.0',
    'Mozilla/5.0 (X11; Linux i686; rv:103.0) Gecko/20100101 Firefox/103.0',
    'Mozilla/5.0 (Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:103.0) Gecko/20100101 Firefox/103.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
    'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36 Edg/104.0.1293.47',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36 Edg/104.0.1293.47',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36 OPR/89.0.4447.71',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36 OPR/89.0.4447.71',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36 OPR/89.0.4447.71',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36 OPR/89.0.4447.71',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36 Vivaldi/5.3.2679.70',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36 Vivaldi/5.3.2679.70',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36 Vivaldi/5.3.2679.70',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36 Vivaldi/5.3.2679.70',
    'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36 Vivaldi/5.3.2679.70',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 YaBrowser/22.7.0 Yowser/2.5 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 YaBrowser/22.7.0 Yowser/2.5 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 YaBrowser/22.7.0 Yowser/2.5 Safari/537.36',
]


MAX_ITEMS = 500
CHECK_INTERVAL = 20

KEYWORDS: List[str] = [
    "macbook air m1",
    "macbook air m2",
    "macbook air m3",
    "macbook pro m1",
    "macbook pro m2",
    "macbook pro m3",
    "macbook pro m4",
    "macbook pro max m1",
    "macbook pro max m2",
    "macbook pro max m3",
    "macbook pro max m4",
    # "airpods max",
    # "airpods max 2",
    # "apple watch ultra",
    # "apple watch ultra 2",
    # "playstation 5",
    # "ps5",
    # "playstation 5 pro",
    # "ps5 pro",
    # "iphone 13",
    # "iphone 14",
    # "iphone 15",
    # "iphone 16",
    "ipad m",
    "ipad pro m",
    "ipad air m",
    "ipad", # Добавлено общее ключевое слово
    "ipad pro", # Добавлено общее ключевое слово
    "ipad air", # Добавлено общее ключевое слово
    "macbook air", # Добавлено общее ключевое слово
    "macbook",
    'мак бук',
    # "macbook pro", # Добавлено общее ключевое слово
    # "playstation", # Добавлено общее ключевое слово
    # "iphone", # Добавлено общее ключевое слово
    # "airpods max", # Добавлено общее ключевое слово
    # "apple watch ultra", # Добавлено общее ключевое слово
]

NEGATIVE_KEYWORDS: List[str] = [
    # "магазин",
    # "салон",
    "трейд ин",
    "трейд-ин",
    # "гарантия",
    "keyboard",
    "magic",
    "mouse",
    # "клавиатура",
    "артикул",
    "арт.",
    "2012",
    "2013",
    "2014",
    "2015",
    "2016",
    "2017",
    "2018",
    "2019",
    "iphone 11",
    "iphone 12",
    "iphone XS",
    "iphone XR",
    "iphone SE",
    "iphone 8",
    "iphone 7",
    # "новый",
    # "новые",
    # "запчасти",
    "в продаже",
    # "запечатанный",
    "юр. лицо",
    "юрлицо",
    "кредит",
    "рассрочка",
    # "чек",
    "опт",
    "оптом",
    "точка",
    "скупка",
    "комиссионный",
    "комиссионка",
    "комиссион",
    # "сервисный центр",
    # "сервис центр",
    "витринный",
    "витрина",
    "демка",
    "демo",
    "trade in",
    "trade-in",
    "трейд ин",
    "трейд-ин",
    # "store",
    # "shop",
    "warranty",
    "sealed",
    "new",
    "intel",
    "мы",
    "нас",
    "приветствую",
    "приветствуем",
    "находимся",
    "располагаемся",
    "товаров",
    "возможность",
    "рассрочку",
    "подписывайтесь",
    "в профиле",
    "смотрите в профиле",
    # "доставка",
    "отправка",
    "по россии",
    "цена окончательная",
    "резерв",
    "бронь",
    "забронировать",
    "трк",
    "адрес магазина",
    "магазин находится",
    "покупайте у нас",
    "лучшая цена",
    "скидки",
    "акция",
    "бонус",
    "выгода",
    "розница",
    "розничный",
    # "в наличии", - часто у магазинов такая хуйня, но челики могу писать что в наличии чехлы, хуе, мое
    "количество",
    "полностью проверен",
    "принимаем б/у",
    "скупка телефонов",
    "выкуп техники",
    "обменяем ваш телефон",
    "номер заказа",
    "самовывоз из магазина",
    "технические характеристики",
    "состояние нового",
    "уникальная возможность",
    "покупай смартфоны в беспроцентную рассрочку",
    "от себя даем гарантию",
    "только новая оригинальная техника",
    "добро пожаловать в магазин",
    "в наличии в ",
]
# --- END OF FILE config.py ---