release: sh release.sh
web: gunicorn material_accounting.wsgi --bind 0.0.0.0:$PORT --workers 2 --worker-class sync --timeout 120
