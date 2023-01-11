import multiprocessing
import threading


def stop_all_threads(stop_events: list[threading.Event]) -> None:
    """ stop all threads """
    for stop_event in stop_events:
        stop_event.set()


def getting_thread(thread_nr: int, task_que: multiprocessing.queues, stop_event: threading.Event) -> None:
    """ getting thread """
    while stop_event.is_set() is False and task_que.empty() is False:
        item = task_que.get()
        print(f"{thread_nr=} Got {item=}")
        time.sleep(1)
    print(f"Stop Thread Flag is Set in {thread_nr}")
    return
