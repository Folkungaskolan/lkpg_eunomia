""" Que DeQue Demo """
import queue
import threading
import time

# FIFO Queue First In First Out
# LIFO Queue Last In First Out
# Priority

q = queue.Queue()  # FIFO Default


def putting_thread(q, stop_thread_flag: threading.Event):
    """ abc """
    while stop_thread_flag.is_set() is False:
        q.put(5)
        time.sleep(1)
        print("Put Something")
    print("Stop Thread Flag is Set")
    return

event = threading.Event()
event.clear() # False
# event.set() # True
t = threading.Thread(target=putting_thread, args=(q,event))
t.start()

i = 1

while True:
    print(q.get(), i)
    print("Got Something")
    i = 1 + i
    if i > 3:
        break

event.set()
