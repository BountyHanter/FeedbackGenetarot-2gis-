import asyncio
from pprint import pprint

import httpx
from fastapi import HTTPException


async def fetch_user_info_async(access_token: str) -> dict:
    """
    Выполняет GET-запрос к API /users с заголовком Authorization.

    Args:
        access_token (str): Токен авторизации.

    Returns:
        dict: Словарь с ключами:

            - **meta** (dict): Метаинформация о запросе, содержит:
                - **code** (int): HTTP-статус ответа.
            - **result** (dict): Данные пользователя:
                - **registerBy** (str): Способ регистрации (например, email).
                - **id** (str): Идентификатор пользователя.
                - **bizUserId** (str): Бизнес-идентификатор пользователя.
                - **email** (str): Почта пользователя.
                - **phone** (str): Номер телефона пользователя.
                - **name** (str): Полное имя пользователя.
                - **firstName** (str): Имя пользователя.
                - **lastName** (str): Фамилия пользователя (если есть).
                - **role** (str): Роль пользователя (например, client).
                - **language** (str): Язык интерфейса пользователя.
                - **isAcceptedPrivacyPolicy** (bool): Согласие с политикой конфиденциальности.
                - **phoneNumberConfirmed** (bool): Подтверждён ли номер телефона.
                - **orgs** (list): Список организаций, где пользователь участвует:
                    - **id** (str): Идентификатор организации.
                    - **name** (str): Название организации.
                    - **regionId** (int): Идентификатор региона.
                    - **regionName** (str): Название региона.
                    - **isRegionPublished** (bool): Опубликован ли регион.
                    - **status** (str): Статус организации (например, approved).
                    - **isActive** (bool): Активна ли организация.
                    - **isPromotional** (bool): Является ли промо-акцией.
                    - **isPrePromotional** (bool): Предварительная промо-акция.
                    - **country** (str): Код страны (например, RU).
    """

    url = "https://api.account.2gis.com/api/1.0/users"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()  # Вызывает исключение при статусах 4xx и 5xx
        except httpx.HTTPStatusError as exc:
            # Обработка ошибок статуса HTTP
            if exc.response.status_code == 401:
                raise HTTPException(
                    status_code=401,
                    detail=f"Unauthorized: Invalid or expired access token. Response: {exc.response.text}"
                )
            else:
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f"HTTP error {exc.response.status_code}: {exc.response.text}"
                )
        except httpx.RequestError as exc:
            # Обработка ошибок сети
            raise HTTPException(
                status_code=500,
                detail=f"Request failed: {str(exc)}"
            )

    # Попытка преобразования ответа в JSON
    try:
        return response.json()
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail="Response is not in valid JSON format"
        )

async def fetch_filials_info_async(*, org_id: str, access_token: str) -> dict:
    """
    Выполняет GET-запрос к API /branches для получения информации о филиалах организации.

    Args:
        org_id (str): ID организации.
        access_token (str): Токен авторизации.

    Returns:
        dict: Словарь с ключами:

            - **meta** (dict): Метаинформация о запросе, содержит:
                - **code** (int): HTTP-статус ответа.

            - **result** (dict): Информация о филиалах организации:
                - **total** (int): Общее количество филиалов.
                - **items** (list): Список филиалов, где каждый элемент — это словарь с данными филиала:
                    - **id** (str): Уникальный идентификатор филиала.
                    - **name** (str): Название филиала.
                    - **address** (str): Адрес филиала.
                    - **city** (dict): Информация о городе, содержит:
                        - **id** (str): Идентификатор города.
                        - **name** (str): Полное название города.
                        - **type** (str): Тип города (например, `byCityId`).
                        - **originalName** (str): Оригинальное название города.
                    - **buildingId** (str): Идентификатор здания, где находится филиал.
                    - **checkedAt** (int): Время последней проверки филиала в формате Unix timestamp.
                    - **entrance** (dict): Информация о входе в филиал:
                        - **id** (str): Уникальный идентификатор входа.
                    - **referencePoint** (str): Ориентир, если указан (может быть пустым).
                    - **isNew** (bool): Флаг, указывающий, является ли филиал новым.
                    - **isCityInFirmProject** (bool): Флаг, указывающий, участвует ли город в проекте фирмы.
                    - **country** (dict): Информация о стране, содержит:
                        - **id** (str): Идентификатор страны.
                        - **phoneCode** (str): Телефонный код страны.
                        - **phoneNumberAvailableLengths** (list): Список возможных длин телефонных номеров.
                        - **availableSocialNetworks** (list): Список доступных социальных сетей (например, `twitter`, `vkontakte`).
                        - **availableMessengers** (list): Список доступных мессенджеров (например, `telegram`, `viber`).
                    - **isActive** (bool): Флаг, активен ли филиал.
                    - **inn** (str): ИНН филиала.
                    - **confirmed** (dict): Подтверждённая информация о филиале, содержит:
                        - **name** (bool): Подтверждено ли имя филиала.
                        - **address** (bool): Подтверждён ли адрес филиала.
                        - **referencePoint** (bool): Подтверждён ли ориентир.
                        - **city** (bool): Подтверждён ли город филиала.
                        - **entrance** (bool): Подтверждён ли вход филиала.
    """

    url = "https://api.account.2gis.com/api/1.0/branches"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    params = {
        "orgId": org_id,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)

    try:
        return response.json()
    except ValueError:
        return {"error": "Response is not in JSON format", "response": response.text}


async def fetch_user_and_filials_info(access_token: str) -> list[dict]:
    """
    Получает информацию о пользователе и его филиалах.

    Args:
        access_token (str): Токен авторизации.

    Returns:
        list[dict]: Список из двух словарей:
            - Первый словарь: Данные пользователя.
            - Второй словарь: Данные о филиалах всех организаций пользователя.
    """
    # Получаем информацию о пользователе
    user_info = await fetch_user_info_async(access_token)
    if "error" in user_info:
        return [{"error": "Failed to fetch user info", "details": user_info}]

    # Извлекаем список организаций
    org_ids = [org["id"] for org in user_info.get("result", {}).get("orgs", [])]
    filials_info = {}

    # Запрашиваем данные о филиалах для каждой организации
    for org_id in org_ids:
        filials = await fetch_filials_info_async(org_id=org_id, access_token=access_token)
        if "error" in filials:
            filials_info[org_id] = {"error": f"Failed to fetch filials for org_id {org_id}"}
        else:
            filials_info[org_id] = filials.get("result", {})

    # Возвращаем оба результата
    return [
        {"user_info": user_info},
        {"filials_info": filials_info}
    ]

if __name__ == "__main__":
    # Токен авторизации
    access_token = "2aeb20754b91f3241430fc96fb9a77b1cf3bd799"

    # Запуск асинхронной функции в синхронной среде
    async def run():
        result = await fetch_user_and_filials_info(access_token)
        pprint(result)

    # Используем asyncio для запуска асинхронного кода
    asyncio.run(run())