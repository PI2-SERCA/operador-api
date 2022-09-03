from flask import Flask
from flask_socketio import SocketIO

from src.config import ALLOWED_HOSTS, BROKER_URL
import pika
from threading import Thread, Semaphore
import json

import functools

import posix_ipc


state = []
state_sem = Semaphore()


def on_message_callback(socketio, ch, method, properties, body):
    # decode json
    decoded = json.loads(body.decode("utf-8"))
    # TODO parse object
    state_sem.acquire()
    state.append(decoded)
    state_sem.release()


def connect_thread(on_message):
    connection = pika.BlockingConnection(pika.URLParameters(BROKER_URL))
    channel = connection.channel()
    channel.queue_declare(queue="cuts", durable=True)
    channel.basic_consume(queue="cuts", on_message_callback=on_message, auto_ack=True)
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

    @socketio.on("get-state")
    def get_state(data):
        global state
        socketio.emit("state", state)

    return app, socketio
