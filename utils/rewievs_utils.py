import re
from datetime import datetime

from models.reviews_model import Reviews


def fix_date_format(date_str: str) -> str:
    """
    Исправляет формат строки времени, обрезая миллисекунды до 3 цифр.
    """
    # Исправляем миллисекунды, оставляя только первые три цифры
    fixed_date_str = re.sub(r"(\.\d{3})\d+", r"\1", date_str)
    return fixed_date_str


async def save_or_update_review(*, review, filial_id):
    """
    Сохраняет новый отзыв или обновляет существующий.

    :param filial_id: ID филиала
    :param review: Словарь с данными отзыва.
    """
    # Проверяем, существует ли отзыв с таким id
    existing_review = await Reviews.get_or_none(review_id=review['id'])

    # Извлекаем оригинальные URL фотографий или None, если фото отсутствуют
    photos = [photo['preview_urls']['url'] for photo in review.get('photos', [])] or None

    if existing_review:
        # Обновляем существующий отзыв
        await existing_review.update_from_dict({
            "comments_count": review['commentsCount'],
            "likes_count": review['likesCount'],
            "photos": photos,
        })
        await existing_review.save()
        print(f"Отзыв с id {review['id']} обновлён.")
    else:
        fixed_date = fix_date_format(review['dateCreated'])
        created_at = datetime.fromisoformat(fixed_date)

        # Создаём новый отзыв
        await Reviews.create(
            filial_id=filial_id,
            review_id=review['id'],
            rating=review['rating'],
            text=review['text'],
            created_at=created_at,
            user_name=review['user']['name'],
            comments_count=review['commentsCount'],
            likes_count=review['likesCount'],
            photos=photos,
        )
        print(f"Отзыв с id {review['id']} создан.")

