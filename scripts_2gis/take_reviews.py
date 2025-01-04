import httpx
from fastapi import HTTPException


async def fetch_reviews_async(*, filial_id, access_token, limit=20, pin_requested_first=False, without_answer=None,
                              rating=None, offset_date=None):
    """
    Выполняет GET-запрос для получения отзывов и возвращает JSON-ответ.

    Args:
        filial_id (str): Айди филиала.
        access_token (str): Токен авторизации.
        limit (int): Лимит отзывов (по умолчанию 20).
        pin_requested_first (bool): Флаг "pinRequestedFirst" (по умолчанию False).
        without_answer (bool): Флаг "withoutAnswer" (если None, параметр не передается).
        rating (str): Фильтр по рейтингу (если None, параметр не передается).
        offset_date (str): Фильтр по дате, указываем дату после которой получаем отзывы

    Returns:
        dict: Словарь с ключами:

            - **meta** (dict): Метаинформация о запросе, содержит:
                - **code** (int): HTTP-статус ответа.

            - **result** (dict): Данные о количестве отзывов и самих отзывах:
                - **2gisReviewsCount** (int): Количество отзывов в 2GIS.
                - **2gisRating** (float): Средний рейтинг в 2GIS.
                - **rdReviewsCount** (int): Количество отзывов с других платформ (например, `0`).
                - **items** (list): Список отзывов, где каждый элемент — это словарь с данными отзыва:
                    - **id** (str): Уникальный идентификатор отзыва.
                    - **rating** (int): Рейтинг отзыва.
                    - **catalog** (dict): Информация о каталоге:
                        - **id** (str): Идентификатор каталога (например, `"2gis"`).
                        - **name** (str): Название каталога (например, `"2GIS"`).
                    - **text** (str): Текст отзыва.
                    - **dateCreated** (str): Дата создания отзыва в формате ISO 8601.
                    - **dateEdited** (str | None): Дата редактирования отзыва (или `None`, если не редактировался).
                    - **commentsCount** (int): Количество комментариев.
                    - **likesCount** (int): Количество лайков.
                    - **url** (str): URL на отзыв (если доступен, иначе пустая строка).
                    - **user** (dict): Информация о пользователе, оставившем отзыв:
                        - **name** (str): Имя пользователя.
                        - **photoPreviewUrls** (dict): Превью аватарки пользователя:
                            - **1920x** (str): Ссылка на фото 1920x.
                            - **320x** (str): Ссылка на фото 320x.
                            - **640x** (str): Ссылка на фото 640x.
                            - **64x64** (str): Ссылка на фото 64x64.
                            - **url** (str): Полный URL фото.
                    - **attributes** (dict): Дополнительные атрибуты отзыва:
                        - **isHidden** (bool): Флаг, скрыт ли отзыв.
                        - **isRated** (bool): Флаг, оценен ли отзыв.
                        - **hasUnresolvedComplains** (bool): Есть ли нерешённые жалобы.
                        - **pinStatus** (str): Статус закрепления отзыва (например, `"none"`).
                    - **allowedActions** (dict): Возможные действия с отзывом:
                        - **replyInCatalog** (bool): Разрешено ли отвечать в каталоге.
                        - **showInCatalog** (bool): Разрешено ли отображение в каталоге.
                        - **reply** (bool): Разрешён ли ответ на отзыв.
                        - **complain** (bool): Разрешена ли подача жалобы.
                        - **complainNoClient** (bool): Разрешена ли жалоба без клиента.
                        - **pin** (bool): Разрешено ли закрепление отзыва.
                        - **setMainComment** (bool): Разрешено ли назначение основным комментарием.
                    - **hasCompanyComment** (bool): Флаг, есть ли комментарий компании.
                    - **firstAnswer** (str | None): Первый ответ на отзыв (или `None`, если нет).
                    - **photos** (list): Список фотографий, прикрепленных к отзыву:
                        - **id** (str): Идентификатор фотографии.
                        - **date_created** (str): Дата создания фото в формате ISO 8601.
                        - **preview_urls** (dict): Превью фото:
                            - **1920x** (str): Ссылка на фото 1920x.
                            - **320x** (str): Ссылка на фото 320x.
                            - **640x** (str): Ссылка на фото 640x.
                            - **64x64** (str): Ссылка на фото 64x64.
                            - **url** (str): Полный URL фото.
                        - **visibility_status** (str): Статус видимости фото (например, `"visible"`).
                    - **readonly** (bool): Флаг, доступен ли отзыв только для чтения.
                    - **branch** (dict): Информация о филиале:
                        - **id** (str): ID филиала.
                        - **name** (str): Название филиала.
                        - **address** (str): Адрес филиала.
                    - **source** (str | None): Источник отзыва (или `None`).
    """
    # Базовый URL для запроса
    url = f"https://api.account.2gis.com/api/1.0/presence/branch/{filial_id}/reviews"

    # Заголовки
    headers = {
        "Authorization": f"Bearer {access_token}",  # Используем переданный токен
    }

    # Параметры запроса
    params = {
        "limit": limit,  # Лимит отзывов
        "pinRequestedFirst": str(pin_requested_first).lower(),  # Приводим к "true"/"false"
    }

    # Добавляем параметры только если они не None
    if without_answer is not None:
        params["withoutAnswer"] = str(without_answer).lower()
    if rating is not None:
        params["rating"] = rating
    if offset_date is not None:
        params["offsetDate"] = offset_date  # Добавляем offsetDate в параметры

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error from 2GIS API: {response.text}"
            )
    try:
        # Если ответ в формате JSON
        response_data = response.json()
        return response_data
    except ValueError:
        # Если ответ не является JSON
        return {"error": "Response is not in JSON format", "response": response.text}
