from pydantic import BaseModel
from tortoise import Model, fields


class Reviews(Model):
    """
    Модель для хранения отзывов.
    """
    id = fields.IntField(pk=True)  # Уникальный идентификатор комментария
    filial_id = fields.IntField()  # ID филиала 2Gis
    review_id = fields.IntField()  # ID отзыва на 2Gis
    rating = fields.IntField()  # Оценка отзыва
    text = fields.TextField()  # Текст отзыва
    created_at = fields.DatetimeField()  # Дата и время создания отзыва
    user_name = fields.TextField()  # Имя пользователя, оставившего отзыв
    comments_count = fields.IntField()  # Количество ответов на отзыв
    likes_count = fields.IntField()  # Количество лайков у отзыва
    topics = fields.JSONField(null=True)  # Темы отзыва
    is_favorite = fields.BooleanField(default=False)  # Избранное
    photos = fields.JSONField(null=True)

    class Meta:
        table = "reviews"  # Название таблицы в базе данных
        ordering = ["-created_at"]  # По умолчанию сортировка по дате создания (новые сверху)


class Complaint(BaseModel):
    main_user_id: int
    text: str
    is_no_client_complaint: bool


class ReplyReview(BaseModel):
    main_user_id: int
    text: str
    is_official: bool
