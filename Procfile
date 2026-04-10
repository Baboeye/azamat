release: bash release.sh
release: sh release.sh || python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: gunicorn material_accounting.wsgi --bind 0.0.0.0:$PORT --workers 2 --worker-class sync --timeout 120
