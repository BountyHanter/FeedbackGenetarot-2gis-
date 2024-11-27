import httpx


async def post_review_async(access_token: str, review_id: str, text: str, is_official: bool = False) -> dict:
    """
    Асинхронно отправляет комментарий к отзыву в API 2ГИС.

    :param access_token: Токен авторизации.
    :param review_id: ID отзыва.
    :param text: Текст комментария.
    :param is_official: Указывает, является ли ответ официальным (по умолчанию False).
    :return: Ответ API в формате JSON.
    """
    url = f'https://api.account.2gis.com/api/1.0/presence/reviews/{review_id}/comments'
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    payload = {
        "text": text,
        "catalog": "2gis",
        "isOfficialAnswer": is_official,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)

        # Проверяем статус-код
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, {response.text}")

        return response.json()
