import os

BROKER_URL = os.environ.get("BROKER_URL", "amqp://guest:guest@localhost:5672")

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS", "https://socketio-playground.ibrod83.com,http://localhost:3001"
).split(",")
