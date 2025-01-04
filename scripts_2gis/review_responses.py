import httpx

from fastapi import HTTPException


async def load_responses_to_review(*, access_token, review_id):
    url = f"https://api.account.2gis.com/api/1.0/presence/reviews/{review_id}/comments"
    params = {
        "catalog": "2gis",
        "limit": 200
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()  # Возвращаем JSON-ответ
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error from 2GIS API: {response.text}"
            )


async def delete_response_to_review(*, access_token, review_id, comment_id):
    url = f"https://api.account.2gis.com/api/1.0/presence/reviews/{review_id}/comments/{comment_id}"
    params = {
        "catalog": "2gis",
        "type": "reply"
    }
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers, params=params)
        if response.status_code == 200:
            print("Комментарий успешно удалён.")
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error from 2GIS API: {response.text}"
            )
