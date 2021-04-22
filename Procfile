web: gunicorn application:app --timeout 500
worker: rq worker -u $REDIS_URL scl-tasks