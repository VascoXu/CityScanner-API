web: gunicorn application:app
worker: rq worker -u $REDIS_URL scl-tasks