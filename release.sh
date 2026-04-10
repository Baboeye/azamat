#!/bin/bash
set -e

echo "🔧 Выполняю миграции базы данных..."
python manage.py migrate

echo "📦 Собираю статические файлы..."
python manage.py collectstatic --noinput

echo "📊 Инициализирую тестовые данные..."
python manage.py init_data

echo "✅ Инициализация завершена!"
