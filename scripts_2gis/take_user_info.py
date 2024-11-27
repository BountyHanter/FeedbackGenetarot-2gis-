import httpx
import requests

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
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            return {"error": "Response is not in JSON format"}
    else:
        return {"error": f"Error: {response.status_code}", "response": response.text}


async def fetch_filials_info_async(org_id: str, access_token: str) -> dict:
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
