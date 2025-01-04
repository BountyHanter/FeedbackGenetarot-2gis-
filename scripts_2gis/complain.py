import asyncio

import httpx
from fastapi import HTTPException


async def submit_complaint_async(*, access_token: str, review_id: str, text: str, is_no_client_complaint: bool = False) -> dict:
    """
    Асинхронно отправляет жалобу на отзыв в API 2ГИС.

    :param access_token: Токен авторизации.
    :param review_id: ID отзыва.
    :param text: Текст жалобы.
    :param is_no_client_complaint: Указывает, является ли жалоба о том, что клиента не было.
    :return: Ответ API в формате JSON.
    """
    # URL для отправки запроса
    url = f"https://api.account.2gis.com/api/1.0/presence/reviews/{review_id}/complaints"

    # Заголовки
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    # Данные для жалобы
    payload = {
        "text": text,
        "catalog": "2gis",
        "isNoClientComplaint": is_no_client_complaint,
    }

    # Отправка запроса
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)

    # Проверка успешности запроса
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to submit complaint: {response.status_code} {response.text}"
        )

    return response.json()

if __name__ == "__main__":
    asyncio.run(submit_complaint_async(access_token="718e1c3de2c1e960d40a902306a4449357a1fd58", review_id="124479532", text='1234'))