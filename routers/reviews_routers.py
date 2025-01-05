from datetime import timezone, datetime
from enum import Enum
from typing import Optional, List

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from tortoise.transactions import in_transaction

from models.reviews_model import Reviews, Complaint, ReplyReview
from scripts_2gis.complain import submit_complaint_async
from scripts_2gis.login import take_access_token_async
from scripts_2gis.response_review import post_review_async
from scripts_2gis.review_responses import load_responses_to_review, delete_response_to_review
from scripts_2gis.take_reviews import fetch_reviews_async
from utils.api_utils import handle_api_request
from utils.user_utils import get_user_and_token

router = APIRouter()


class Rating(str, Enum):
    positive = "positive"
    negative = "negative"


# @router.get("/dgis_get_reviews", status_code=200)
async def download_reviews(
        main_user_id: int,
        filial_id: int,
        limit: Optional[int] = Query(None, description="Количество отзывов"),
        pin_requested_first: Optional[bool] = Query(None, description="Закреплённые отзывы в начале"),
        without_answer: Optional[bool] = Query(None, description="Отзывы без ответа"),
        rating: Optional[Rating] = Query(None, description="Рейтинг отзыва (positive или negative)"),
        offset_date: Optional[str] = Query(None, description="Дата для смещения"),
):
    # Проверяем, существует ли пользователь с таким main_user_id
    try:
        user, access_token = await get_user_and_token(main_user_id)

    except HTTPException as e:
        # Пробрасываем HTTPException, чтобы FastAPI сам обработал её
        raise e

    # Сбор параметров для запроса
    params = {
        "filial_id": filial_id,
        "limit": limit,
        "pin_requested_first": pin_requested_first,
        "without_answer": without_answer,
        "rating": rating,
        "offset_date": offset_date,
    }

    # Убираем параметры, значение которых None
    params = {
        key: value for key, value in params.items()
        if value is not None and not isinstance(value, type(Query()))
    }

    # Выполняем запрос для получения отзывов
    try:
        reviews = await fetch_reviews_async(**params, access_token=access_token)
        return {"message": "Отзывы получены успешно", "reviews": reviews}
    except HTTPException as e:
        if e.status_code == 401:  # Если токен недействителен
            try:
                # Обновляем токен
                new_access_token = await take_access_token_async(user.username, user.hashed_password)

                # Сохраняем новый токен в базе
                async with in_transaction():
                    user.access_token = new_access_token
                    await user.save()

                # Повторяем запрос с новым токеном
                result = await fetch_reviews_async(**params, access_token=new_access_token)
                return result
            except Exception as inner_e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Не удалось обновить токен доступа: {inner_e}"
                )
        elif e.status_code == 404:  # Если ресурс не найден
            raise HTTPException(status_code=404, detail=e.detail)
        else:  # Обработка других ошибок
            raise HTTPException(status_code=500, detail=f"Неизвестная ошибка: {e}")


@router.get("/get_reviews", status_code=200)
async def get_reviews_from_db(
        filial_id: int,
        limit: Optional[int] = Query(20, description="Количество отзывов (по умолчанию 20)"),
        offset_date: Optional[str] = Query(None, description="Дата для смещения"),
        rating: Optional[str] = Query(None, description="Минимальный рейтинг отзыва"),
        topics: Optional[List[str]] = Query(None, description="Темы отзыва"),
        is_favorite: Optional[bool] = Query(None, description="Избранное (True/False)"),
        without_answer: Optional[bool] = Query(None, description="Без ответа (True/False"),
):
    """
    Получение отзывов из базы данных с фильтрацией.
    """
    try:

        # Базовый запрос к таблице Reviews
        query = Reviews.filter(filial_id=filial_id)

        # Фильтрация по дате
        if offset_date:
            try:
                # Преобразуем дату из UTC+7 в UTC
                offset_date_utc = datetime.fromisoformat(offset_date).astimezone(timezone.utc)
                query = query.filter(created_at__lt=offset_date_utc)
            except ValueError:
                raise HTTPException(status_code=400, detail="Недопустимый формат offset_date. Используйте формат ISO 8601.")

        rating_list = [int(r) for r in rating.split(',')] if rating else None

        # Фильтрация по рейтингу
        if rating_list is not None:
            query = query.filter(rating__in=rating_list)

        # Фильтрация по темам
        if topics is not None:
            query = query.filter(topics__contains=topics)

        # Фильтрация по избранному
        if is_favorite is not None:
            query = query.filter(is_favorite=is_favorite)

        # Фильтрация по наличию ответов
        if without_answer is True:
            query = query.filter(comments_count=0)

        # Сортировка по дате от новых к старым и ограничение по количеству
        query = query.order_by("-created_at").limit(limit)

        # Выполняем запрос
        reviews = await query.all()

        # Преобразуем результаты для возврата
        reviews_result = []
        for review in reviews:
            reviews_result.append({
                "id": review.id,
                "review_id": review.review_id,
                "rating": review.rating,
                "text": review.text,
                "created_at": review.created_at,
                "user_name": review.user_name,
                "comments_count": review.comments_count,
                "likes_count": review.likes_count,
                "topics": review.topics,
                "is_favorite": review.is_favorite,
                "photos": review.photos
            })

        return {
            "message": "Reviews fetched successfully",
            "reviews": reviews_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Неизвестная ошибка: {e}")


@router.post("/post_review_reply/{review_id}", status_code=200)
async def post_review_reply(
    review_id: int,
    reply_review: ReplyReview
):
    """
    Отправляет отзыв с комментариями.
    """

    review = await Reviews.filter(id=review_id).first()
    if not review:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Отзыв не найден."},
        )

    dgis_review_id = review.review_id
    return await handle_api_request(
        main_user_id=reply_review.main_user_id,
        api_function=post_review_async,
        review_id=dgis_review_id,
        text=reply_review.text,
        is_official=reply_review.is_official,
    )


@router.get("/comments/fetch", status_code=200)
async def get_comments(
    main_user_id: int,
    review_id: int
):
    """
    Загружает ответы на отзыв.
    """
    return await handle_api_request(
        main_user_id=main_user_id,
        api_function=load_responses_to_review,
        review_id=review_id,
    )


@router.post("/comments/delete", status_code=200)
async def delete_comment(
    main_user_id: int,
    review_id: int,
    comment_id: int
):
    """
    Удаляет выбранный ответ на отзыв.
    """
    return await handle_api_request(
        main_user_id=main_user_id,
        api_function=delete_response_to_review,
        review_id=review_id,
        comment_id=comment_id,
    )


@router.post("/favorite/{review_id}", status_code=200)
async def post_favorite(review_id: int):
    review = await Reviews.filter(id=review_id).first()
    if not review:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Отзыв не найден."},
        )
    review.is_favorite = not review.is_favorite
    await review.save()

    return JSONResponse(
        status_code=200,
        content={"success": True, "is_favorite": review.is_favorite},
    )


@router.post("/complaints/{review_id}", status_code=200)
async def post_complaint(review_id: int, complaint: Complaint):
    review = await Reviews.filter(id=review_id).first()
    if not review:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Отзыв не найден."},
        )

    main_user_id = complaint.main_user_id
    text = complaint.text
    is_no_client_complaint = complaint.is_no_client_complaint
    dgis_review_id = str(review.review_id)

    return await handle_api_request(
        main_user_id=main_user_id,
        api_function=submit_complaint_async,
        review_id=dgis_review_id,
        text=text,
        is_no_client_complaint=is_no_client_complaint,
    )



