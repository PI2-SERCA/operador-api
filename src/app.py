from flask import Flask
from flask_socketio import SocketIO

from src.config import ALLOWED_HOSTS, BROKER_URL
import pika
from threading import Thread

import functools

import posix_ipc


def on_message_callback(socketio, ch, method, properties, body):
    print(body)
    decoded = body.decode("utf-8")
    # TODO parse object
    socketio.emit("message", decoded, broadcast=True)


def connect_thread(on_message):
    connection = pika.BlockingConnection(pika.URLParameters(BROKER_URL))
    channel = connection.channel()
    channel.queue_declare(queue="alpha", durable=True)
    channel.basic_consume(queue="alpha", on_message_callback=on_message, auto_ack=True)
    channel.start_consuming()


def create_app():
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins=ALLOWED_HOSTS)
    cuts_mq = posix_ipc.MessageQueue("/cuts", posix_ipc.O_CREX)

    on_message = functools.partial(on_message_callback, socketio)

    pika_thread = Thread(target=connect_thread, args=(on_message,), daemon=True)
    pika_thread.start()

    @socketio.on("start-cut")
    def start_cut(data):
        print(data)
        # TODO Fazer isso direito
        cuts_mq.send(data.encode("utf-8"))

    return app, socketio
