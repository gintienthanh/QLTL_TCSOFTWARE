#!/usr/bin/env bash
python manage.py collectstatic --no-input
docker build --platform=linux/amd64 -t hungdvtima2022/qltl:0.0.1 .
sudo docker push hungdvtima2022/qltl:0.0.1

