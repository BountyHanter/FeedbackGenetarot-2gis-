import asyncio
from datetime import datetime, timedelta

from celery import shared_task
from tortoise import Tortoise

from config import init_db
from models.user_stats_model import StatusEnum
from routers.reviews_routers import download_reviews
from utils.redis_utils import redis_client
from utils.rewievs_utils import save_or_update_review
from utils.user_utils import get_or_create_user_stats


@shared_task(name="tasks.collect_stats")
def collect_stats(main_user_id: int, filial_id: int):
    """
    Синхронная обёртка для асинхронной задачи.
    """
    asyncio.run(collect_stats_async(main_user_id, filial_id))


async def collect_stats_async(main_user_id: int, filial_id: int):
    wait_time = 5
    start_time = datetime.utcnow()
    end_time = None
    # Инициализация Tortoise ORM
    await init_db()
    user_stats = await get_or_create_user_stats(str(filial_id))

    # Словарь для статистики
    stats_result = {
        "one_star": 0,  # Количество отзывов с 1 звездой
        "two_stars": 0,  # Количество отзывов с 2 звездами
        "three_stars": 0,  # Количество отзывов с 3 звёздами
        "four_stars": 0,  # Количество отзывов с 4 звёздами
        "five_stars": 0,  # Количество отзывов с 5 звёздами
        "rating": 0       # Средний рейтинг
    }

    try:
        offset_date = user_stats.last_parsed_review_date or None
        total_reviews = None  # Всего отзывов (устанавливается после первого запроса)
        processed_reviews = 0  # Сколько отзывов уже обработано
        count_reviews = 0

        # Сопоставление рейтингов с ключами stats_result
        rating_key_map = {
            1: "one_star",
            2: "two_stars",
            3: "three_stars",
            4: "four_stars",
            5: "five_stars"
        }

        while True:
            print(f"Текущие результаты: {stats_result}")
            # Получаем отзывы
            reviews = await download_reviews(main_user_id, filial_id, offset_date=offset_date, limit=50)

            # Устанавливаем общее количество отзывов после первого запроса
            if total_reviews is None:
                total_reviews = reviews['reviews']['result']['2gisReviewsCount']
                time_parsing = (total_reviews/50) * (wait_time+1)
                end_time = start_time + timedelta(seconds=time_parsing)
                print(start_time, end_time)
                print("start time, end time")

                print(f"Всего отзывов: {total_reviews}")

            result = reviews['reviews']['result']['items']

            if result:
                for review in result:
                    if review['catalog']['name'] == "2GIS":
                        await save_or_update_review(review=review, filial_id=filial_id)
                        rating = review['rating']
                        count_reviews += 1

                        # Обновляем соответствующий ключ в stats_result
                        if rating in rating_key_map:
                            stats_result[rating_key_map[rating]] += 1

                # Увеличиваем количество обработанных отзывов
                processed_reviews += len(result)
                remaining_reviews = total_reviews - processed_reviews

                print(f"Обработано: {processed_reviews}/{total_reviews}, Осталось: {remaining_reviews}")

                # Обновляем offset_date и рейтинг
                offset_date = result[-1]['dateCreated']
                print(f"offset_date: {offset_date}")
                stats_result["rating"] = reviews['reviews']['result']['2gisRating']

                # Сохраняем обновленные данные в базу
                await user_stats.update_from_dict({
                    "one_star": stats_result["one_star"],
                    "two_stars": stats_result["two_stars"],
                    "three_stars": stats_result["three_stars"],
                    "four_stars": stats_result["four_stars"],
                    "five_stars": stats_result["five_stars"],
                    "rating": stats_result["rating"],
                    "count_reviews": count_reviews,
                    "last_parsed_review_date": offset_date,
                    "end_parsing_time": end_time,
                    "status": StatusEnum.IN_PROGRESS,
                    "error_message": ''
                })
                await user_stats.save()

                # Задержка перед следующим запросом
                await asyncio.sleep(wait_time)
            else:
                # Завершаем процесс, обновляем статус и дату
                await user_stats.update_from_dict({
                    "last_updated": datetime.utcnow(),
                    "last_parsed_review_date": None,
                    "status": StatusEnum.COMPLETED
                })
                await user_stats.save()
                print('Итоговые результаты:', stats_result)
                break

    except Exception as e:
        print('Ошибка: ', e)
        # Обрабатываем ошибки и записываем их в UserStats
        await user_stats.update_from_dict({
            "status": StatusEnum.FAILED,
            "error_message": str(e),
            "last_updated": datetime.utcnow()
        })
        await user_stats.save()

    finally:
        # Удаляем ключ из Redis
        redis_key = f"filial_task:{filial_id}"
        redis_client.delete(redis_key)
        print(f"Key {redis_key} removed from Redis.")

        # Закрываем соединения с базой данных
        await Tortoise.close_connections()

if __name__ == '__main__':
    asyncio.run(collect_stats_async(13, 70000001030466019))