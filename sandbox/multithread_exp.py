import asyncio

# Next-Level Concurrent Programming In Python With Asyncio @ArjanCodes
# https://www.youtube.com/watch?v=GpqAQxH1Afc

# How To Easily Do Asynchronous Programming With Asyncio In Python@ ArjanCodes
# https://www.youtube.com/watch?v=2IW-ZEui4h4

# The Power Of The Plugin Architecture In Python @ArjanCodes
# https://www.youtube.com/watch?v=iCE1bDoit9Q

async def f(thread_nr: int):
    for i in range(100):
        print(f"Thread {thread_nr} : {i}")
    return


if __name__ == "__main__":
    pass
