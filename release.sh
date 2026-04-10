#!/bin/bash
set -e

echo "🔧 Выполняю миграции базы данных..."
python manage.py migrate --verbosity 2

echo "📦 Собираю статические файлы..."
python manage.py collectstatic --noinput --verbosity 2

echo "📊 Инициализирую тестовые данные..."
python manage.py init_data || echo "⚠️ Ошибка при инициализации данных (возможно, уже инициализировано)"

echo "✅ Инициализация завершена!"
echo "🟢 Приложение готово к запуску"
