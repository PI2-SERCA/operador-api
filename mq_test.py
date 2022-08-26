import posix_ipc
import time

if __name__ == "__main__":
    mq = posix_ipc.MessageQueue("/cuts")
    while True:
        msg = mq.receive()
        print(msg[0])
        time.sleep(0.5)
