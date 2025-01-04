FROM python:3.10-slim

WORKDIR /app

# Установить системные зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    default-libmysqlclient-dev \
    sqlite3 \
    redis-tools \
    && apt-get clean

# Установить Python-зависимости
COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

# Копировать исходный код
COPY . .

# Копируем и делаем скрипт entrypoint исполняемым
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Открыть порт
EXPOSE 8000

# Настроить ENTRYPOINT и CMD
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

