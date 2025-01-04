import httpx
from fastapi import HTTPException

from models.reviews_model import Reviews


async def post_review_async(*, access_token: str, review_id: int, text: str, is_official: bool = False) -> dict:
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
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error from 2GIS API: {response.text}"
            )
        review = await Reviews.filter(review_id=review_id).first()
        review.comments_count += 1
        await review.save()
        return response.json()
