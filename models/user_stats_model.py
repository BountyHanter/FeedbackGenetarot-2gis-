from enum import Enum

from tortoise import Model
from tortoise import fields


class StatusEnum(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"


class UserStats(Model):
    id = fields.IntField(pk=True)
    filial_id = fields.CharField(max_length=50)
    one_star = fields.IntField(null=True, blank=True)
    two_stars = fields.IntField(null=True, blank=True)
    three_stars = fields.IntField(null=True, blank=True)
    four_stars = fields.IntField(null=True, blank=True)
    five_stars = fields.IntField(null=True, blank=True)
    rating = fields.FloatField(null=True, blank=True)
    count_reviews = fields.IntField(null=True, blank=True)
    last_updated = fields.DatetimeField(null=True, blank=True)
    last_parsed_review_date = fields.TextField(null=True, blank=True)
    status = fields.CharEnumField(enum_type=StatusEnum, default=StatusEnum.PENDING)
    error_message = fields.TextField(null=True, blank=True)
    end_parsing_time = fields.DatetimeField(null=True, blank=True)

    class Meta:
        table = "user_stats"
