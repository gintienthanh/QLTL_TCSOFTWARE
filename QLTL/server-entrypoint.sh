echo "Run backend server ..."

python manage.py collectstatic --noinput

gunicorn --config gunicorn-cfg.py QLTL.wsgi