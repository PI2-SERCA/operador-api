from flask import Flask
from flask_socketio import SocketIO

from src.config import ALLOWED_HOSTS, BROKER_URL
import pika
from threading import Thread, Semaphore
import json

import functools

import posix_ipc

from src.util.data import filter_data


state = []
state_sem = Semaphore()


def on_message_callback(socketio, ch, method, properties, body):
    global state
    # decode json
    decoded = json.loads(body.decode("utf-8"))

    print("Mensagem recebida")

    state_sem.acquire()
    state = state + decoded
    state_sem.release()

    filtered = filter_data(decoded)
    socketio.emit("append-cut", filtered, broadcast=True)


def connect_thread(on_message):
    url_params = pika.URLParameters(BROKER_URL)
    connection = pika.BlockingConnection(url_params)
    channel = connection.channel()
    channel.queue_declare(queue="cuts", durable=True)
    print("Connected to queue: ", url_params.host)
    channel.basic_consume(queue="cuts", on_message_callback=on_message, auto_ack=True)
    channel.start_consuming()


def create_app():
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins=ALLOWED_HOSTS)
    cuts_mq = posix_ipc.MessageQueue("/cuts", posix_ipc.O_CREAT)

    on_message = functools.partial(on_message_callback, socketio)

    pika_thread = Thread(target=connect_thread, args=(on_message,), daemon=True)
    pika_thread.start()

    # TODO notify when scribe ends

    @socketio.on("start-cut")
    def start_cut():
        global state

        state_sem.acquire()
        cut = state.pop(0)
        state_sem.release()

        cuts_mq.send(cut["gcode"].encode("utf-8"))

    @socketio.on("get-state")
    def get_state():
        global state
        filtered = filter_data(state)

        socketio.emit("state", filtered)

    return app, socketio
