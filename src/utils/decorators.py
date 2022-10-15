""" Funktioner för decorators """
from time import time


def function_timer(func):
    """ tar tid hur länge det tar att köra viss funktion."""

    # This function shows the execution time of
    # the function object passed
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Function {func.__name__!r}  with arg:{args} and kw:{kwargs}  executed in {(t2 - t1):.4f}s')
        return result

    return wrap_func
