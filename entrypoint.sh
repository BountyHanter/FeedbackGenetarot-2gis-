#!/bin/bash

# Останавливаем выполнение скрипта при ошибке
set -e

# Переход в рабочую директорию
cd /app


# Проверяем доступность Redis
echo "Проверка доступности Redis..."
until redis-cli -h redis ping > /dev/null 2>&1; do
    echo "Ожидание Redis..."
    sleep 1
done
echo "Redis доступен."

# Запускаем приложение
echo "ENTRYPOINT завершён. Передача управления CMD..."
exec "$@"

