#!/bin/bash
alembic upgrade head
proxychains4 gunicorn src.main:app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:80 --forwarded-allow-ips="*"
