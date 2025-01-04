import uuid
import time
import httpx

from fake_useragent import UserAgent

from utils.password import decrypt_password


async def take_access_token_async(login: str, hashed_password: str) -> str:
    """
    Асинхронно получает токен доступа для заданных логина и пароля.

    :param login: Логин пользователя.
    :param hashed_password: Зашифрованный пароль пользователя.
    :return: Токен доступа.
    """
    password = decrypt_password(hashed_password)
    # Генерация случайных данных
    user_agent = UserAgent().random
    request_id = str(uuid.uuid4())  # Генерация уникального ID для запроса
    current_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())  # Текущее время в нужном формате

    # Заголовки
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en,ru;q=0.9,la;q=0.8",
        "Content-Type": "application/json",
        "Locale": "ru",
        "Origin": "https://account.2gis.com",
        "Referer": "https://account.2gis.com/",
        "Sec-Ch-Ua": '"Chromium";v="126"',  # Нейтральный Chromium
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Linux",
        "User-Agent": user_agent,
        "X-Request-Date": current_time,
        "X-Request-Id": request_id,
    }

    # Тело запроса
    data = {
        "login": login,
        "password": password
    }

    # Асинхронное выполнение запроса
    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.account.2gis.com/api/1.0/users/auth", headers=headers, json=data)

    # Проверка статуса ответа
    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.status_code} {response.text}")

    # Извлечение токена из ответа
    return response.json()['result']['access_token']
