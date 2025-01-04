from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "main_user_id" INT NOT NULL UNIQUE,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(128) NOT NULL,
    "access_token" VARCHAR(128)  UNIQUE
);
CREATE TABLE IF NOT EXISTS "user_stats" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "filial_id" VARCHAR(50) NOT NULL,
    "one_star" INT,
    "two_stars" INT,
    "three_stars" INT,
    "four_stars" INT,
    "five_stars" INT,
    "rating" REAL,
    "count_reviews" INT,
    "last_updated" TIMESTAMP,
    "last_parsed_review_date" TEXT,
    "status" VARCHAR(11) NOT NULL  DEFAULT 'pending' /* IN_PROGRESS: in_progress\nCOMPLETED: completed\nFAILED: failed\nPENDING: pending */,
    "error_message" TEXT,
    "end_parsing_time" TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "reviews" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "filial_id" INT NOT NULL,
    "review_id" INT NOT NULL,
    "rating" INT NOT NULL,
    "text" TEXT NOT NULL,
    "created_at" TIMESTAMP NOT NULL,
    "user_name" TEXT NOT NULL,
    "comments_count" INT NOT NULL,
    "likes_count" INT NOT NULL,
    "topics" JSON,
    "is_favorite" INT NOT NULL  DEFAULT 0,
    "photos" JSON
) /* Модель для хранения отзывов. */;
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
